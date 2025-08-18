import requests
import json
from kafka import KafkaProducer

# CONFIGURATION
TOMORROW_API_KEY = "OC9yH405dZFT1BOO6w6nPgDanrhpPwV8"
LAT, LON = 14.6937, -17.4441  
KAFKA_BROKER = 'kafka:9092'  
TOPIC_NAME = 'weather_dakar'

# On initialise le PRODUCER
producer = KafkaProducer(
    bootstrap_servers=KAFKA_BROKER,
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

# Fonction d'appel de l'api Tomorrow.io
def get_weather():
    url = f"https://api.tomorrow.io/v4/weather/realtime?location={LAT},{LON}&apikey={TOMORROW_API_KEY}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        weather = data.get("data", {}).get("values", {})
        return {
            "temperature": weather.get("temperature"),
            "humidity": weather.get("humidity"),
            "windSpeed": weather.get("windSpeed"),
            "cloudCover": weather.get("cloudCover"),
            "rainIntensity": weather.get("rainIntensity"),
            "timestamp": data.get("data", {}).get("time")
        }
    else:
        print("Erreur d'appel API:", response.status_code)
        return None

# Fonction principale
def run():
    weather_data = get_weather()
    if weather_data:
        print(f"Envoi vers Kafka : {weather_data}")
        producer.send(TOPIC_NAME, weather_data)
        producer.flush()
    else:
        print("Aucune donnée météo récupérée.")

if __name__ == "__main__":
    run()