import requests
import csv
from datetime import datetime

# CONFIGURATION des paramètres de base
TOMORROW_API_KEY = "UUVeOVnuGpAQJ9HJssbulwnQFHytCjVw"
region = "Dakar"
csv_file = "./data/api/Alla_meteo_dakar.csv"

# FONCTION pour recuperer les coordonnées(latitude, longitude) via le nom de la region
def get_coordinates(region_name):
    try:
        url = f"https://nominatim.openstreetmap.org/search?format=json&q={region_name},Sénégal"
        response = requests.get(url, headers={"User-Agent": "weather-script"})
        data = response.json()
        if data:
            lat = float(data[0]["lat"])
            lon = float(data[0]["lon"])
            return lat, lon
    except Exception as e:
        print(f"[Erreur géocodage] {region_name} ➤ {e}")
    return None, None

# Fonction pour récuperer les données météo entre startTime et endTime
def get_weather_history(lat, lon):
    url = f"https://api.tomorrow.io/v4/timelines?apikey={TOMORROW_API_KEY}"

    # Les parametres de la requete POST
    payload = {
        "location": f"{lat},{lon}",
        "fields": ["temperature", "humidity", "cloudCover", "windSpeed", "rainIntensity"],
        "units": "metric",
        "timesteps": ["5m"],
        "startTime": "2025-07-29T00:00:00Z",
        "endTime": "now"
    }

    # L'entete de la requete POST
    headers = {
        "accept": "application/json",
        "content-type": "application/json"
    }

    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        data = response.json()
        return data["data"]["timelines"][0]["intervals"]
    except Exception as e:
        print(f"[Erreur API météo] ➤ {e}")
        return []

# TRAITEMENT PRINCIPAL
lat, lon = get_coordinates(region)
if lat is not None and lon is not None:
    weather_intervals = get_weather_history(lat, lon)

    if weather_intervals:
        # Construction des enregistrements à écrire
        records = []
        for interval in weather_intervals:
            values = interval["values"]
            raw_time = interval["startTime"]
            # Formatage de la date en jour-mois-année H:m:s
            formatted_time = datetime.fromisoformat(raw_time.replace("Z", "")).strftime("%d-%m-%Y %H:%M:%S")

            record = {
                "region": region,
                "latitude": lat,
                "longitude": lon,
                "datetime": formatted_time,
                "temperature": values.get("temperature"),
                "humidity": values.get("humidity"),
                "cloudCover": values.get("cloudCover"),
                "windSpeed": values.get("windSpeed"),
                "rainIntensity": values.get("rainIntensity")
            }

            records.append(record)

        # Écriture CSV
        write_header = False
        try:
            with open(csv_file, "r", encoding="utf-8") as f:
                if not f.readline():
                    write_header = True
        except FileNotFoundError:
            write_header = True

        with open(csv_file, mode="a", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(file, fieldnames=records[0].keys())
            if write_header:
                writer.writeheader()
            writer.writerows(records)

        print(f"{len(records)} enregistrements météo sauvegardés dans '{csv_file}'")

    else:
        print(f"[Erreur] Aucune donnée météo trouvée pour {region}")
else:
    print(f"[Erreur] Coordonnées introuvables pour {region}")
