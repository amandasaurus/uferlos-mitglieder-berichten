import csv
from collections import defaultdict

import locale
locale.setlocale(locale.LC_ALL, 'de_DE.utf8')
locale.setlocale(locale.LC_NUMERIC, 'de_DE.utf8')
from locale import format_string as fmt

alle_abteilungen = set()
membership_types = set()

abteilungen_membership_count = defaultdict(lambda: defaultdict(int))
abteilungen_fractional_count = defaultdict(lambda: defaultdict(float))

members = []

with open("mitglieder.csv") as fp:
    rdr = csv.DictReader(fp)
    for r in rdr:
        if r['Ende Mitgliedschaft'] != '':
            continue
        r['Abteilungen List'] = [x.strip() for x in r['Abteilungen'].split(',')]
        alle_abteilungen.update(r['Abteilungen List'])
        membership_types.add(r['Beitragssätze'])
        r['Name'] = r['Vorname'] + ' ' + r['Nachname/Firma']
        r['NachnameVorname'] = r['Nachname/Firma'] + ', ' + r['Vorname']
        r['Abteilungzahl'] = len(r['Abteilungen List'])
        r['Mitgliederteil'] = 1.0/float(len(r['Abteilungen List']))
        members.append(r)

members.sort(key=lambda m: m['NachnameVorname'])

membership_types = sorted(list(membership_types))
alle_abteilungen = sorted(list(alle_abteilungen))

for member in members:
    for ab in member['Abteilungen List']:
        abteilungen_membership_count[ab]['Alle'] += 1
        abteilungen_fractional_count[ab]['Alle'] += 1.0/len(member['Abteilungen List'])

        abteilungen_membership_count[ab][member['Beitragssätze']] += 1
        abteilungen_fractional_count[ab][member['Beitragssätze']] += 1.0/len(member['Abteilungen List'])


with open("bericht-tabellen.txt", 'w') as out:
    out.write("\nAbteilung Mitgliederzahl, doppel\n")
    for ab in alle_abteilungen:
        out.write(locale.format_string("%20s gesamt %2d, Halle Fö: %2d, Halle N: %2d, Halle erm.: %2d, Outdoor Norm.: %2d, Outdoor erm.: %2d\n", (
            ab,
            abteilungen_membership_count[ab]['Alle'],
            abteilungen_membership_count[ab]['Halle Förderm.'],
            abteilungen_membership_count[ab]['Halle Normaltarif'],
            abteilungen_membership_count[ab]['Halle ermäßigt'],
            abteilungen_membership_count[ab]['Outdoor Normaltarif'],
            abteilungen_membership_count[ab]['Outdoor ermäßigt'],
            'd'
            )))

    out.write("\nAbteilung Mitgliederzahl, geteilet\n")
    for ab in alle_abteilungen:
        out.write("{:>20}   gesamt {:>6.1f}, Halle Fö: {:>6.1f}, Halle N: {:>6.1f}, Halle erm.: {:>6.1f}, Outdoor Norm.: {:>6.1f}, Outdoor erm.: {:>6.1f}\n".format(
            ab,
            abteilungen_fractional_count[ab]['Alle'],
            abteilungen_fractional_count[ab]['Halle Förderm.'],
            abteilungen_fractional_count[ab]['Halle Normaltarif'],
            abteilungen_fractional_count[ab]['Halle ermäßigt'],
            abteilungen_fractional_count[ab]['Outdoor Normaltarif'],
            abteilungen_fractional_count[ab]['Outdoor ermäßigt'],
            ))

membership_beitraege = {'Outdoor ermäßigt': 20.00, 'Halle ermäßigt': 66.00, 'Halle Förderm.': 36.00, 'Outdoor Normaltarif': 36.00, 'Halle Normaltarif': 120.00, '(kein Beitrag)': 0.00}
with open("bericht-listen.adoc", 'w') as out:
    out.write("= Uferlos Mitglieder teil\n")

    for ab in alle_abteilungen:
        out.write(f"\n\n== {ab} Abteilung\n")
        out.write(f"=== Mitglieder Zusammenfassung\n")
        out.write("{} Mitglieder\n\n".format(abteilungen_membership_count[ab]['Alle']))
        for t in membership_types:
            out.write(fmt("* %3d %s Mitglieder\n", (abteilungen_membership_count[ab][t], t)))

        out.write(fmt("\n%.2f Mitgliederteil\n\n", abteilungen_fractional_count[ab]['Alle']))
        gesamt = 0.0
        for t in membership_types:
            einkommen = membership_beitraege[t]*abteilungen_fractional_count[ab][t]
            out.write("* {0:>8.2n} {1} Mitgliederteil ( = {2:.2n}€ × {0:.02n} = {3:.2n}€ )\n".format(abteilungen_fractional_count[ab][t], t, membership_beitraege[t], float(einkommen) ))
            gesamt += einkommen
        out.write("\n\nGesamt: {:.2n}€\n".format(gesamt))
        #print("Gesamt: {:.02f}€".format(gesamt))
        #print("Gesamt: %.02f€" % gesamt)
        #print(locale.format_string("Gesamt: %.02f€", gesamt))

        out.write(f"\n=== Mitglieder List\n")
        out.write("\n[cols=\"1,1,1,1,1\"]\n|===\n")
        out.write("|Name |Beitrag |Abteilungzahl |Mitgliederteil |Einkommenteil\n\n")
        mitgliederteil_gesamt = 0.0
        einkommen_gesamt = 0.0
        for m in members:
            if ab not in m['Abteilungen List']:
                continue
            out.write("|{name}\n|{beitrag}\n|{ab_zahl}\n|{mitglt:.>.2n}\n|{eink_zahl:>.2n}€\n".format(
                name=m['NachnameVorname'],
                beitrag="{} ({:.2n}€)".format(m['Beitragssätze'], float(membership_beitraege[m['Beitragssätze']])),
                ab_zahl=m['Abteilungzahl'],
                mitglt=m['Mitgliederteil'],
                eink_zahl=membership_beitraege[m['Beitragssätze']] * m['Mitgliederteil'],
            ))
            mitgliederteil_gesamt += m['Mitgliederteil']
            einkommen_gesamt += membership_beitraege[m['Beitragssätze']] * m['Mitgliederteil']

        out.write("|\n|\n|\n|{:.2n}\n|{:.2n}€\n".format(mitgliederteil_gesamt, einkommen_gesamt))
        out.write("|===\n")



res = defaultdict(int)
for m in members:
    num_abteilungen = len(m['Abteilungen List'])
    res[num_abteilungen] += 1

res = sorted(list(res.items()))
for (num_abteilungen, num_mitglieder) in res:
    print(f"{num_mitglieder:>3d} Mitglied(er) sind in {num_abteilungen:>1} Abteilung(en)")

ueber3s = []
for m in members:
    num_abteilungen = len(m['Abteilungen List'])
    if num_abteilungen > 3:
        ueber3s.append((num_abteilungen, "{:>20s} ist in {:1} Abteilungen: {}".format(m['Name'], num_abteilungen, m['Abteilungen'])))

ueber3s.sort()
print("\n".join(x[1] for x in ueber3s))
