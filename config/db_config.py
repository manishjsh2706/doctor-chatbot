# import psycopg2

# def get_db_connection():
#     return psycopg2.connect(
#         #host="localhost",
#         host="host.docker.internal",
#         database="superclinic",
#         user="postgres",
#         password="admin",
#         port=5432
#     )
import os
import psycopg2

def get_db_connection():
    # It will look for the environment variable 'DB_HOST', 
    # and if not found, it defaults to 'db'
    return psycopg2.connect(
        host=os.getenv('DB_HOST', 'db'),
        database=os.getenv('DB_NAME', 'superclinic'),
        user=os.getenv('DB_USER', 'postgres'),
        password=os.getenv('DB_PASSWORD', 'admin'),
        port=5432
    )