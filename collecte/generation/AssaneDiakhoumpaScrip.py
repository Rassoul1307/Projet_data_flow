import pandas as pd
import random
from datetime import datetime, timedelta

# Coordonnées et région
region = "Dakar"
latitude = 14.693425
longitude = -17.447938

# Fonction de génération
def generer_donnees_meteo_csv(n=1000, fichier="PROJET_DATA_FLOW_360/data/generation/meteo_dakar_1000.csv"):
    donnees = []
    maintenant = datetime.now()

    for i in range(n):
        date_heure = maintenant - timedelta(minutes=i * 15)
        donnees.append({
            "Date_time": date_heure.strftime("%d/%m/%Y %H:%M:%S"),
            "Region": region,
            "Latitude": latitude,
            "Longitude": longitude,
            "Temperature": round(random.uniform(24.0, 36.0), 1),
            "Humidite": random.randint(40, 95),
            "Couverture_des_nuage": random.randint(10, 100),
            "Intensite_pluies": round(random.uniform(0.0, 5.0), 2),
            "Vitesse_vents": round(random.uniform(5.0, 25.0), 1)
        })

    df = pd.DataFrame(donnees)
    df.to_csv(fichier, index=False)
    print(f" Fichier CSV généré avec succès : {fichier}")

# Exécution
generer_donnees_meteo_csv()