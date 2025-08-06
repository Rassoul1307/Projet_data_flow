import pandas as pd
from sqlalchemy import create_engine, MetaData, Table, Column, String, DateTime, Numeric, insert
import os


# Connexion PostgreSQL via variable d'environnement
db_url = os.environ.get("DATABASE_URL")
engine = create_engine(db_url)
metadata = MetaData()
# Définition de la table (doit correspondre aux colonnes du CSV)
metheo_dakar = Table(
    'metheo_dakar', metadata,
    Column('Date_time', DateTime),
    Column('Region', String(25)),
    Column('Latitude', Numeric),
    Column('Longitude', Numeric),
    Column('Temperature', Numeric),
    Column('Humidite', Numeric),
    Column('Couverture_des_nuage', Numeric),
    Column('Intensite_pluies', Numeric),
    Column('Vitesse_vents', Numeric)
)

# Étape 1 : Création de la table dans la base si elle n'existe pas
metadata.create_all(engine)

print("DATABASE_URL =", db_url)

# Étape 2 : Lecture du CSV avec conversion automatique de Date_time en datetime
df = pd.read_csv("meteo_dakar_1000.csv", parse_dates=["Date_time"])

# Étape 3 : Conversion du DataFrame en liste de dictionnaires
donnees = df.to_dict(orient="records")

# Étape 4 : Insertion des données
with engine.connect() as conn:
    existants = pd.read_sql('SELECT "Date_time", "Region" FROM metheo_dakar', conn)

# Suppression des doublons dans le DataFrame
df_new = df.merge(existants, on=["Date_time", "Region"], how="left", indicator=True)
df_new = df_new[df_new["_merge"] == "left_only"].drop(columns=["_merge"])

# Insertion
donnees = df_new.to_dict(orient="records")
with engine.connect() as conn:
    conn.execute(insert(metheo_dakar), donnees)
    conn.commit()
