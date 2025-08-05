import json
import uuid
from cassandra.cluster import Cluster
from cassandra.query import SimpleStatement

#connexion à Cassandra
cluster = Cluster(['cassandra'])
session = cluster.connect()

#Créer le keyspace
session.execute("""
    CREATE KEYSPACE IF NOT EXISTS meteo_dakar
    WITH replication = {'class':'SimpleStrategy', 'replication_factor': 1}
""")

#connexion
session.set_keyspace('meteo_dakar')

#Créer la table 
session.execute("""
    CREATE TABLE IF NOT EXISTS meteo_scraper (
        date TEXT PRIMARY KEY,
        temperature_max_celsius FLOAT,
        precipitation FLOAT,
        vent_kmh FLOAT,
        humidite_pourcentage FLOAT
    )
""")

#chargement
with open('meteo_dakar_annuelle_by_SDiarra.json', 'r') as f:
    data = json.load(f)

#inserer
for donnee in data :
    session.execute("""
        INSERT INTO meteo_scraper (date, temperature_max_celsius, precipitation,vent_kmh,humidite_pourcentage)
        VALUES (%s, %s, %s, %s,%s)    
    """, (
        donnee['date'],
        donnee['température_max_celsius'],
        donnee['précipitations_mm'],
        donnee['vent_kmh'],
        donnee['humidité_pourcentage']
    ))
print("Finish!!!")
    