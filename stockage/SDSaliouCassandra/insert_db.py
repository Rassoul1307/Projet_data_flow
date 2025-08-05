import json
import time
from cassandra.cluster import Cluster
from cassandra.cluster import NoHostAvailable
from cassandra.query import SimpleStatement

# === Connexion avec retry ===
MAX_RETRIES = 10
WAIT_TIME = 10  # secondes entre les essais

for i in range(MAX_RETRIES):
    try:
        cluster = Cluster(['cassandra'])  # ← ou IP/DNS du service Cassandra
        session = cluster.connect()
        print("✅ Cassandra est prêt ! Connexion établie.")
        break
    except NoHostAvailable as e:
        print(f"⏳ Cassandra non disponible (tentative {i+1}/{MAX_RETRIES})... nouvelle tentative dans {WAIT_TIME}s")
        time.sleep(WAIT_TIME)
else:
    print("❌ Échec de la connexion à Cassandra après plusieurs tentatives.")
    exit(1)

# === Création du keyspace ===
session.execute("""
    CREATE KEYSPACE IF NOT EXISTS meteo_dakar
    WITH replication = {'class':'SimpleStrategy', 'replication_factor': 1}
""")

# === Sélection du keyspace ===
session.set_keyspace('meteo_dakar')

# === Création de la table ===
session.execute("""
    CREATE TABLE IF NOT EXISTS meteo_scraper (
        date TEXT PRIMARY KEY,
        temperature_max_celsius FLOAT,
        precipitation FLOAT,
        vent_kmh FLOAT,
        humidite_pourcentage FLOAT
    )
""")

# === Chargement du fichier JSON ===
with open('meteo_dakar_annuelle_by_SDiarra.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# === Insertion des données ===
for donnee in data:
    session.execute("""
        INSERT INTO meteo_scraper (date, temperature_max_celsius, precipitation, vent_kmh, humidite_pourcentage)
        VALUES (%s, %s, %s, %s, %s)
    """, (
        donnee['date'],
        donnee['température_max_celsius'],
        donnee['précipitations_mm'],
        donnee['vent_kmh'],
        donnee['humidité_pourcentage']
    ))

print("✅ Insertion terminée avec succès !")