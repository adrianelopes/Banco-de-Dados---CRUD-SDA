from database import get_connection
import psycopg2.extras
from quarto import Quarto
from datetime import date


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
    cur.execute("SELECT * FROM vendedor WHERE login_vendedor=%s AND senha_hash=%s", (email, senha))
    vendedor = cur.fetchone()
    if vendedor:
        cur.close()
        conn.close()
        return {"tipo": "vendedor", "dados": vendedor}

    cur.close()
    conn.close()
    return None


def criar_conta(nome: str, email: str, senha: str):
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO cliente (nome_cliente, login_cliente, senha_hash) VALUES (%s, %s, %s) RETURNING id_cliente",
            (nome, email, senha)
        )
        cliente_id = cur.fetchone()[0]
        conn.commit()
        cur.close()
        conn.close()
        return True, None, cliente_id
    except Exception as e:
        return False, str(e), None


def criar_conta_vendedor(nome: str, email: str, senha: str):
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO vendedor (nome_vendedor, login_vendedor, senha_hash) VALUES (%s, %s, %s) RETURNING id_vendedor",
            (nome, email, senha)
        )
        vendedor_id = cur.fetchone()[0]
        conn.commit()
        cur.close()
        conn.close()
        return True, None, vendedor_id
    except Exception as e:
        return False, str(e), None


class QuartoManager:
    def __init__(self, conn_factory=get_connection):
        self.conn_factory = conn_factory

    def get_all(self, filtro: str = ""):
        conn = self.conn_factory()
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        if filtro:
            filtro_like = f"%{filtro}%"
            cur.execute("""
                SELECT * FROM quartos 
                WHERE codigo ILIKE %s OR tipo ILIKE %s OR CAST(preco_diaria AS TEXT) ILIKE %s
                ORDER BY id;
            """, (filtro_like, filtro_like, filtro_like))
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

    def add(self, codigo: str, tipo: str, preco_diaria: float, vendedor_id: int | None = None):
        conn = self.conn_factory()
        cur = conn.cursor()
        if vendedor_id is None:
            cur.execute(
                "INSERT INTO quartos (codigo, tipo, preco_diaria) VALUES (%s, %s, %s)",
                (codigo, tipo, preco_diaria)
            )
        else:
            cur.execute(
                "INSERT INTO quartos (codigo, tipo, preco_diaria, vendedor_id) VALUES (%s, %s, %s, %s)",
                (codigo, tipo, preco_diaria, vendedor_id)
            )
        conn.commit()
        cur.close()
        conn.close()

    def update(self, quarto: Quarto):
        conn = self.conn_factory()
        cur = conn.cursor()
        cur.execute("""
            UPDATE quartos 
            SET codigo=%s, tipo=%s, preco_diaria=%s
            WHERE id=%s
        """, (quarto.codigo, quarto.tipo, quarto.preco_diaria, quarto.id))
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

    def get_quartos_cliente(self, filtro: str = ""):
        conn = self.conn_factory()
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        if filtro:
            filtro_like = f"%{filtro}%"
            cur.execute("""
                SELECT q.*, v.nome_vendedor AS vendedor_nome
                FROM quartos q
                JOIN vendedor v ON q.vendedor_id = v.id_vendedor
                WHERE codigo ILIKE %s OR tipo ILIKE %s OR CAST(preco_diaria AS TEXT) ILIKE %s
                ORDER BY id;
            """, (filtro_like, filtro_like, filtro_like))
        else:
            cur.execute("""
                SELECT q.*, v.nome_vendedor AS vendedor_nome
                FROM quartos q
                JOIN vendedor v ON q.vendedor_id = v.id_vendedor
                ORDER BY q.id;
            """)
        rows = cur.fetchall()
        cur.close()
        conn.close()
        return rows

    def get_relatorio_quartos(self, vendedor_id: int):
        conn = self.conn_factory()
        cur = conn.cursor()

        # total de quartos do vendedor
        cur.execute("SELECT COUNT(*) FROM quartos WHERE vendedor_id = %s;", (vendedor_id,))
        total = cur.fetchone()[0]

        # quartos ocupados do vendedor
        cur.execute("""
            SELECT COUNT(DISTINCT q.id)
            FROM quartos q
            JOIN reserva r ON q.id = r.id_quarto
            WHERE q.vendedor_id = %s
            AND r.autorizado = TRUE
            AND r.data_checkin <= %s
            AND r.data_checkout >= %s
        """, (vendedor_id, date.today(), date.today()))
        ocupados = cur.fetchone()[0]

        livres = total - ocupados

        # valor total das reservas ativas
        cur.execute("""
            SELECT COALESCE(SUM(q.preco_diaria), 0)
            FROM quartos q
            JOIN reserva r ON q.id = r.id_quarto
            WHERE q.vendedor_id = %s
            AND r.autorizado = TRUE
            AND r.data_checkin <= %s
            AND r.data_checkout >= %s
        """, (vendedor_id, date.today(), date.today()))
        valor_total = cur.fetchone()[0]

        # média das diárias apenas dos quartos do vendedor
        cur.execute("SELECT COALESCE(AVG(preco_diaria), 0) FROM quartos WHERE vendedor_id = %s;", (vendedor_id,))
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


class ReservaManager:
    def __init__(self, conn_factory=get_connection):
        self.conn_factory = conn_factory

    def criar_reserva(self, id_quarto: int, id_cliente: int, checkin, checkout) -> int:
        """
        Cria uma reserva segura verificando conflitos de datas.
        Levanta ValueError se houver conflito.
        """
        conn = self.conn_factory()
        cur = conn.cursor()
        try:
            # Verificar se já existe reserva no mesmo quarto com datas que se sobrepõem
            cur.execute("""
                SELECT 1 FROM reserva
                WHERE id_quarto = %s
                AND daterange(data_checkin, data_checkout, '[]')
                    && daterange(%s::date, %s::date, '[]')
                LIMIT 1;
            """, (id_quarto, checkin, checkout))
            if cur.fetchone():
                raise ValueError("Data de reserva coincide com outra reserva existente.")

            # Criar a reserva
            cur.execute("""
                INSERT INTO reserva (id_quarto, id_cliente, data_checkin, data_checkout)
                VALUES (%s, %s, %s, %s)
                RETURNING id_reserva;
            """, (id_quarto, id_cliente, checkin, checkout))
            reserva_id = cur.fetchone()[0]
            conn.commit()
            return reserva_id
        except Exception as e:
            conn.rollback()
            raise
        finally:
            cur.close()
            conn.close()


    def listar_reservas_quarto(self, id_quarto: int):
        conn = self.conn_factory()
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute("SELECT * FROM reserva WHERE id_quarto=%s ORDER BY data_checkin;", (id_quarto,))
        rows = cur.fetchall()
        cur.close()
        conn.close()
        return rows

    def listar_reservas_cliente(self, id_cliente: int):
        conn = self.conn_factory()
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute("SELECT * FROM reserva WHERE id_cliente=%s ORDER BY data_checkin;", (id_cliente,))
        rows = cur.fetchall()
        cur.close()
        conn.close()
        return rows

    def listar_pendentes(self):
        conn = self.conn_factory()
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute("SELECT * FROM reserva WHERE autorizado=FALSE;")
        rows = cur.fetchall()
        cur.close()
        conn.close()
        return rows

    def autorizar_reserva(self, id_reserva: int, vendedor_id: int):
        conn = self.conn_factory()
        cur = conn.cursor()
        cur.execute("""
            UPDATE reserva
            SET autorizado=TRUE, autorizado_por=%s, autorizado_em=NOW()
            WHERE id_reserva=%s
        """, (vendedor_id, id_reserva))
        conn.commit()
        cur.close()
        conn.close()

    def rejeitar_reserva(self, id_reserva: int):
        conn = self.conn_factory()
        cur = conn.cursor()
        cur.execute("DELETE FROM reserva WHERE id_reserva=%s;", (id_reserva,))
        conn.commit()
        cur.close()
        conn.close()

    def get_by_id(self, reserva_id: int):
        conn = self.conn_factory()
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute("SELECT * FROM reserva WHERE id_reserva=%s", (reserva_id,))
        row = cur.fetchone()
        cur.close()
        conn.close()
        return row  # Retorna um dicionário ou None
    
    def marcar_como_pago(self, id_reserva: int, metodo: str):
    
        try:
            conn = self.conn_factory()
            cur = conn.cursor()
            cur.execute("""
                UPDATE reserva
                SET pago = TRUE
                WHERE id_reserva = %s
            """, (id_reserva,))
            conn.commit()
            cur.close()
            conn.close()
            return True, None
        except Exception as e:
            return False, str(e)
