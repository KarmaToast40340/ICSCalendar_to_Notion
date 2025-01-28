import requests
import csv
import icalendar
import os
import suppr
from dotenv import load_dotenv

load_dotenv()

suppr.delete_all_events()

# URL du fichier ICS
ics_url = "https://planning.univ-rennes1.fr/jsp/custom/modules/plannings/v3V5ldWb.shu"

# Télécharger le fichier ICS depuis l'URL
response = requests.get(ics_url)
if response.status_code != 200:
    raise Exception(f"Échec du téléchargement du fichier ICS depuis {ics_url}. Code: {response.status_code}")

# Charger le contenu ICS dans un objet Calendar
calendar = icalendar.Calendar.from_ical(response.content)

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

print("Fichier CSV généré avec succès.")

# Notion API key et Database ID
NOTION_API_KEY = os.getenv("NOTION_API_KEY")
DATABASE_ID = os.getenv("DATABASE_ID")

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
        # Créer le titre avec la localisation
        summary_with_location = f"{row['SUMMARY']} - {row['LOCATION']}"

        # Préparer les données pour chaque événement
        data = {
            "parent": {
                "database_id": DATABASE_ID
            },
            "properties": {
                "Nom": {  # Correspond à la colonne SUMMARY
                    "title": [{
                        "text": {
                            "content": summary_with_location  # Utiliser le titre avec la localisation
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
            print(f"Événement {summary_with_location} ajouté à Notion avec succès.")
        else:
            print(f"Erreur pour {summary_with_location}: {response.status_code}")
            print("Détails:", response.json())



print("Téléversement terminé.")


# Supprimer le fichier CSV après utilisation
if os.path.exists(csv_file):
    os.remove(csv_file)
    print(f"Fichier {csv_file} supprimé avec succès.")