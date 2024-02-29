import csv
from collections import defaultdict

alle_abteilungen = set()
membership_types = set()

abteilungen_membership_count = defaultdict(lambda: defaultdict(int))
abteilungen_fractional_count = defaultdict(lambda: defaultdict(int))

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
        members.append(r)

membership_types = sorted(list(membership_types))
alle_abteilungen = sorted(list(alle_abteilungen))

for member in members:
    for ab in member['Abteilungen List']:
        abteilungen_membership_count[ab]['Alle'] += 1
        abteilungen_fractional_count[ab]['Alle'] += 1.0/len(member['Abteilungen List'])

        abteilungen_membership_count[ab][member['Beitragssätze']] += 1
        abteilungen_fractional_count[ab][member['Beitragssätze']] += 1.0/len(member['Abteilungen List'])


print("\nAbteilung Mitgliederzahl, doppel")
for ab in alle_abteilungen:
    print("{:>20}   gesamt {:>2d}, Halle Fö: {:>2d}, Halle N: {:>2d}, Halle erm.: {:>2d}, Outdoor Norm.: {:>2d}, Outdoor erm.: {:>2d}".format(
        ab,
        abteilungen_membership_count[ab]['Alle'],
        abteilungen_membership_count[ab]['Halle Förderm.'],
        abteilungen_membership_count[ab]['Halle Normaltarif'],
        abteilungen_membership_count[ab]['Halle ermäßigt'],
        abteilungen_membership_count[ab]['Outdoor Normaltarif'],
        abteilungen_membership_count[ab]['Outdoor ermäßigt'],
        ))

print("\nAbteilung Mitgliederzahl, geteilet")
for ab in alle_abteilungen:
    print("{:>20}   gesamt {:>6.1f}, Halle Fö: {:>6.1f}, Halle N: {:>6.1f}, Halle erm.: {:>6.1f}, Outdoor Norm.: {:>6.1f}, Outdoor erm.: {:>6.1f}".format(
        ab,
        abteilungen_fractional_count[ab]['Alle'],
        abteilungen_fractional_count[ab]['Halle Förderm.'],
        abteilungen_fractional_count[ab]['Halle Normaltarif'],
        abteilungen_fractional_count[ab]['Halle ermäßigt'],
        abteilungen_fractional_count[ab]['Outdoor Normaltarif'],
        abteilungen_fractional_count[ab]['Outdoor ermäßigt'],
        ))

membership_beitraege = {'Outdoor ermäßigt': 20.00, 'Halle ermäßigt': 66.00, 'Halle Förderm.': 0.00, 'Outdoor Normaltarif': 36.00, 'Halle Normaltarif': 120.00}
for ab in alle_abteilungen:
    print(f"\n{ab} Abteilung")
    print("{} Mitglieder".format(abteilungen_membership_count[ab]['Alle']))
    for t in membership_types:
        print("  {} {} Mitglieder".format(abteilungen_membership_count[ab][t], t))

    print("\n{:.1f} Mitgliederteil".format(abteilungen_fractional_count[ab]['Alle']))
    gesamt = 0.0
    for t in membership_types:
        einkommen = membership_beitraege[t]*abteilungen_fractional_count[ab][t]
        print("  {0:.1f} {1} Mitgliederteil ( = {2:.2f}€ × {0:.1f} = {3:.2f}€ )".format(abteilungen_fractional_count[ab][t], t, membership_beitraege[t], einkommen ))
        gesamt += einkommen
    print("Gesamt: {:.2f}€ + {:.2f} Halle Förderm.".format(gesamt, abteilungen_fractional_count[ab]['Halle Förderm.']))
