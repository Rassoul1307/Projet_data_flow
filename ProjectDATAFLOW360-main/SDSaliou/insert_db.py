import json
import uuid
from cassandra.cluster import Cluster

#connexion à Cassandra
cluster = Cluster(['127.0.0.1'])
session = cluster.connect('meteo_dakar')

#chargement
with open('meteo_dakar_annuelle_by_SDiarra.json', 'r') as f:
    data = json.load(f)

#inserer
for donnee in data :
    session.execute("""
        INSERT INTO meteo_scraper (id, date, temperature_max_celsius, precipitation,vent_kmh,humidite_pourcentage)
        VALUES (%s, %s, %s, %s, %s,%s)    
    """, (
        uuid.uuid4(),
        donnee['date'],
        donnee['température_max_celsius'],
        donnee['précipitations_mm'],
        donnee['vent_kmh'],
        donnee['humidité_pourcentage']
    ))
print("Finish!!!")
    