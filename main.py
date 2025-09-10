from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse, RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
import queries
from database import get_connection
from database import create_tables
create_tables()


app = FastAPI()
templates = Jinja2Templates(directory="templates")


# Página inicial
@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("home.html", {"request": request})

# Listar quartos
@app.get("/quartos", response_class=HTMLResponse)
def listar_quartos(request: Request):
    quartos = queries.get_quartos()
    return templates.TemplateResponse("listar_quartos.html", {"request": request, "quartos": quartos})

# Página de adicionar
@app.get("/add", response_class=HTMLResponse)
def add_page(request: Request):
    return templates.TemplateResponse("add_quarto.html", {"request": request})

# Adicionar quarto
@app.post("/add")
def add_quarto(codigo: str = Form(...), tipo: str = Form(...), preco_diaria: float = Form(...)):
    queries.add_quarto(codigo, tipo, preco_diaria)
    return RedirectResponse("/quartos", status_code=303)

# Deletar quarto
@app.get("/delete/{id}")
def delete_quarto(id: int):
    queries.delete_quarto(id)
    return RedirectResponse("/quartos", status_code=303)

# Atualizar quarto
@app.post("/update/{id}")
def update_quarto(id: int, codigo: str = Form(...), tipo: str = Form(...), preco_diaria: float = Form(...), ocupado: str = Form(...)):
    queries.update_quarto(id, codigo, tipo, preco_diaria, ocupado.lower() == "sim")
    return RedirectResponse("/quartos", status_code=303)

# Reservar quarto
@app.get("/reservar/{id}", response_class=HTMLResponse)
def reservar_page(id: int, request: Request):
    return templates.TemplateResponse("reservar_quarto.html", {"request": request, "quarto_id": id})

@app.post("/reservar/{id}")
def reservar_post(
    id: int,
    checkin: str = Form(...),
    checkout: str = Form(...),
    servicos: str = Form(...)
):
    queries.reservar_quarto(id, checkin, checkout, servicos)
    return RedirectResponse("/quartos", status_code=303)
