import psycopg2
import pandas as pd

conn = psycopg2.connect(
    host = "postgres_meteo",
    port = "5432",
    dbname = "",
    user = "",
    password = ""

)