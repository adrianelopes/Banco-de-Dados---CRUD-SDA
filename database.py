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
    CREATE TABLE IF NOT EXISTS vendedor (
        id_vendedor SERIAL PRIMARY KEY,
        login VARCHAR(100) NOT NULL UNIQUE,
        senha_hash VARCHAR(200) NOT NULL,
        nome VARCHAR(200) NOT NULL
    );
    """)
        
    cur.execute("""
    CREATE TABLE IF NOT EXISTS quartos (
        id SERIAL PRIMARY KEY,
        codigo VARCHAR(10) NOT NULL,
        tipo VARCHAR(100) NOT NULL,
        preco_diaria NUMERIC(10,2) NOT NULL,
        ocupado BOOLEAN DEFAULT FALSE,
        status VARCHAR(20) NOT NULL,
        servicos TEXT,
        checkin DATE,
        checkout DATE,
        vendedor_id INT,
        CONSTRAINT fk_vendedor_quarto FOREIGN KEY (vendedor_id) REFERENCES vendedor(id_vendedor) ON DELETE SET NULL
    );
    """)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS cliente (
        id_cliente SERIAL PRIMARY KEY,
        login_cliente VARCHAR(100) NOT NULL UNIQUE,
        nome_cliente VARCHAR(200) NOT NULL,
        senha_hash VARCHAR(200) NOT NULL
    );
    """)
    
    cur.execute("""
    CREATE TABLE IF NOT EXISTS reserva (
        id_reserva SERIAL PRIMARY KEY,
        id_quarto INT NOT NULL,
        id_cliente INT NOT NULL,
        data_checkin DATE NOT NULL,
        data_checkout DATE NOT NULL,
        pago BOOLEAN DEFAULT FALSE,
        autorizado BOOLEAN DEFAULT FALSE,
        autorizado_por INT,
        autorizado_em TIMESTAMP,
        CONSTRAINT fk_quarto_reserva FOREIGN KEY (id_quarto) REFERENCES quartos(id) ON DELETE CASCADE,
        CONSTRAINT fk_cliente_reserva FOREIGN KEY (id_cliente) REFERENCES cliente(id_cliente) ON DELETE CASCADE,
        CONSTRAINT fk_vendedor_autorizador FOREIGN KEY (autorizado_por) REFERENCES vendedor(id_vendedor) ON DELETE SET NULL
    );
    """)
    
    cur.execute("CREATE INDEX IF NOT EXISTS idx_reserva_id_quarto ON reserva(id_quarto);")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_reserva_id_cliente ON reserva(id_cliente);")

    conn.commit()
    cur.close()
    conn.close()
    print("Tabela 'quartos' criada ou já existente.")
