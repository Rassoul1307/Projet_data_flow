from kafka import KafkaConsumer
import json

# === CONFIGURATION ===
KAFKA_TOPIC = "meteo_data"
KAFKA_BROKER = "localhost:9092"

# === CONSUMER Kafka ===
consumer = KafkaConsumer(
    KAFKA_TOPIC,
    bootstrap_servers=KAFKA_BROKER,
    auto_offset_reset='earliest',  # Commencer depuis le début des messages genre FIFO
    enable_auto_commit=True,
    group_id="meteo_group",
    value_deserializer=lambda m: json.loads(m.decode("utf-8"))
)

print(f"En écoute sur le topic Kafka : '{KAFKA_TOPIC}'...\n")

# === LECTURE BOUCLE INFINIE ===
for message in consumer:
    print(f"[Kafka] Nouveau message reçu :\n{message.value}\n")
