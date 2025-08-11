from pyspark.sql import SparkSession
from hdfs import InsecureClient

# ------------------ MongoDB Credentials ------------------
username = "root"
password = "passer123"
mongo_host = "mongo"
mongo_port = 27017
auth_db = "admin"
db_name = "meteo_base"
collection_name = "meteo_collection"

# ------------------ PostgreSQL Credentials ------------------
pg_user = "postgres"
pg_password = "azoupro"
pg_host = "postgres_meteo"
pg_port = 5432
pg_db = "meteo_dakar"
pg_table = "metheo_dakar"  # adapte le nom

# ------------------ Mysql Credentials ------------------
mysql_user = "appuser"
mysql_password = "apppassword123"
mysql_host = "mysql"
mysql_port = 3306
mysql_db = "meteo_db"
mysql_table = "metheo_dakar"  # adapte le nom



# ------------------ Init SparkSession ------------------
spark = SparkSession.builder \
    .appName("MultiBasestoHDFS") \
    .config("spark.jars.packages",
            "org.mongodb.spark:mongo-spark-connector_2.12:3.0.1,",
            "mysql:mysql-connector-java:8.0.33,"
            "org.postgresql:postgresql:42.6.0") \
    .getOrCreate()

# ------------------ MongoDB → HDFS ------------------
mongo_uri = f"mongodb://{username}:{password}@{mongo_host}:{mongo_port}/{db_name}.{collection_name}?authSource={auth_db}"

try:
    mongo_df = spark.read.format("mongo").option("uri", mongo_uri).load()
    print("✅ Data read from MongoDB successfully.")
    mongo_df.printSchema()
    mongo_df.show(5)

    hdfs_client = InsecureClient("http://hadoop-namenode:9870", user="root")
    print("✅ connexion à HDFS réussie")

    hdfs_path_mongo = "hdfs://hadoop-namenode:9000/mes_donnees/pyspark1/mongo_data"
    mongo_df.write.format("parquet").mode("overwrite").save(hdfs_path_mongo)
    print(f"✅ MongoDB data written to HDFS at: {hdfs_path_mongo}")

except Exception as e:
    print(f"❌ MongoDB error: {e}")

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

    hdfs_path_pg = "hdfs://hadoop-namenode:9000/mes_donnees/pyspark1/postgres_data"
    pg_df.write.format("parquet").mode("overwrite").save(hdfs_path_pg)
    print(f"✅ PostgreSQL data written to HDFS at: {hdfs_path_pg}")

except Exception as e:
    print(f"❌ PostgreSQL error: {e}")

# --------------------- Mysql -> HDFS ----------------------
try:
    mysql_url = f"jdbc:mysql://{mysql_host}:{mysql_port}/{mysql_db}"
    mysql_properties = {
        "user": mysql_user,
        "password": mysql_password,
        "driver": "com.mysql.cj.jdbc.Driver"
    }
    mysql_df = spark.read.jdbc(url= mysql_url, table = mysql_table, properties = mysql_properties)
    print("✅ Data read from Mysql successfully.")
    hdfs_path_mysql = "hdfs://hadoop-namenode:9000/mes_donnees/pyspark1/mysql_data"
    mysql_df.write.format("parquet").mode("overwrite").save(hdfs_path_mysql)
except Exception as e :
    print(f"❌ PostgreSQL error: {e}")



finally:
    spark.stop()
    print("SparkSession stopped.")