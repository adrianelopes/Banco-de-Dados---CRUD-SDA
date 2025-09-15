from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse, RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
import queries
from fastapi import Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from database import get_connection
from database import create_tables
from queries import QuartoManager
create_tables()


app = FastAPI()
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="templates"), name="static")


manager = QuartoManager()

# Página inicial
@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("home.html", {"request": request})

# Listar quartos
@app.get("/quartos", response_class=HTMLResponse)
def listar_quartos(request: Request, q: str = ""):
    quartos = manager.get_all(q)
    resumo = manager.resumo()
    return templates.TemplateResponse(
        "listar_quartos.html",
        {"request": request, "quartos": quartos, "q": q, **resumo}
    )   

# Página de adicionar
@app.get("/add", response_class=HTMLResponse)
def add_page(request: Request):
    return templates.TemplateResponse("add_quarto.html", {"request": request})

# Adicionar quarto
@app.post("/add")
def add_quarto(codigo: str = Form(...), tipo: str = Form(...), preco_diaria: float = Form(...)):
    manager.add(codigo, tipo, preco_diaria)
    return RedirectResponse("/quartos", status_code=303)

# Deletar quarto
@app.get("/delete/{id}")
def delete_quarto(id: int):
    manager.delete(id)
    return RedirectResponse("/quartos", status_code=303)

# Atualizar quarto
@app.post("/update/{id}")
def update(id: int, codigo: str = Form(...), tipo: str = Form(...), preco_diaria: float = Form(...), ocupado: str = Form(...)):
    manager.update(id, codigo, tipo, preco_diaria, ocupado.lower() == "sim")
    return RedirectResponse("/quartos", status_code=303)

# Reservar quarto
@app.get("/reservar/{id}", response_class=HTMLResponse)
def reservar_page(id: int, request: Request):
    quarto = manager.get_by_id(id)
    if not quarto:
        return HTMLResponse(f"<h1>Quarto {id} não encontrado</h1>", status_code=404)

    quarto_tipo = quarto.tipo or "anao"  
    foto_url = f"/static/imagens/{quarto_tipo.lower()}.png"

    return templates.TemplateResponse(
        "reservar_quarto.html",
        {"request": request, "quarto_id": id, "quarto_tipo": quarto_tipo, "foto_url": foto_url}
    )
    
@app.post("/reservar/{id}")
def reservar_post(
   id: int,
    checkin: str = Form(...),
    checkout: str = Form(...),
    servicos: str = Form("")
):
    quarto = manager.get_by_id(id)
    if quarto:
        quarto.reservar(checkin, checkout, servicos)
        manager.update(quarto)
    return RedirectResponse("/quartos", status_code=303)

@app.get("/liberar/{id}")
def liberar_quarto(id: int):
    quarto = manager.get_by_id(id)
    if quarto:
        quarto.liberar()
        manager.update(quarto)
    return RedirectResponse("/quartos", status_code=303)

@app.get("/relatorio", response_class=HTMLResponse)
def relatorio(request: Request):
    dados = manager.get_relatorio_quartos()
    return templates.TemplateResponse(
        "relatorio.html",
        {"request": request, **dados}
    )

@app.get("/quarto/{id}")
def detalhes_quarto(id: int, request: Request):
    quarto = manager.get_quarto(id)
    if not quarto:
        return HTMLResponse("Quarto não encontrado", status_code=404)
    return templates.TemplateResponse("quarto_detalhes.html", {"request": request, "quarto": quarto})
