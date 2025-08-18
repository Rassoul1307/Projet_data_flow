from pyspark.sql import SparkSession
from hdfs import InsecureClient

# ------------------ PostgreSQL Credentials ------------------
pg_user = "postgres"
pg_password = "azoupro"
pg_host = "postgres_meteo"
pg_port = 5432
pg_db = "meteo_dakar"
pg_table = "metheo_dakar"  # adapte le nom

# ------------------ Init SparkSession ------------------
spark = SparkSession.builder \
    .appName("MultiBasestoHDFS") \
    .config("spark.jars.packages","org.postgresql:postgresql:42.6.0") \
    .getOrCreate()


# ------------------ PostgreSQL → HDFS ------------------
try:
    pg_url = f"jdbc:postgresql://{pg_host}:{pg_port}/{pg_db}"
    pg_properties = {
        "user": pg_user,
        "password": pg_password,
        "driver": "org.postgresql.Driver"
    }

    pg_df = spark.read.jdbc(url=pg_url, table=pg_table, properties=pg_properties)
    print("✅ Data read from PostgreSQL successfully.")
    pg_df.printSchema()
    pg_df.show(5)

    hdfs_path_pg = "hdfs://namenode:8020/mes_donnees/pyspark1/postgres_data"
    pg_df.write.format("parquet").mode("overwrite").save(hdfs_path_pg)
    print(f"✅ PostgreSQL data written to HDFS at: {hdfs_path_pg}")

except Exception as e:
    print(f"❌ PostgreSQL error: {e}")
