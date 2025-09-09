import psycopg2

def create_tables():
    commands = """
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
    """
    conn = None
    try:
        conn = psycopg2.connect(
        dbname="ponesaltitante",
        user="hobbit",
        password="condado123",
        host="localhost",
        port="5432"
        )
        cur = conn.cursor()
        cur.execute(commands)
        conn.commit()
        cur.close()
        print("Tabela criada com sucesso!")
    except Exception as e:
        print(f"Erro: {e}")
    finally:
        if conn is not None:
            conn.close()
