import requests
import json
from datetime import datetime

# 
TOMORROW_API_KEY = "OC9yH405dZFT1BOO6w6nPgDanrhpPwV8"

# les Coordonnées (latitude et longitude ) de Dakar
lat, lon = 14.693425, -17.447938
location = f"{lat},{lon}"

# 
url = f"https://api.tomorrow.io/v4/timelines?apikey={TOMORROW_API_KEY}"

payload = {
    "location": location,
    "fields": ["temperature", "humidity","cloudCover","windSpeed","rainIntensity"],
    "units": "metric",
    "timesteps": ["30m"],
    "startTime": "2025-07-29T00:00:00Z",
    "endTime": "now"
}

headers = {
    "accept": "application/json",
    "content-type": "application/json"
}

# Requête API
try:
    response = requests.post(url, json=payload, headers=headers)
    data = response.json()
    
    intervals = data.get("data", {}).get("timelines", [])[0].get("intervals", [])
    results = []

    for item in intervals:
        weather_info = {
            "region": "Dakar",
            "latitude": lat,
            "longitude": lon,
            "datetime": item["startTime"],
            "temperature": item["values"].get("temperature"),
            "humidity": item["values"].get("humidity"),
            "cloudCover": item["values"].get("cloudCover"),
            "windSpeed": item["values"].get("windSpeed"),
            "rainIntensity": item["values"].get("rainIntensity"),
        }
        results.append(weather_info)

    # Affichage des paramétre météo
    for entry in results:
        print(f"{entry['datetime']} ➤ Température : {entry['temperature']}°C")

    # Enregistrement dans El_malick_meteo_dakar.json
    with open("./data/api/El_malick_meteo_dakar.json", "a", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=4)

    print(" Données météo enregistrées avec succès.")
    
except Exception as e:
    print(f" Erreur lors de l'appel API : {e}")
