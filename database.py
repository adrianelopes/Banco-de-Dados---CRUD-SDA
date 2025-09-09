import psycopg2

def get_connection():
    conn = psycopg2.connect(
        dbname="ponesaltitante",
        user="hobbit",
        password="condado123",
        host="localhost",
        port="5432"
    )
    return conn

def create_tables():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS quartos (
        id SERIAL PRIMARY KEY,
        codigo VARCHAR(10) NOT NULL,
        tipo VARCHAR(100) NOT NULL,
        preco_diaria NUMERIC(10,2) NOT NULL,
        ocupado BOOLEAN DEFAULT FALSE,
        servicos TEXT,
        checkin DATE,
        checkout DATE
    );
    """)
    conn.commit()
    cur.close()
    conn.close()
    print("Tabela 'quartos' criada ou já existente.")
