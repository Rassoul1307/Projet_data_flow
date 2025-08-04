import openmeteo_requests
import pandas as pd
import requests_cache
import requests
from retry_requests import retry
from datetime import datetime, timedelta


# Client Open-Meteo SANS cache ni retry
session = requests.Session()
openmeteo = openmeteo_requests.Client(session=session)
# Coordonnées de Dakar
latitude = 14.6928
longitude = -17.4467

# Période des 16 derniers jours
end_date = datetime.utcnow().date()
start_date = end_date - timedelta(days=16)

# API historique d'Open-Meteo
url = "https://archive-api.open-meteo.com/v1/archive"
params = {
    "latitude": latitude,
    "longitude": longitude,
    "start_date": start_date.isoformat(),
    "end_date": end_date.isoformat(),
    "hourly": [
        "temperature_2m",
        "relative_humidity_2m",
        "rain",
        "wind_speed_10m",
        "cloud_cover",
        "apparent_temperature"
    ],
    "timezone": "auto"
}

# Appel API
responses = openmeteo.weather_api(url, params=params)
response = responses[0]

# Infos générales
print(f"Données météo pour Dakar ({response.Latitude()}°N, {response.Longitude()}°E)")
print(f"Du {start_date} au {end_date}")

# Données horaires
hourly = response.Hourly()

# Données météo avec libellés français
donnees_horaires = {
    "Date": pd.date_range(
        start=pd.to_datetime(hourly.Time(), unit="s", utc=True),
        end=pd.to_datetime(hourly.TimeEnd(), unit="s", utc=True),
        freq=pd.Timedelta(seconds=hourly.Interval()),
        inclusive="left"
    ),
    "Température (2m)": hourly.Variables(0).ValuesAsNumpy(),
    "Humidité relative (2m)": hourly.Variables(1).ValuesAsNumpy(),
    "Pluie (mm)": hourly.Variables(2).ValuesAsNumpy(),
    "Vitesse du vent (10m)": hourly.Variables(3).ValuesAsNumpy(),
    "Couverture nuageuse (%)": hourly.Variables(4).ValuesAsNumpy(),
    "Température ressentie": hourly.Variables(5).ValuesAsNumpy()
}

# Construction du DataFrame
df = pd.DataFrame(donnees_horaires)

# ✅ Formatage de la date en "jj-mm-aaaa hh:mm:ss"
df["Date"] = df["Date"].dt.strftime("%d-%m-%Y %H:%M:%S")

# Export en JSON avec encodage UTF-8, format lisible
df.to_json("donnees_meteo_dakar.json", orient="records", force_ascii=False, indent=4)

print("\n✅ Fichier JSON créé avec dates formatées : donnees_meteo_dakar.json")