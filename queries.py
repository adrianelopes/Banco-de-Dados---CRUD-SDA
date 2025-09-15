from database import get_connection
import psycopg2.extras
from quarto import Quarto   # supondo que você crie um arquivo models.py

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

    def add(self, codigo: str, tipo: str, preco_diaria: float, ocupado: bool = False):
        conn = self.conn_factory()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO quartos (codigo, tipo, preco_diaria, ocupado) VALUES (%s, %s, %s, %s)",
            (codigo, tipo, preco_diaria, ocupado)
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

