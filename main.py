from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse, RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
import psycopg2
import psycopg2.extras
from database import get_connection
from database import create_tables
create_tables()


app = FastAPI()
templates = Jinja2Templates(directory="templates")

# Página inicial - Home
@app.get("/", response_class=HTMLResponse)
def read_quartos(request: Request):
    conn = get_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute("SELECT * FROM quartos ORDER BY id;")
    quartos = cur.fetchall()
    cur.close()
    conn.close()
    return templates.TemplateResponse("home.html", {"request": request})

# Adicionar quarto
@app.get("/add", response_class=HTMLResponse)
def add_page(request: Request):
    return templates.TemplateResponse("add_quarto.html", {"request": request})

@app.post("/add")
def add_quarto(numero: str = Form(...), tipo: str = Form(...), valor: int = Form(...), disponivel: str = Form(...)):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO quartos (numero, tipo, valor, disponivel) VALUES (%s, %s, %s, %s)",
        (numero, tipo, valor, disponivel)
    )
    conn.commit()
    cur.close()
    conn.close()
    return RedirectResponse("/quartos", status_code=303)

@app.get("/quartos", response_class=HTMLResponse)
def listar_quartos(request: Request):
    conn = get_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute("SELECT * FROM quartos ORDER BY id;")
    quartos = cur.fetchall()
    cur.close()
    conn.close()
    return templates.TemplateResponse("listar_quartos.html", {"request": request, "quartos": quartos})

#Listar quartos
@app.get("/quartos", response_class=HTMLResponse)
def listar_quartos(request: Request):
    conn = get_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute("SELECT * FROM quartos ORDER BY id;")
    quartos = cur.fetchall()
    cur.close()
    conn.close()
    return templates.TemplateResponse("listar_quartos.html", {"request": request, "quartos": quartos})

# Deletar quarto
@app.get("/delete/{id}")
def delete_quarto(id: int):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM quartos WHERE id=%s", (id,))
    conn.commit()
    cur.close()
    conn.close()
    return RedirectResponse("/quartos", status_code=303)

# Atualizar quarto
@app.post("/update/{id}")
def update_quarto(id: int, numero: str = Form(...), tipo: str = Form(...), valor: int = Form(...), disponivel: str = Form(...)):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "UPDATE quartos SET numero=%s, tipo=%s, valor=%s, disponivel=%s WHERE id=%s",
        (numero, tipo, valor, disponivel, id)
    )
    conn.commit()
    cur.close()
    conn.close()
    return RedirectResponse("/quartos", status_code=303)
