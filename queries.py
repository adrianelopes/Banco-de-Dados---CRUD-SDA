from database import get_connection
import psycopg2
import psycopg2.extras

# Buscar todos os quartos
def get_quartos(filtro: str = ""):
    conn = get_connection()
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
    quartos = cur.fetchall()
    cur.close()
    conn.close()
    return quartos

def get_quarto_by_id(quarto_id: int):
    conn = get_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute("SELECT * FROM quartos WHERE id=%s", (quarto_id,))
    quarto = cur.fetchone()
    cur.close()
    conn.close()
    return quarto

# Inserir novo quarto
def add_quarto(codigo: str, tipo: str, preco_diaria: float, ocupado: bool = False):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO quartos (codigo, tipo, preco_diaria, ocupado) VALUES (%s, %s, %s, %s)",
        (codigo, tipo, preco_diaria, ocupado)
    )
    conn.commit()
    cur.close()
    conn.close()

# Atualizar quarto
def update_quarto(quarto_id: int, codigo: str, tipo: str, preco_diaria: float, ocupado: bool):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "UPDATE quartos SET codigo=%s, tipo=%s, preco_diaria=%s, ocupado=%s WHERE id=%s",
        (codigo, tipo, preco_diaria, ocupado, quarto_id)
    )
    conn.commit()
    cur.close()
    conn.close()

# Deletar quarto
def delete_quarto(quarto_id: int):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM quartos WHERE id=%s", (quarto_id,))
    conn.commit()
    cur.close()
    conn.close()

# Reservar quarto (só marca ocupado = True)
def reservar_quarto(quarto_id: int):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "UPDATE quartos SET ocupado = TRUE WHERE id = %s AND ocupado = FALSE",
        (quarto_id,)
    )
    updated = cur.rowcount
    conn.commit()
    cur.close()
    conn.close()
    return updated > 0

def get_resumo_quartos():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM quartos;")
    total = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM quartos WHERE ocupado = FALSE;")
    livres = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM quartos WHERE ocupado = TRUE;")
    ocupados = cur.fetchone()[0]

    cur.close()
    conn.close()

    return {
        "total_quartos": total,
        "quartos_livres": livres,
        "quartos_ocupados": ocupados
    }

def reservar_quarto(quarto_id: int, checkin: str, checkout: str, servicos: str):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        UPDATE quartos
        SET checkin=%s,
            checkout=%s,
            servicos=%s,
            ocupado=TRUE
        WHERE id=%s
    """, (checkin, checkout, servicos, quarto_id))
    conn.commit()
    cur.close()
    conn.close()
    
    