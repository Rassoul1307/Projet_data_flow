import pandas as pd
from pymongo import MongoClient
from hdfs import InsecureClient
import json

# Connexion à MongoDB
username = "root"
password = "passer123"
mongo_host = "mongo"
mongo_port = 27017
auth_db = "admin"

mongo_uri = f"mongodb://{username}:{password}@{mongo_host}:{mongo_port}/?authSource={auth_db}"
mongo_client = MongoClient(mongo_uri)

# Base de données et collection
db = mongo_client["meteo_base"]
collection = db["meteo_collection"]

# Récupération des données MongoDB
data = list(collection.find())

if data:
    df = pd.DataFrame(data)
    df.drop(columns=["_id"], errors="ignore", inplace=True)

    # 🔁 Convertir le DataFrame en liste de dictionnaires
    json_data = df.to_dict(orient="records")

    # Connexion HDFS
    hdfs_client = InsecureClient("http://hadoop-namenode:9870", user="root")
    print("✅ connexion a hdfs reussi")

    # Chemin HDFS
    hdfs_path = "/data/meteo_json/mes_donnees.json"

    # Écriture dans HDFS
    with hdfs_client.write(hdfs_path, encoding="utf-8", overwrite=True) as writer:
        json.dump(json_data, writer, ensure_ascii=False, indent=2)

    print(f"✅ Fichier JSON écrit avec succès dans HDFS à l’emplacement : {hdfs_path}")
else:
    print("⚠️ Aucune donnée trouvée dans la collection MongoDB.")