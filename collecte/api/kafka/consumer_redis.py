from kafka import KafkaConsumer
import redis
import json

# CONFIGURATION 
KAFKA_BROKER = 'kafka:9092'        # ← SEULS CHANGEMENTS
TOPIC_NAME = 'weather_dakar'
REDIS_HOST = 'my_redis'             # ← ICI
REDIS_PORT = 6379
REDIS_KEY = 'weather_data'

# ==== INIT REDIS ====
redis_client = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT, db=0)

# Initialisation du Kafka Consumer
consumer = KafkaConsumer(
    TOPIC_NAME,
    bootstrap_servers=KAFKA_BROKER,
    auto_offset_reset='earliest',
    value_deserializer=lambda m: json.loads(m.decode('utf-8'))
)

# TRAITEMENT DES MESSAGES
print("En attente de messages météo depuis Kafka...")

for message in consumer:
    data = message.value
    print(f"Reçu depuis Kafka : {data}")

    # Ajoute les données dans Redis (structure LIST)
    redis_client.rpush(REDIS_KEY, json.dumps(data))
    print("→ Donnée poussée dans Redis")