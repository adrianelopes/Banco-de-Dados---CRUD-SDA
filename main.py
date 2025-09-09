from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from database import get_connection

app = FastAPI()
templates = Jinja2Templates(directory="templates")

# Página inicial - listar quartos
@app.get("/", response_class=HTMLResponse)
def read_quartos(request: Request):
    conn = get_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute("SELECT * FROM quartos ORDER BY id;")
    quartos = cur.fetchall()
    cur.close()
    conn.close()
    return templates.TemplateResponse("index.html", {"request": request, "quartos": quartos})

# Adicionar quarto
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
    return RedirectResponse("/", status_code=303)

# Deletar quarto
@app.get("/delete/{id}")
def delete_quarto(id: int):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM quartos WHERE id = %s", (id,))
    conn.commit()
    cur.close()
    conn.close()
    return RedirectResponse("/", status_code=303)

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
    return RedirectResponse("/", status_code=303)
