import csv
from collections import defaultdict

import sys, copy
import locale
locale.setlocale(locale.LC_ALL, 'de_DE.utf8')
locale.setlocale(locale.LC_NUMERIC, 'de_DE.utf8')
from locale import format_string as fmt

alle_abteilungen = set()
mitglieder_arten = set()

halle_abteilungen = { 'Badminton', 'Federboa', 'Fußball', 'Schwimmen',
        'Tischtennis', 'Volleyball Frauen', 'Volleyball Männer', 'Yoga' }

outdoor_abteilungen = { 'Boule', 'Kegeln', 'Laufen', 'Motorrad',
        'Nordic-Walking', 'Radsport', 'Ski', 'Wandern', 'Seniorensport',
        '(Keine Abteilung zugeordnet)'
        }


abteilungen = {}

mitglieder_beitraege = {
    'Halle Normaltarif': 120.00,
    'Outdoor Normaltarif': 36.00,

    'Halle ermäßigt': 66.00,
    'Outdoor ermäßigt': 20.00,

    'Halle Förderm.': 36.00,
    'Outdoor Förderm.': 36.00,

    '(kein Beitrag)': 0.00
}

probleme = []
mitglieder = []

mitgleider_hallen_outdoor_zahl = defaultdict(int)

anzahl_hallen_max = 0
anzahl_outdoor_max = 0

input_file = sys.argv[1]

with open(input_file) as fp:
    rdr = csv.DictReader(fp)
    for r in rdr:
        if r['Ende Mitgliedschaft'] != '':
            continue
        r['Abteilungen List'] = [x.strip() for x in r['Abteilungen'].split(',')]
        r['Anzahl Hallen'] = sum(1 for abt in r['Abteilungen List'] if abt in halle_abteilungen)
        r['Anzahl Outdoor'] = sum(1 for abt in r['Abteilungen List'] if abt in outdoor_abteilungen)
        mitgleider_hallen_outdoor_zahl[(r['Anzahl Hallen'], r['Anzahl Outdoor'])] += 1
        r['Anzahl Abteilungen'] = len(r['Abteilungen List'])
        anzahl_hallen_max = max(anzahl_hallen_max, r['Anzahl Hallen'])
        anzahl_outdoor_max = max(anzahl_outdoor_max, r['Anzahl Outdoor'])
        alle_abteilungen.update(r['Abteilungen List'])
        mitglieder_arten.add(r['Beitragssätze'])
        r['Name'] = r['Vorname'] + ' ' + r['Nachname/Firma']
        r['NachnameVorname'] = r['Nachname/Firma'] + ', ' + r['Vorname']
        r['Abteilungzahl'] = len(r['Abteilungen List'])
        r['Mitgliederteil'] = 1.0/float(len(r['Abteilungen List']))
        mitglieder.append(r)

mitglieder.sort(key=lambda m: m['NachnameVorname'])

mitglieder_arten = sorted(list(mitglieder_arten))
alle_abteilungen = sorted(list(alle_abteilungen))
abteilungen = { name:
        {'Name': name,
        'Art': ('Halle' if name in halle_abteilungen else 'Outdoor'),
        'Mitglieder Angekreuzt': 0, 'Mitgliederteil': 0.0, 'Einkommen': 0.00,
        'Mitglieder': [],
        }
    for name in alle_abteilungen}

einkommen_pro_abt = {
    'Halle Normaltarif': {},
    'Outdoor Normaltarif': {},

    'Halle ermäßigt': {},
    'Outdoor ermäßigt': {},

    'Halle Förderm.': {},
    'Outdoor Förderm.': {},
}

for anzahl_halle in range(0, 10):
    for anzahl_outdoor in range(0, 10):
        einkommen_halle_pro = 0
        einkommen_outdoor_pro = 0
        if anzahl_halle+anzahl_outdoor == 0:
            continue

        # Normaltarif
        if anzahl_outdoor > 0:
            einkommen_outdoor_pro = (36.00 / (anzahl_halle+anzahl_outdoor))
        else:
            einkommen_outdoor_pro = 0.00
        einkommen_outdoor_gesamt = einkommen_outdoor_pro * anzahl_outdoor
        if anzahl_halle > 0:
            einkommen_halle_gesamt = 120.00 - einkommen_outdoor_gesamt
            einkommen_halle_pro = einkommen_halle_gesamt / anzahl_halle
        einkommen_pro_abt['Halle Normaltarif'][(anzahl_halle, anzahl_outdoor)] = (einkommen_halle_pro, einkommen_outdoor_pro)
        einkommen_pro_abt['Outdoor Normaltarif'][(anzahl_halle, anzahl_outdoor)] = (0.00, einkommen_outdoor_pro)

        # ermäßigt
        if anzahl_outdoor > 0:
            einkommen_outdoor_pro = (20.00 / (anzahl_halle+anzahl_outdoor))
        else:
            einkommen_outdoor_pro = 0.00
        einkommen_outdoor_gesamt = einkommen_outdoor_pro * anzahl_outdoor
        if anzahl_halle > 0:
            einkommen_halle_gesamt = 66.00 - einkommen_outdoor_gesamt
            einkommen_halle_pro = einkommen_halle_gesamt / anzahl_halle
        einkommen_pro_abt['Halle ermäßigt'][(anzahl_halle, anzahl_outdoor)] = (einkommen_halle_pro, einkommen_outdoor_pro)
        einkommen_pro_abt['Outdoor ermäßigt'][(anzahl_halle, anzahl_outdoor)] = (0.00, einkommen_outdoor_pro)

        # Förderm
        if anzahl_outdoor > 0:
            einkommen_outdoor_pro = (36.00 / (anzahl_halle+anzahl_outdoor))
        else:
            einkommen_outdoor_pro = 0.00
        einkommen_outdoor_gesamt = einkommen_outdoor_pro * anzahl_outdoor
        if anzahl_halle > 0:
            einkommen_halle_gesamt = 36.00 - einkommen_outdoor_gesamt
            einkommen_halle_pro = einkommen_halle_gesamt / anzahl_halle
        einkommen_pro_abt['Halle Förderm.'][(anzahl_halle, anzahl_outdoor)] = (einkommen_halle_pro, einkommen_outdoor_pro)
        einkommen_pro_abt['Outdoor Förderm.'][(anzahl_halle, anzahl_outdoor)] = (0.00, einkommen_outdoor_pro)

for mitglied in mitglieder:
    if mitglied['Beitragssätze'] not in einkommen_pro_abt:
        probleme.append(("Mitglied \"{}\" hat unbekannter Beitrag: \"{}\"".format(mitglied['Name'], mitglied['Beitragssätze'])))
        continue
    anzahl_halle_outdoor = (mitglied['Anzahl Hallen'], mitglied['Anzahl Outdoor'])
    mitglieder_einkommen_pro_abt = einkommen_pro_abt[mitglied['Beitragssätze']][anzahl_halle_outdoor]

    for abteilung_name in mitglied['Abteilungen List']:
        abteilung = abteilungen[abteilung_name]
        abteilung['Mitglieder Angekreuzt'] += 1
        abteilung['Mitgliederteil'] += (1.0/len(mitglied['Abteilungen List']))
        if abteilung['Name'] in halle_abteilungen:
            abteilung['Einkommen'] += mitglieder_einkommen_pro_abt[0]
            abteilung['Mitglieder'].append((mitglied, mitglied['Beitragssätze'], anzahl_halle_outdoor, mitglieder_einkommen_pro_abt[0]))
        elif abteilung['Name'] in outdoor_abteilungen:
            abteilung['Einkommen'] += mitglieder_einkommen_pro_abt[1]
            abteilung['Mitglieder'].append((mitglied, mitglied['Beitragssätze'], anzahl_halle_outdoor, mitglieder_einkommen_pro_abt[1]))
        else:
            assert False, abteilung


mitglieder_pro_beitrage = defaultdict(int)
for mitglied in mitglieder:
    mitglieder_pro_beitrage[mitglied['Beitragssätze']] += 1


with open("bericht-listen.adoc", 'w') as out:
    out.write("= Uferlos Mitglieder teil\n")
    out.write(":table-caption!:\n")

    out.write("\n\nQuelle-Code: https://github.com/amandasaurus/uferlos-mitglieder-berichten\n")
    out.write("\nDatei: "+input_file)
    out.write("\n\nHalle Abteilungen: {}\n\n".format(", ".join(sorted(halle_abteilungen))))
    out.write("\nOutdoor Abteilungen: {}\n\n".format(", ".join(sorted(outdoor_abteilungen))))

    out.write(f"\n\n== Probleme\n")
    for p in probleme:
        out.write(fmt("\n* %s", p))

    out.write(f"\n\n<<<\n== Method\n")

    out.write("\n=== Nur Hallen")
    out.write("\n[cols=\">1,>1,>1,>1\"]\n[%autowidth]\n|===")
    out.write("\n|Anz. Halle|Halle Normaltarif|Halle ermäßigt|Halle Förderm.")
    for anz_halle in range(1, anzahl_hallen_max+1):
        out.write(fmt("\n|%d", anz_halle))
        out.write(fmt("\n|%.2f €", einkommen_pro_abt["Halle Normaltarif"][(anz_halle, 0)][0]))
        out.write(fmt("\n|%.2f €", einkommen_pro_abt["Halle ermäßigt"][(anz_halle, 0)][0]))
        out.write(fmt("\n|%.2f €", einkommen_pro_abt["Halle Förderm."][(anz_halle, 0)][0]))
    out.write("\n|===")

    out.write("\n=== Nur Outdoor")
    out.write("\n[cols=\">1,>1,>1,>1\"]\n[%autowidth]\n|===")
    out.write("\n|Anz. Outdoor|Outdoor Normaltarif|Outdoor ermäßigt|Outdoor Förderm.")
    for anz_outdoor in range(1, anzahl_outdoor_max+1):
        out.write(fmt("\n|%d", anz_outdoor))
        out.write(fmt("\n|%.2f €", einkommen_pro_abt["Outdoor Normaltarif"][(0, anz_outdoor)][1]))
        out.write(fmt("\n|%.2f €", einkommen_pro_abt["Outdoor ermäßigt"][(0, anz_outdoor)][1]))
        out.write(fmt("\n|%.2f €", einkommen_pro_abt["Outdoor Förderm."][(0, anz_outdoor)][1]))
    out.write("\n|===")

    out.write("\n\n=== Hallen und Outdoor")

    for beitraege in ['Halle Normaltarif', 'Halle ermäßigt', 'Halle Förderm.']:
        out.write(fmt("\n\n==== %s", beitraege))
        cols = ",".join([">1" for _ in range(0, anzahl_outdoor_max+1)])
        out.write("\n[cols=\">1,"+cols+"\"]\n[%autowidth]\n|===")
        out.write("\n|_|"+("|".join([fmt("%d O", anz_outdoor) for anz_outdoor in range(0, anzahl_outdoor_max+1)])))
        for anz_halle in range(1, anzahl_hallen_max+1):
            out.write(fmt("\n|%d H", anz_halle))
            for anz_outdoor in range(0, anzahl_outdoor_max+1):
                out.write(fmt("\n|H:%.2f O:%.2f", einkommen_pro_abt[beitraege][(anz_halle, anz_outdoor)]))

        out.write("\n|===")

    out.write(f"\n<<<\n== Zusammenfassung\n")

    totalbeitragsum = 0
    out.write(f"\n\n=== Mitgleider pro Beitragssätze\n")
    out.write("\n[cols=\">1,>1,>1\"]\n[%autowidth]\n|===")
    out.write("\n|Beitrag|Anzahl Mitgl.|Total\n")
    for beitrage in [ 'Halle Normaltarif', 'Outdoor Normaltarif', 'Halle ermäßigt', 'Outdoor ermäßigt', 'Halle Förderm.', 'Outdoor Förderm.']:
        beitragsum = mitglieder_pro_beitrage[beitrage] * mitglieder_beitraege[beitrage]
        totalbeitragsum += beitragsum
        out.write(fmt("\n|%s\n|%d|%d\n", (beitrage, mitglieder_pro_beitrage[beitrage], beitragsum)))
    out.write("\n|===")
    out.write(fmt("\n\nTotal Beitrag: %.2f €", totalbeitragsum))
    out.write("\n\n")


    totalEinkommen = 0
    for (abt_name, abt) in abteilungen.items():
        out.write("\n".format(abt_name))
        out.write("\n[cols=\">1,>1\"]\n[%autowidth]\n|===")
        out.write(fmt("\n|Name|%s", abt_name))
        out.write(fmt("\n|Angekreuzt|%d", abt['Mitglieder Angekreuzt']))
        out.write(fmt("\n|Mitgliederteil|%.3f", abt['Mitgliederteil']))
        out.write(fmt("\n|Einkommen|%.2f €", abt['Einkommen']))
        totalEinkommen += abt['Einkommen']
        out.write("\n|===\n ")
    out.write(fmt("\n\nTotal Einkommen (sollte gliech mit Total Beitrag sein): %.2f €", totalEinkommen))
    out.write("\n\n")

    for (abt_name, abt) in abteilungen.items():
        out.write(f"\n<<<\n== {abt_name} Abteilung\n")
        out.write("\n[cols=\">1,>1\"]\n[%autowidth]\n|===")
        out.write(fmt("\n|Angekreuzt|%d", abt['Mitglieder Angekreuzt']))
        out.write(fmt("\n|Mitgliederteil|%.3f", abt['Mitgliederteil']))
        out.write(fmt("\n|Einkommen|%.2f €", abt['Einkommen']))
        out.write("\n|===\n ")

        out.write("\n[cols=\"1,1,>1,>1,>1\"]\n[%autowidth]\n|===")
        out.write("\n|Name|Beitragssätze|Anz. H.|Anz. O.|Diese Abt.\n")
        for mitglied in abt['Mitglieder']:
            out.write(fmt("\n|%s", mitglied[0]['Name']))
            out.write(fmt("\n|%s (%.0f €)", (mitglied[0]['Beitragssätze'], mitglieder_beitraege[mitglied[0]['Beitragssätze']])))
            out.write(fmt("\n|%d", mitglied[2][0]))
            out.write(fmt("\n|%d", mitglied[2][1]))
            out.write(fmt("\n|%.2f €", mitglied[3]))
        out.write("\n|===\n ")


print("bericht-listen.adoc geschreiben")
