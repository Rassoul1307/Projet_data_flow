import os
import json
from pymongo import MongoClient

# Connexion MongoDB
username = os.getenv('MONGO_USERNAME')
password = os.getenv('MONGO_PASSWORD')
client = MongoClient(f'mongodb://{username}:{password}@mongo:27017/?authSource=admin')
db = client["meteo_base"]
collection = db["meteo_collection"]

# Lecture et filtrage
documents_to_insert = []

with open('./data/generation/rassoul_data_meteo.json', 'r', encoding='utf-8') as file:
    for line in file:
        if line.strip():
            doc = json.loads(line)
            doc['Date'] = doc['Date'].strip()  # Nettoyage
            # Vérifie si un document avec la même Date existe déjà
            if not collection.find_one({'Date': doc['Date']}):
                documents_to_insert.append(doc)

# Insertion
if documents_to_insert:
    collection.insert_many(documents_to_insert)
    print(f"{len(documents_to_insert)} nouveaux documents insérés.")
else:
    print("Aucun nouveau document à insérer.")