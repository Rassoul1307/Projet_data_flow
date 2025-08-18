from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col
from pyspark.sql.types import StructType, StringType, FloatType, TimestampType

# Initialisation Spark avec HDFS
spark = SparkSession.builder \
    .appName("KafkaToHDFSWeather") \
    .master("local[*]") \
    .config("spark.hadoop.fs.defaultFS", "hdfs://namenode:9000") \
    .config("spark.hadoop.dfs.client.use.datanode.hostname", "true") \
    .config("spark.hadoop.dfs.datanode.use.datanode.hostname", "true") \
    .config("spark.sql.adaptive.enabled", "false") \
    .getOrCreate()

spark.sparkContext.setLogLevel("WARN")

# Schéma des données JSON
schema = StructType() \
    .add("temperature", FloatType()) \
    .add("humidity", FloatType()) \
    .add("windSpeed", FloatType()) \
    .add("cloudCover", FloatType()) \
    .add("rainIntensity", FloatType()) \
    .add("timestamp", StringType()) 

print("Connexion à Kafka...")

try:
    # Lecture du flux Kafka - Docker network
    df_raw = spark.readStream \
        .format("kafka") \
        .option("kafka.bootstrap.servers", "kafka:9092") \
        .option("subscribe", "weather_dakar") \
        .option("startingOffsets", "latest") \
        .option("failOnDataLoss", "false") \
        .load()
    print("Connexion Kafka réussie (kafka:9092)")
except Exception as e:
    print(f"Erreur connexion Kafka: {e}")
    raise e

# Transformation des données
print("Transformation des données JSON...")
df_json = df_raw.selectExpr("CAST(value AS STRING) as json_string")
df_parsed = df_json.select(
    from_json(col("json_string"), schema).alias("data")
).select("data.*")

# ÉCRITURE DANS HDFS (data lake)
print("Démarrage du streaming vers HDFS...")
query = df_parsed.writeStream \
    .format("parquet") \
    .option("checkpointLocation", "/checkpoints/weather") \
    .option("path", "/data/weather") \
    .outputMode("append") \
    .trigger(processingTime="1 minute") \
    .start()

print("Streaming actif - Données météo sauvegardées dans HDFS:/data/weather")
query.awaitTermination()

print("Streaming terminé.")
spark.stop()