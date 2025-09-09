from fastapi import FastAPI, Request, Form, Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from database import SessionLocal
from models import Quarto

app = FastAPI()
templates = Jinja2Templates(directory="templates")

# Dependência para pegar a sessão do banco
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Listar quartos
@app.get("/", response_class=HTMLResponse)
def read_quartos(request: Request, db: Session = Depends(get_db)):
    quartos = db.query(Quarto).all()
    return templates.TemplateResponse("index.html", {"request": request, "quartos": quartos})

# Criar quarto
@app.post("/add")
def add_quarto(
    numero: str = Form(...),
    tipo: str = Form(...),
    valor: int = Form(...),
    disponivel: str = Form(...),
    db: Session = Depends(get_db)
):
    novo_quarto = Quarto(numero=numero, tipo=tipo, valor=valor, disponivel=disponivel)
    db.add(novo_quarto)
    db.commit()
    return {"message": "Quarto adicionado com sucesso!"}
