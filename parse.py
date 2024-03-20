import csv
from collections import defaultdict

import locale
locale.setlocale(locale.LC_ALL, 'de_DE.utf8')
locale.setlocale(locale.LC_NUMERIC, 'de_DE.utf8')
from locale import format_string as fmt

alle_abteilungen = set()
membership_types = set()

abteilungen = {}
#abteilungen_membership_count = defaultdict(lambda: defaultdict(int))
#abteilungen_fractional_count = defaultdict(lambda: defaultdict(float))


membership_beitraege = {
    'Outdoor ermäßigt': 20.00,
    'Halle ermäßigt': 66.00,
    'Halle Förderm.': 36.00,
    'Outdoor Normaltarif': 36.00,
    'Halle Normaltarif': 120.00,
    '(kein Beitrag)': 0.00
}

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
abteilungen = { name:
        {'Name': name,
        'Mitglieder Zahl': 0, 'Mitgliederteil': 0.0, 'Einkommen': 0.00,
        'Beitrag': {
            t: {'Mitglieder Zahl': 0, 'Mitgliederteil': 0.0, 'Einkommen': 0.00}
            for t in membership_beitraege
        }
    }
    for name in alle_abteilungen}

for member in members:
    for ab in member['Abteilungen List']:
        einkommen = float(membership_beitraege[member['Beitragssätze']])/float(member['Abteilungzahl'])

        abteilungen[ab]['Mitglieder Zahl'] += 1
        abteilungen[ab]['Mitgliederteil'] += 1.0/float(member['Abteilungzahl'])
        abteilungen[ab]['Einkommen'] += einkommen

        abteilungen[ab]['Beitrag'][member['Beitragssätze']]['Mitglieder Zahl'] += 1
        abteilungen[ab]['Beitrag'][member['Beitragssätze']]['Mitgliederteil'] += 1.0/float(member['Abteilungzahl'])
        abteilungen[ab]['Beitrag'][member['Beitragssätze']]['Einkommen'] += einkommen

with open("bericht-listen.adoc", 'w') as out:
    out.write("= Uferlos Mitglieder teil\n")
    out.write(":table-caption!:\n")
    out.write("\n\nQuelle-Code: https://github.com/amandasaurus/uferlos-mitglieder-berichten\n")

    out.write(f"\n\n== Zusammenfassung\n")
    for (abt_name, ab) in abteilungen.items():
        out.write("\n\n=== {}\n".format(abt_name))
        zusammenfassung = []
        for t in membership_types:
            bt = ab['Beitrag'][t]
            if bt['Mitglieder Zahl'] > 0:
                zusammenfassung.append("{} × {}".format(bt['Mitglieder Zahl'], t))
        out.write(", ".join(zusammenfassung))

        out.write("\n[cols=\">1,>1,>1,>1\",options=unbreakable]\n[%autowidth]\n|===\n".format(abt_name=abt_name))
        out.write("|Beitrag Name |Zahl |Beitrag Kost| Gesamt Einkommen\n\n")
        for t in membership_types:
            bt = ab['Beitrag'][t]
            out.write(locale.format_string(
                "|%s\n|%.5f\n|%3d€\n|%.2f€\n",
                (t, bt['Mitgliederteil'], membership_beitraege[t], bt['Einkommen']),
                grouping=True
                ))
        out.write(locale.format_string("|*Gesamt*\n|*%.2f*\n|\n|*%.2f€*\n|===\n", (ab['Mitgliederteil'], ab['Einkommen']), grouping=True))


    for (abt_name, ab) in abteilungen.items():
        out.write(f"\n<<<\n== {abt_name} Abteilung\n")
        out.write("\n[cols=\">1,1\"]\n.Wer hat gekreuzt?\n[%autowidth]\n|===\n")
        out.write("|Zahl (Alle) |Beitrag\n\n")
        for t in membership_types:
            bt = ab['Beitrag'][t]
            out.write(fmt("|%3d\n|%s\n", (bt['Mitglieder Zahl'], t)))
        out.write("|*{}*\n|*Gesamt gekreuzt*\n|===\n".format(ab['Mitglieder Zahl']))

        out.write("\n[cols=\">1,>1,>1,>1\"]\n.Geteilte Mitglieder\n[%autowidth]\n|===\n")
        out.write("|Beitrag Name |Zahl |Beitrag Kost| Gesamt Einkommen\n\n")
        for t in membership_types:
            bt = ab['Beitrag'][t]
            out.write(locale.format_string(
                "|%s\n|%.5f\n|%3d€\n|%.2f€\n",
                (t, bt['Mitgliederteil'], membership_beitraege[t], bt['Einkommen']),
                grouping=True
                ))
        out.write(locale.format_string("|*Gesamt*\n|*%.2f*\n|\n|*%.2f€*\n|===\n", (ab['Mitgliederteil'], ab['Einkommen']), grouping=True))

        out.write(f"\n=== Mitglieder List\n")
        out.write("\n[cols=\"1,1,1,1,>1\"]\n|===\n")
        out.write("|Name |Beitrag |Abt.-zahl |Mgl.-teil |Einkommenteil\n\n")

        for m in members:
            if abt_name not in m['Abteilungen List']:
                continue
            out.write(locale.format_string("|%s\n|%s\n|%d\n|%.5f\n|%.2f€\n", (
                m['NachnameVorname'],
                "{} ({:d}€)".format(m['Beitragssätze'], int(membership_beitraege[m['Beitragssätze']])),
                m['Abteilungzahl'],
                m['Mitgliederteil'],
                membership_beitraege[m['Beitragssätze']] * m['Mitgliederteil'],
            )))

        out.write(locale.format_string("|*Gesamt*\n|\n|\n|*%.2f*\n|*%.2f€*\n", (ab['Mitgliederteil'], ab['Einkommen']), grouping=True))
        out.write("|===\n")

print("bericht-listen.adoc geschreiben")
#
#res = defaultdict(int)
#for m in members:
#    num_abteilungen = len(m['Abteilungen List'])
#    res[num_abteilungen] += 1
#
#res = sorted(list(res.items()))
#for (num_abteilungen, num_mitglieder) in res:
#    print(f"{num_mitglieder:>3d} Mitglied(er) sind in {num_abteilungen:>1} Abteilung(en)")
#
#ueber3s = []
#for m in members:
#    num_abteilungen = len(m['Abteilungen List'])
#    if num_abteilungen > 3:
#        ueber3s.append((num_abteilungen, "{:>20s} ist in {:1} Abteilungen: {}".format(m['Name'], num_abteilungen, m['Abteilungen'])))
#
#ueber3s.sort()
#print("\n".join(x[1] for x in ueber3s))
