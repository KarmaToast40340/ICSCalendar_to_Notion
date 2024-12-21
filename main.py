import requests
import csv
import icalendar
import suppr
import os

suppr.delete_all_events()

# Détermine le répertoire où se trouve le script
script_dir = os.path.dirname(os.path.abspath(__file__))

# Construire le chemin complet vers le fichier ICS
ics_file_path = os.path.join(script_dir, "ADECal.ics")

# Charger le fichier ICS
if not os.path.exists(ics_file_path):
    raise FileNotFoundError(f"Le fichier {ics_file_path} est introuvable.")

with open(ics_file_path, 'rb') as f:
    calendar = icalendar.Calendar.from_ical(f.read())
# Liste des événements
events = []

# Extraire les données du fichier ICS
for component in calendar.walk():
    if component.name == "VEVENT":
        event = {
            "DTSTART": component.get('DTSTART').dt,
            "DTEND": component.get('DTEND').dt,
            "SUMMARY": component.get('SUMMARY'),
            "LOCATION": component.get('LOCATION'),
            "DESCRIPTION": component.get('DESCRIPTION')
        }
        events.append(event)

# Sauvegarder dans un fichier CSV compatible avec Notion
with open('notion_calendar.csv', 'w', newline='', encoding='utf-8') as csvfile:
    fieldnames = ['DTSTART', 'DTEND', 'SUMMARY', 'LOCATION', 'DESCRIPTION']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

    writer.writeheader()
    for event in events:
        writer.writerow(event)

print("Conversion ICS vers CSV terminée.")

# Notion API key et Database ID
NOTION_API_KEY = "secret_DX8Fdsr7kExKOvOX3VXaBxmjClf4MvbVGXM42oZvTTj"
DATABASE_ID = "43041498339045e6b9c4fdccb6574e5c"

# Headers de l'API Notion
headers = {
    "Authorization": f"Bearer {NOTION_API_KEY}",
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28"
}

# Chemin vers le fichier CSV
csv_file = 'notion_calendar.csv'

# Lire le fichier CSV
with open(csv_file, mode='r', newline='', encoding='utf-8') as file:
    reader = csv.DictReader(file)

    # Parcourir chaque ligne (chaque événement)
    for row in reader:
        # Vérifier si la description contient "CPTD2TP3"
        description=row['DESCRIPTION']
        if 'FISE1' in description or 'INFO1 TD2TP3' in description:
            # Préparer les données pour chaque événement
            data = {
                "parent": {
                    "database_id": DATABASE_ID
                },
                "properties": {
                    "Nom": {  # Correspond à la colonne SUMMARY
                        "title": [{
                            "text": {
                                "content": row['SUMMARY']  # Utiliser la colonne "SUMMARY"
                            }
                        }]
                    },
                    "Date": {  # Correspond aux colonnes DTSTART et DTEND
                        "date": {
                            "start": row['DTSTART'],  # Colonne "DTSTART" du CSV
                            "end": row['DTEND']  # Colonne "DTEND" du CSV
                        }
                    },
                    "Location": {  # Correspond à la colonne LOCATION
                        "rich_text": [{
                            "text": {
                                "content": row['LOCATION']  # Colonne "LOCATION"
                            }
                        }]
                    },
                    "Description": {  # Correspond à la colonne DESCRIPTION
                        "rich_text": [{
                            "text": {
                                "content": row['DESCRIPTION']  # Colonne "DESCRIPTION"
                            }
                        }]
                    }
                }
            }

            # Envoyer la requête POST à Notion
            response = requests.post('https://api.notion.com/v1/pages',
                                     headers=headers,
                                     json=data)

            # Vérifier la réponse de l'API
            if response.status_code == 200:
                print(f"Événement {row['SUMMARY']} ajouté à Notion avec succès.")
            else:
                print(f"Erreur pour {row['SUMMARY']}: {response.status_code}")
                print("Détails:", response.json())

print("téléversement terminé")
