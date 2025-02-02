import requests
import os
import time

# Notion API key et Database ID
NOTION_API_KEY = os.getenv("NOTION_API_KEY")
DATABASE_ID = os.getenv("DATABASE_ID")

# Headers pour l'API Notion
headers = {
    "Authorization": f"Bearer {NOTION_API_KEY}",
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28"
}

# Fonction pour récupérer tous les événements (pages) de la base de données
def get_all_events():
    url = f"https://api.notion.com/v1/databases/{DATABASE_ID}/query"
    events = []
    has_more = True
    next_cursor = None

    while has_more:
        payload = {"page_size": 100}
        if next_cursor:
            payload["start_cursor"] = next_cursor

        response = requests.post(url, headers=headers, json=payload)
        
        if response.status_code == 200:
            data = response.json()
            events.extend(data["results"])
            has_more = data.get("has_more", False)
            next_cursor = data.get("next_cursor")
        else:
            print(f"❌ Erreur lors de la récupération des événements: {response.status_code}")
            print(response.text)  # Afficher le texte brut pour éviter l'erreur JSONDecodeError
            return []

    return events

# Fonction pour supprimer (archiver) un événement
def archive_event(event_id):
    url = f"https://api.notion.com/v1/pages/{event_id}"
    data = {"archived": True}
    
    for attempt in range(3):  # Essayer jusqu'à 3 fois en cas d'erreur
        response = requests.patch(url, headers=headers, json=data)
        
        if response.status_code == 200:
            print(f"✅ Événement {event_id} archivé (supprimé) avec succès.")
            return True
        elif response.status_code in [429, 502]:  # Trop de requêtes ou erreur temporaire
            print(f"⚠️ Erreur {response.status_code} pour {event_id}, nouvelle tentative dans 5s...")
            time.sleep(5)  # Attendre avant de réessayer
        else:
            print(f"❌ Erreur lors de la suppression de {event_id}: {response.status_code}")
            print(response.text)  # Afficher le texte brut pour voir le problème
            return False

# Fonction principale pour supprimer tous les événements
def delete_all_events():
    events = get_all_events()
    if not events:
        print("📭 Aucun événement trouvé dans le calendrier.")
        return

    print(f"📌 {len(events)} événements trouvés. Suppression en cours...")
    
    for event in events:
        archive_event(event["id"])
        time.sleep(1)  # Attendre 1s entre chaque suppression pour éviter d'être bloqué

    print("✅ Tous les événements ont été archivés avec succès.")

