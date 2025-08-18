from kafka import KafkaConsumer
import redis
import json

# Configuration de kafka_redis
KAFKA_BROKER = 'kafka:9092'        
TOPIC_NAME = 'weather_dakar'
REDIS_HOST = 'my_redis'             
REDIS_PORT = 6379
REDIS_KEY = 'weather_data'

#Initialisation de  REDIS 
redis_client = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT, db=0)

# Initialisation du Kafka Consumer
consumer = KafkaConsumer(
    TOPIC_NAME,
    bootstrap_servers=KAFKA_BROKER,
    auto_offset_reset='earliest',
    value_deserializer=lambda m: json.loads(m.decode('utf-8'))
)

# Traitement des messages
print("En attente de messages météo depuis Kafka...")

for message in consumer:
    data = message.value
    print(f"Reçu depuis Kafka : {data}")

    # Ajouter les données dans Redis de type LIST
    redis_client.rpush(REDIS_KEY, json.dumps(data))
    print("→ Donnée poussée dans Redis")