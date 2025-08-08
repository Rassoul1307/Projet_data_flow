from kafka import KafkaConsumer
import redis
import json
import time

# === CONFIGURATION ===
KAFKA_TOPIC = "meteo_data"  # Changé pour correspondre au producer
KAFKA_BOOTSTRAP_SERVERS = ["localhost:9092"]  # Changé de localhost à kafka
REDIS_HOST = "redis_airflow"  # Changé pour utiliser le nom du service
REDIS_PORT = 6379
TIMEOUT_SECONDS = 60  # Timeout pour éviter que le consumer tourne indéfiniment

# === CONNEXIONS ===

# Test de connexion Redis
try:
    r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=0, socket_timeout=5)
    r.ping()
    print(f"✓ Connexion Redis établie sur {REDIS_HOST}:{REDIS_PORT}")
except Exception as e:
    print(f"✗ Erreur connexion Redis : {e}")
    exit(1)

# Kafka consumer
try:
    consumer = KafkaConsumer(
        KAFKA_TOPIC,
        bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
        value_deserializer=lambda m: json.loads(m.decode("utf-8")),
        auto_offset_reset='earliest',  # Changé à 'earliest' pour traiter tous les messages
        enable_auto_commit=True,
        group_id="meteo-consumer-group",
        consumer_timeout_ms=TIMEOUT_SECONDS * 1000  # Timeout en millisecondes
    )
    print(f"✓ Consumer Kafka prêt sur le topic '{KAFKA_TOPIC}'")
except Exception as e:
    print(f"✗ Erreur connexion Kafka : {e}")
    exit(1)

# === BOUCLE DE CONSOMMATION ===
message_count = 0
start_time = time.time()

print(f"🔄 Début de la consommation (timeout: {TIMEOUT_SECONDS}s)")

try:
    for message in consumer:
        data = message.value  # dict
        message_count += 1
        
        print(f"📨 Message {message_count} reçu depuis Kafka : {data}")
        
        # On stocke chaque message dans une liste Redis (type List)
        try:
            r.lpush("weather_data", json.dumps(data))
            print(f"✓ Message {message_count} stocké dans Redis ➤ liste 'weather_data'")
            
            # Vérification du stockage
            list_length = r.llen("weather_data")
            print(f"📊 Total messages dans Redis : {list_length}")
            
        except Exception as e:
            print(f"✗ Erreur stockage Redis : {e}")
        
        # Vérification du timeout
        if time.time() - start_time > TIMEOUT_SECONDS:
            print(f"⏰ Timeout atteint ({TIMEOUT_SECONDS}s)")
            break

except Exception as e:
    print(f"✗ Erreur consommation Kafka : {e}")

finally:
    consumer.close()
    print(f"🏁 Consumer fermé - {message_count} messages traités")
    
    # Affichage du résumé
    try:
        total_in_redis = r.llen("weather_data")
        print(f"📈 Résumé : {total_in_redis} messages au total dans Redis")
        
        # Afficher le dernier message pour vérification
        if total_in_redis > 0:
            latest_message = r.lindex("weather_data", 0)
            print(f"📄 Dernier message : {latest_message.decode('utf-8') if latest_message else 'None'}")
    except Exception as e:
        print(f"✗ Erreur récupération résumé : {e}")