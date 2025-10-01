from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse, RedirectResponse, JSONResponse, FileResponse 
from fastapi.templating import Jinja2Templates
from fastapi import Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from database import create_tables
from queries import QuartoManager, autenticar, criar_conta, criar_conta_vendedor
from quarto import Quarto
from pathlib import Path
from fastapi.staticfiles import StaticFiles
import csv
from fastapi import Cookie
create_tables()

app = FastAPI()

# templates directory
templates_dir = Path(__file__).parent / "templates"
templates = Jinja2Templates(directory=str(templates_dir))

# monte apenas a pasta templates inteira em /static (assim /static/imagens/x.png funciona)
app.mount("/static", StaticFiles(directory=str(templates_dir)), name="static")

manager = QuartoManager()


# -----------------------
# HOME / PÁGINAS INICIAIS
# -----------------------
@app.get("/", response_class=HTMLResponse)
def home(request: Request, user_type: str | None = Cookie(default=None), user_name: str | None = Cookie(default=None)):
    return templates.TemplateResponse(
        "home_comum.html",
        {"request": request, "user_name": user_name, "user_type": user_type}
    )


@app.get("/home_cliente", response_class=HTMLResponse)
def home_cliente(request: Request, user_name: str | None = Cookie(default=None)):
    quartos = manager.get_all()
    return templates.TemplateResponse("home_cliente.html", {"request": request, "quartos": quartos, "user_name": user_name})


@app.get("/home_vendedor", response_class=HTMLResponse)
def home_vendedor(request: Request, user_name: str | None = Cookie(default=None)):
    return templates.TemplateResponse("home_vendedor.html", {"request": request, "user_name": user_name})


# -----------------------
# LOGIN / LOGOUT / CADASTRO
# -----------------------
@app.get("/login", response_class=HTMLResponse)
def login_get(request: Request):
    return templates.TemplateResponse("login.html", {"request": request, "error": ""})


@app.post("/login")
def login_post(request: Request, email: str = Form(...), senha: str = Form(...)):
    usuario = autenticar(email, senha)
    if usuario:
        tipo = usuario["tipo"]
        dados = usuario["dados"]

        # pegar id e nome corretos conforme tipo e setar cookie user_id
        if tipo == "cliente":
            nome = dados.get("nome_cliente")
            user_id = dados.get("id_cliente")
            redirect_target = "/home_cliente"
        else:  # vendedor
            nome = dados.get("nome")
            user_id = dados.get("id_vendedor")
            redirect_target = "/home_vendedor"

        response = RedirectResponse(redirect_target, status_code=303)
        response.set_cookie(key="user_type", value=str(tipo))
        response.set_cookie(key="user_name", value=str(nome))
        response.set_cookie(key="user_email", value=str(email))
        # armazenamos user_id como string (pode ser usado depois para filtrar)
        response.set_cookie(key="user_id", value=str(user_id))
        return response

    return templates.TemplateResponse("login.html", {"request": request, "error": "Email ou senha incorretos"})


@app.get("/criar_conta", response_class=HTMLResponse)
def criar_conta_get(request: Request, tipo: str = "cliente"):
    return templates.TemplateResponse("criar_conta.html", {"request": request, "error": "", "tipo": tipo})


@app.post("/criar_conta")
def criar_conta_post(
    request: Request,
    nome: str = Form(...),
    email: str = Form(...),
    senha: str = Form(...),
    tipo: str = Form("cliente"),
):
    if tipo == "cliente":
        sucesso, erro = criar_conta(nome, email, senha)
        redirect_url = "/home_cliente"
    elif tipo == "vendedor":
        sucesso, erro = criar_conta_vendedor(nome, email, senha)
        redirect_url = "/home_vendedor"
    else:
        return templates.TemplateResponse("criar_conta.html", {"request": request, "error": "Tipo inválido", "tipo": tipo})

    if not sucesso:
        return templates.TemplateResponse("criar_conta.html", {"request": request, "error": erro, "tipo": tipo})

    # login automático (nome/email/cookie tipo); user_id só estará disponível após login real,
    # mas normalmente o usuário pode clicar em login depois se precisar do id.
    response = RedirectResponse(redirect_url, status_code=303)
    response.set_cookie(key="user_type", value=str(tipo))
    response.set_cookie(key="user_name", value=str(nome))
    response.set_cookie(key="user_email", value=str(email))
    return response


@app.get("/logout")
def logout():
    response = RedirectResponse("/", status_code=303)
    response.delete_cookie("user_type")
    response.delete_cookie("user_name")
    response.delete_cookie("user_email")
    response.delete_cookie("user_id")
    return response


# rota para criar conta de vendedor (opcional separada)
@app.get("/criar_conta_vendedor", response_class=HTMLResponse)
def criar_conta_vendedor_get(request: Request):
    return templates.TemplateResponse("criar_conta_vendedor.html", {"request": request, "error": ""})


@app.post("/criar_conta_vendedor")
def criar_conta_vendedor_post(request: Request, nome: str = Form(...), email: str = Form(...), senha: str = Form(...)):
    sucesso, erro = criar_conta_vendedor(nome, email, senha)
    if not sucesso:
        return templates.TemplateResponse("criar_conta_vendedor.html", {"request": request, "error": erro})
    return RedirectResponse("/home_vendedor", status_code=303)


# -----------------------
# LISTAGENS
# -----------------------
@app.get("/quartos_cliente", response_class=HTMLResponse)
def quartos_cliente_compat(request: Request, q: str = ""):
    # redireciona para a rota correta ou exibe a mesma página
    quartos = manager.get_all(filtro=q)
    return templates.TemplateResponse("listar_quartos_cliente.html", {"request": request, "quartos": quartos, "q": q})


@app.get("/listar_quartos_cliente", response_class=HTMLResponse)
def listar_quartos_cliente(request: Request, q: str = ""):
    # listagem para clientes (sem painel lateral / sem editar)
    quartos = manager.get_all(filtro=q)
    return templates.TemplateResponse("listar_quartos_cliente.html", {"request": request, "quartos": quartos, "q": q})


@app.get("/quartos", response_class=HTMLResponse)
def listar_quartos(request: Request, q: str = "", user_type: str | None = Cookie(default=None), user_id: str | None = Cookie(default=None)):
    # listagem principal: se for vendedor e tiver user_id, filtra pelos quartos daquele vendedor
    if user_type == "vendedor" and user_id:
        try:
            vendedor_id = int(user_id)
            quartos = manager.get_quartos_vendedor(vendedor_id=vendedor_id, filtro=q)
        except (ValueError, TypeError):
            quartos = manager.get_all(filtro=q)
    else:
        quartos = manager.get_all(filtro=q)

    resumo = manager.resumo() if user_type != "vendedor" else {}
    return templates.TemplateResponse("listar_quartos.html", {"request": request, "quartos": quartos, "q": q, **resumo})


# -----------------------
# ADD / DELETE / EDIT
# -----------------------
@app.get("/add", response_class=HTMLResponse)
def add_page(request: Request):
    return templates.TemplateResponse("add_quarto.html", {"request": request})


@app.post("/add")
def add_quarto(
    request: Request,
    codigo: str = Form(...),
    tipo: str = Form(...),
    preco_diaria: float = Form(...),
    user_type: str | None = Cookie(default=None),
    user_id: str | None = Cookie(default=None),
):
    vendedor_id = None
    if user_type == "vendedor" and user_id:
        try:
            vendedor_id = int(user_id)
        except ValueError:
            vendedor_id = None

    manager.add(codigo, tipo, preco_diaria, vendedor_id=vendedor_id)
    # se vendedor, volta para /quartos (filtrada), senão listar para cliente
    return RedirectResponse("/quartos" if user_type == "vendedor" else "/listar_quartos_cliente", status_code=303)


@app.get("/delete/{id}")
def delete_quarto(id: int):
    manager.delete(id)
    return RedirectResponse("/quartos", status_code=303)


@app.get("/editar/{id}", response_class=HTMLResponse)
def editar_page(id: int, request: Request):
    quarto = manager.get_by_id(id)
    if not quarto:
        return HTMLResponse(f"<h1>Quarto {id} não encontrado</h1>", status_code=404)
    return templates.TemplateResponse("editar_quarto.html", {"request": request, "quarto": quarto})


@app.post("/editar/{id}")
def editar_quarto(id: int, codigo: str = Form(...), tipo: str = Form(...), preco_diaria: float = Form(...), ocupado: str = Form(...)):
    quarto = Quarto(id=id, codigo=codigo, tipo=tipo, preco_diaria=preco_diaria, ocupado=(True if ocupado.lower() == "sim" else False))
    manager.update(quarto)
    return RedirectResponse("/quartos", status_code=303)


# -----------------------
# RESERVAS
# -----------------------
@app.get("/reservar/{id}", response_class=HTMLResponse)
def reservar_page(id: int, request: Request):
    quarto = manager.get_by_id(id)
    if not quarto:
        return HTMLResponse(f"<h1>Quarto {id} não encontrado</h1>", status_code=404)
    quarto_tipo = quarto.tipo or "anao"
    foto_url = f"/static/imagens/{quarto_tipo.lower()}.png"
    return templates.TemplateResponse("reservar_quarto.html", {"request": request, "quarto_id": id, "quarto_tipo": quarto_tipo, "foto_url": foto_url})


@app.post("/reservar/{id}")
def reservar_post(id: int, checkin: str = Form(...), checkout: str = Form(...), servicos: str = Form("")):
    quarto = manager.get_by_id(id)
    if quarto:
        quarto.reservar(checkin, checkout, servicos)
        manager.update(quarto)
    return RedirectResponse("/quartos", status_code=303)

@app.get("/listar_quartos_cliente", response_class=HTMLResponse)
def listar_quartos_cliente(request: Request, q: str = ""):
    quartos = manager.get_quartos(q)
    return templates.TemplateResponse(
        "listar_quartos_cliente.html",
        {"request": request, "quartos": quartos, "q": q}
    )


@app.post("/clientes/reservar/{id}")
def reservar_cliente_post(
    id: int,
    nome_cliente: str = Form(...),
    email_cliente: str = Form(...),
    checkin: str = Form(...),
    checkout: str = Form(...),
    observacoes: str = Form("")
):
    # grava a solicitação no banco como 'aguardando'
    manager.solicitar_reserva(id, checkin, checkout, observacoes)
    
    # redireciona para a listagem de quartos do cliente
    return RedirectResponse("/listar_quartos_cliente", status_code=303)

@app.get("/clientes/reservar/{id}", response_class=HTMLResponse)
def reservar_page(id: int, request: Request):
    quarto = manager.get_by_id(id)
    if not quarto:
        return HTMLResponse(f"<h1>Quarto {id} não encontrado</h1>", status_code=404)
    quarto_tipo = quarto.tipo or "anao"
    foto_url = f"/static/imagens/{quarto_tipo.lower()}.png"
    return templates.TemplateResponse("reserva_cliente.html", {"request": request, "quarto_id": id, "quarto_tipo": quarto_tipo, "foto_url": foto_url})


@app.get("/liberar/{id}")
def liberar_quarto(id: int):
    quarto = manager.get_by_id(id)
    if quarto:
        quarto.liberar()
        manager.update(quarto)
    return RedirectResponse("/quartos", status_code=303)


# -----------------------
# RELATÓRIO / DOWNLOAD
# -----------------------
@app.get("/relatorio", response_class=HTMLResponse)
def relatorio(request: Request):
    dados = manager.get_relatorio_quartos()
    return templates.TemplateResponse("relatorio.html", {"request": request, **dados})


@app.get("/relatorio/download")
def download_relatorio():
    dados = manager.get_relatorio_quartos()
    filename = "relatorio.csv"
    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f, delimiter=";")
        writer.writerow(["Métrica", "Valor"])
        writer.writerow(["Total de Quartos", dados["total_quartos"]])
        writer.writerow(["Quartos Livres", dados["quartos_livres"]])
        writer.writerow(["Quartos Ocupados", dados["quartos_ocupados"]])
        writer.writerow(["Valor Total em Reservas", f"R$ {dados['valor_total_reservas']}"])
        writer.writerow(["Valor Médio da Diária", f"R$ {round(dados['valor_medio_diaria'], 2)}"])
    return FileResponse(path=filename, filename=filename, media_type="text/csv")


# -----------------------
# DETALHES
# -----------------------
@app.get("/quarto/{id}", response_class=HTMLResponse)
def detalhes_quarto(id: int, request: Request):
    quarto = manager.get_quarto(id)
    if not quarto:
        return HTMLResponse("Quarto não encontrado", status_code=404)
    # seu manager.get_quarto pode retornar tuple ou objeto; aqui assumimos object com atributos
    quarto_tipo = quarto.tipo if hasattr(quarto, "tipo") else (quarto[2] if isinstance(quarto, (list, tuple)) else "anao")
    foto_url = f"/static/imagens/{quarto_tipo.lower()}.png"
    return templates.TemplateResponse("quarto_detalhes.html", {"request": request, "quarto": quarto, "quarto_tipo": quarto_tipo, "foto_url": foto_url})
