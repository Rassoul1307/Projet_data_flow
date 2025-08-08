from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col
from pyspark.sql.types import StructType, StringType, FloatType, TimestampType

# 1. Initialiser Spark Session avec Structured Streaming
spark = (
    SparkSession.builder
    .appName("MeteoKafkaToHDFS")
    .master("yarn")
    .getOrCreate()
)

# spark = SparkSession.builder \
#     .appName("KafkaToHDFS") \
#     .config("spark.hadoop.fs.defaultFS", "hdfs://namenode:8020") \
#     .config("spark.hadoop.fs.hdfs.impl", "org.apache.hadoop.hdfs.DistributedFileSystem") \
#     .getOrCreate()

# spark.sparkContext.setLogLevel("WARN")

# 2. Schéma des données JSON (à adapter à ta structure API météo)
schema = (
    StructType()
    .add("temperature", FloatType())
    .add("humidity", FloatType())
    .add("windSpeed", FloatType())
    .add("cloudCover", FloatType())
    .add("rainIntensity", FloatType())
    .add("timestamp", TimestampType())
)

# 3. Lire depuis Kafka (streaming)
df_kafka = (
    spark.readStream
    .format("kafka")
    .option("kafka.bootstrap.servers", "kafka:9092")
    .option("subscribe", "weather_dakar")
    .option("startingOffsets", "earliest")
    .load()
)

# 4. Transformer le message Kafka (clé/valeurs binaires → JSON structuré)
df_parsed = (
    df_kafka.selectExpr("CAST(value AS STRING) as json_value")
    .select(from_json(col("json_value"), schema).alias("data"))
    .select("data.*")
)

# 5. Écrire dans HDFS (en format Parquet par défaut, ou JSON)
output_path = "hdfs://namenode:9870/datalake/meteo_stream"

query = (
    df_parsed.writeStream
    .format("parquet")
    .option("path", output_path)
    .option("checkpointLocation", "hdfs://namenode:8020/checkpoints/weather_checkpoint")
    .outputMode("append")
    .start()
)

query.awaitTermination()
