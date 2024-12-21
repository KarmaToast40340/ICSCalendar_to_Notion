import requests
import os

# Notion API key et Database ID
NOTION_API_KEY = "secret_DX8Fdsr7kExKOvOX3VXaBxmjClf4MvbVGXM42oZvTTj"
DATABASE_ID = "43041498339045e6b9c4fdccb6574e5c"

# Headers de l'API Notion
headers = {
    "Authorization": f"Bearer {NOTION_API_KEY}",
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28"
}

# Récupérer toutes les pages de la base de données
def get_all_pages():
    url = f"https://api.notion.com/v1/databases/{DATABASE_ID}/query"
    response = requests.post(url, headers=headers)
    if response.status_code == 200:
        return response.json()["results"]
    else:
        print(f"Erreur lors de la récupération des pages: {response.status_code}")
        print(response.json())
        return []

# Supprimer une page
def delete_page(page_id):
    url = f"https://api.notion.com/v1/blocks/{page_id}"
    response = requests.delete(url, headers=headers)
    if response.status_code == 200:
        print(f"Page {page_id} supprimée avec succès.")
    else:
        print(f"Erreur lors de la suppression de la page {page_id}: {response.status_code}")
        print(response.json())

# Supprimer toutes les pages du calendrier
def delete_all_events():
    pages = get_all_pages()
    for page in pages:
        delete_page(page["id"])

# Exécuter la suppression de tous les événements
delete_all_events()
