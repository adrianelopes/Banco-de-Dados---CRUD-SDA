from database import get_connection
import psycopg2.extras
from quarto import Quarto  

def autenticar(email, senha):
    conn = get_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

    # Procurar usuário nos clientes
    cur.execute("SELECT * FROM cliente WHERE login_cliente=%s AND senha_hash=%s", (email, senha))
    cliente = cur.fetchone()
    if cliente:
        cur.close()
        conn.close()
        return {"tipo": "cliente", "dados": cliente}

    # Procurar usuário nos vendedores
    cur.execute("SELECT * FROM vendedor WHERE login=%s AND senha_hash=%s", (email, senha))
    vendedor = cur.fetchone()
    if vendedor:
        cur.close()
        conn.close()
        return {"tipo": "vendedor", "dados": vendedor}

    cur.close()
    conn.close()
    return None

def criar_conta(nome: str, email: str, senha: str):
    conn = get_connection()
    cur = conn.cursor()
    
    # Verificar se o email já existe
    cur.execute("SELECT * FROM cliente WHERE login_cliente=%s", (email,))
    if cur.fetchone():
        cur.close()
        conn.close()
        return False, "Email já cadastrado"
    
    # Inserir novo cliente
    cur.execute(
        "INSERT INTO cliente (nome_cliente, login_cliente, senha_hash) VALUES (%s, %s, %s)",
        (nome, email, senha)  # no futuro substitua 'senha' por hash
    )
    conn.commit()
    cur.close()
    conn.close()
    
    return True, None

def criar_conta_vendedor(nome, email, senha):
    conn = get_connection()
    cur = conn.cursor()
    # Verifica se email já existe
    cur.execute("SELECT * FROM vendedor WHERE login=%s", (email,))
    if cur.fetchone():
        cur.close()
        conn.close()
        return False, "Email já cadastrado"
    
    # Inserir novo vendedor com a coluna correta
    cur.execute(
        "INSERT INTO vendedor (nome, login, senha_hash) VALUES (%s, %s, %s)",
        (nome, email, senha)
    )
    conn.commit()
    cur.close()
    conn.close()
    return True, None

class QuartoManager:
    def __init__(self, conn_factory=get_connection):
        self.conn_factory = conn_factory

    def get_all(self, filtro: str = ""):
        conn = self.conn_factory()
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        if filtro:
            filtro = f"%{filtro}%"
            cur.execute("""
                SELECT * FROM quartos 
                WHERE codigo ILIKE %s OR tipo ILIKE %s OR CAST(preco_diaria AS TEXT) ILIKE %s
                ORDER BY id;
            """, (filtro, filtro, filtro))
        else:
            cur.execute("SELECT * FROM quartos ORDER BY id;")
        rows = cur.fetchall()
        cur.close()
        conn.close()
        return [Quarto(**row) for row in rows]

    def get_by_id(self, quarto_id: int):
        conn = self.conn_factory()
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute("SELECT * FROM quartos WHERE id=%s", (quarto_id,))
        row = cur.fetchone()
        cur.close()
        conn.close()
        return Quarto(**row) if row else None

    def add(self, codigo: str, tipo: str, preco_diaria: float, vendedor_id: int | None = None, ocupado: bool = False):
        conn = self.conn_factory()
        cur = conn.cursor()
        if vendedor_id is None:
            cur.execute(
                "INSERT INTO quartos (codigo, tipo, preco_diaria, ocupado) VALUES (%s, %s, %s, %s)",
                (codigo, tipo, preco_diaria, ocupado)
            )
        else:
            cur.execute(
                "INSERT INTO quartos (codigo, tipo, preco_diaria, ocupado, vendedor_id) VALUES (%s, %s, %s, %s, %s)",
                (codigo, tipo, preco_diaria, ocupado, vendedor_id)
            )
        conn.commit()
        cur.close()
        conn.close()


    def update(self, quarto: Quarto):
        conn = self.conn_factory()
        cur = conn.cursor()
        cur.execute("""
            UPDATE quartos 
            SET codigo=%s, tipo=%s, preco_diaria=%s, ocupado=%s, checkin=%s, checkout=%s, servicos=%s
            WHERE id=%s
        """, (quarto.codigo, quarto.tipo, quarto.preco_diaria, quarto.ocupado,
              quarto.checkin, quarto.checkout, quarto.servicos, quarto.id))
        conn.commit()
        cur.close()
        conn.close()

    def delete(self, quarto_id: int):
        conn = self.conn_factory()
        cur = conn.cursor()
        cur.execute("DELETE FROM quartos WHERE id=%s", (quarto_id,))
        conn.commit()
        cur.close()
        conn.close()

    def resumo(self):
        conn = self.conn_factory()
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM quartos;")
        total = cur.fetchone()[0]

        cur.execute("SELECT COUNT(*) FROM quartos WHERE ocupado=FALSE;")
        livres = cur.fetchone()[0]

        cur.execute("SELECT COUNT(*) FROM quartos WHERE ocupado=TRUE;")
        ocupados = cur.fetchone()[0]

        cur.close()
        conn.close()

        return {"total_quartos": total, "quartos_livres": livres, "quartos_ocupados": ocupados}

    def get_relatorio_quartos(self):
        conn = get_connection()
        cur = conn.cursor()

        # total de quartos
        cur.execute("SELECT COUNT(*) FROM quartos;")
        total = cur.fetchone()[0]

        # quartos livres
        cur.execute("SELECT COUNT(*) FROM quartos WHERE ocupado = FALSE;")
        livres = cur.fetchone()[0]

        # quartos ocupados
        cur.execute("SELECT COUNT(*) FROM quartos WHERE ocupado = TRUE;")
        ocupados = cur.fetchone()[0]

        # valor total das reservas (somatório do preço dos ocupados)
        cur.execute("SELECT COALESCE(SUM(preco_diaria), 0) FROM quartos WHERE ocupado = TRUE;")
        valor_total = cur.fetchone()[0]

        # valor médio da diária
        cur.execute("SELECT COALESCE(AVG(preco_diaria), 0) FROM quartos;")
        valor_medio = cur.fetchone()[0]

        cur.close()
        conn.close()

        return {
            "total_quartos": total,
            "quartos_livres": livres,
            "quartos_ocupados": ocupados,
            "valor_total_reservas": valor_total,
            "valor_medio_diaria": valor_medio
        }

    def get_quarto(self, quarto_id: int):
        conn = self.conn_factory()
        cur = conn.cursor()
        cur.execute("SELECT * FROM quartos WHERE id=%s", (quarto_id,))
        quarto = cur.fetchone()
        conn.close()
        return quarto
    
    def get_quartos_vendedor(self, vendedor_id: int, filtro: str = ""):
        conn = self.conn_factory()
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

        query = "SELECT * FROM quartos WHERE vendedor_id = %s"
        params = [vendedor_id]

        if filtro:
            filtro_like = f"%{filtro}%"
            query += " AND (codigo ILIKE %s OR tipo ILIKE %s OR CAST(preco_diaria AS TEXT) ILIKE %s)"
            params.extend([filtro_like, filtro_like, filtro_like])

        query += " ORDER BY id;"
        cur.execute(query, tuple(params))
        rows = cur.fetchall()
        cur.close()
        conn.close()
        return [Quarto(**row) for row in rows]

