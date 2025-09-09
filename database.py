import psycopg2
import psycopg2.extras

# Configuração da conexão
def get_connection():
    conn = psycopg2.connect(
        dbname="crud_db",
        user="myuser",
        password="mypassword",
        host="localhost",
        port="5432"
    )
    return conn
