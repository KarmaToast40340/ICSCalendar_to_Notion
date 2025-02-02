import requests
import csv
import icalendar
import os
import time
import suppr

# Supprimer tous les anciens événements avant d'ajouter les nouveaux
suppr.delete_all_events()

# URL du fichier ICS
ics_url = "https://planning.univ-rennes1.fr/jsp/custom/modules/plannings/v3V5ldWb.shu"

# Télécharger le fichier ICS depuis l'URL
response = requests.get(ics_url)
if response.status_code != 200:
    raise Exception(f"❌ Échec du téléchargement du fichier ICS depuis {ics_url}. Code: {response.status_code}")

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
csv_file = 'notion_calendar.csv'
with open(csv_file, 'w', newline='', encoding='utf-8') as csvfile:
    fieldnames = ['DTSTART', 'DTEND', 'SUMMARY', 'LOCATION', 'DESCRIPTION']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

    writer.writeheader()
    for event in events:
        writer.writerow(event)

print("✅ Fichier CSV généré avec succès.")

# Notion API key et Database ID
NOTION_API_KEY = os.getenv("NOTION_API_KEY")
DATABASE_ID = os.getenv("DATABASE_ID")

# Headers de l'API Notion
headers = {
    "Authorization": f"Bearer {NOTION_API_KEY}",
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28"
}

# Fonction pour ajouter un événement à Notion avec gestion des erreurs
def add_event_to_notion(event_data, summary_with_location):
    """Envoie une requête POST à Notion pour créer un événement avec gestion des erreurs."""
    url = 'https://api.notion.com/v1/pages'

    for attempt in range(3):  # Essayer jusqu'à 3 fois en cas d'erreur
        response = requests.post(url, headers=headers, json=event_data)

        if response.status_code == 200:
            print(f"✅ Événement ajouté : {summary_with_location}")
            return True
        elif response.status_code in [429, 502]:  # Trop de requêtes ou erreur temporaire
            print(f"⚠️ Erreur {response.status_code} pour {summary_with_location}, nouvelle tentative dans 5s...")
            time.sleep(5)  # Attendre avant de réessayer
        else:
            print(f"❌ Erreur pour {summary_with_location}: {response.status_code}")
            print("Détails:", response.text)  # Afficher le texte brut pour voir l'erreur
            return False

# Lire le fichier CSV et envoyer les données à Notion
with open(csv_file, mode='r', newline='', encoding='utf-8') as file:
    reader = csv.DictReader(file)

    for row in reader:
        summary_with_location = f"{row['SUMMARY']} - {row['LOCATION']}"

        # Préparer les données pour l'événement
        event_data = {
            "parent": {"database_id": DATABASE_ID},
            "properties": {
                "Nom": {"title": [{"text": {"content": summary_with_location}}]},
                "Date": {"date": {"start": row['DTSTART'], "end": row['DTEND']}},
                "Location": {"rich_text": [{"text": {"content": row['LOCATION']}}]},
                "Description": {"rich_text": [{"text": {"content": row['DESCRIPTION']}}]}
            }
        }

        add_event_to_notion(event_data, summary_with_location)
        time.sleep(1)  # Attendre 1s entre chaque requête pour éviter d'être bloqué

print("✅ Téléversement terminé.")

# Supprimer le fichier CSV après utilisation
if os.path.exists(csv_file):
    os.remove(csv_file)
    print(f"🗑️ Fichier {csv_file} supprimé avec succès.")
