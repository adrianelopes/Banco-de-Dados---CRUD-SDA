from fastapi import FastAPI, Request, Form, Cookie
from fastapi.responses import HTMLResponse, RedirectResponse, FileResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from database import create_tables
from queries import QuartoManager, ReservaManager, autenticar, criar_conta, criar_conta_vendedor
from quarto import Quarto
from pathlib import Path
import csv
from datetime import date, datetime
from queries import ReservaManager

create_tables()

app = FastAPI()

templates_dir = Path(__file__).parent / "templates"
templates = Jinja2Templates(directory=str(templates_dir))

app.mount("/static", StaticFiles(directory=str(templates_dir)), name="static")

manager = QuartoManager()
reserva_manager = ReservaManager()

# -----------------------
# HOME / PÁGINAS INICIAIS
# -----------------------
@app.get("/")
def root(request: Request):
    user_type = request.cookies.get("user_type")

    if user_type == "vendedor":
        return RedirectResponse("/home_vendedor", status_code=302)
    elif user_type == "cliente":
        return RedirectResponse("/home_cliente", status_code=302)
    else:
        return RedirectResponse("/home_comum", status_code=302)

@app.get("/home_cliente", response_class=HTMLResponse)
def home_cliente(request: Request, user_name: str | None = Cookie(default=None)):
    quartos = manager.get_all()
    return templates.TemplateResponse("home_cliente.html", {"request": request, "quartos": quartos, "user_name": user_name})


@app.get("/home_vendedor", response_class=HTMLResponse)
def home_vendedor(request: Request, user_name: str | None = Cookie(default=None)):
    return templates.TemplateResponse("home_vendedor.html", {"request": request, "user_name": user_name})

@app.get("/home_comum", response_class=HTMLResponse)
def home_vendedor(request: Request, user_name: str | None = Cookie(default=None)):
    return templates.TemplateResponse("home_comum.html", {"request": request, "user_name": user_name})

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

        if tipo == "cliente":
            nome = dados.get("nome_cliente")
            user_id = dados.get("id_cliente")
            redirect_target = "/home_cliente"
        else:
            nome = dados.get("nome")
            user_id = dados.get("id_vendedor")
            redirect_target = "/home_vendedor"

        response = RedirectResponse(redirect_target, status_code=303)
        response.set_cookie(key="user_type", value=str(tipo))
        response.set_cookie(key="user_name", value=str(nome))
        response.set_cookie(key="user_email", value=str(email))
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
    tipo: str = Form("cliente")
):
    if tipo == "cliente":
        sucesso, erro, user_id = criar_conta(nome, email, senha)
        redirect_url = "/home_cliente"
    elif tipo == "vendedor":
        sucesso, erro, user_id = criar_conta_vendedor(nome, email, senha)
        redirect_url = "/home_vendedor"
    else:
        return templates.TemplateResponse("criar_conta.html", {"request": request, "error": "Tipo inválido", "tipo": tipo})

    if not sucesso:
        return templates.TemplateResponse("criar_conta.html", {"request": request, "error": erro, "tipo": tipo})

    response = RedirectResponse(redirect_url, status_code=303)
    response.set_cookie(key="user_type", value=str(tipo))
    response.set_cookie(key="user_name", value=str(nome))
    response.set_cookie(key="user_email", value=str(email))
    response.set_cookie(key="user_id", value=str(user_id))  
    return response


@app.get("/logout")
def logout():
    response = RedirectResponse("/", status_code=303)
    for cookie in ["user_type", "user_name", "user_email", "user_id"]:
        response.delete_cookie(cookie)
    return response


# -----------------------
# LISTAGENS
# -----------------------
# Página inicial do cliente
@app.get("/home_cliente", response_class=HTMLResponse)
def home_cliente(request: Request, user_name: str | None = Cookie(default=None)):
    quartos = manager.get_all()  # pega todos os quartos
    return templates.TemplateResponse(
        "home_cliente.html",
        {"request": request, "quartos": quartos, "user_name": user_name}
    )

# Listagem de quartos para cliente
@app.get("/listar_quartos_cliente", response_class=HTMLResponse)
def listar_quartos_cliente(request: Request, q: str = ""):
    quartos = manager.get_all(filtro=q)
    return templates.TemplateResponse(
        "listar_quartos_clientes.html",
        {"request": request, "quartos": quartos, "q": q}
    )

# Página para solicitar reserva do quarto (cliente)
@app.get("/clientes/reservar/{id}", response_class=HTMLResponse)
def reservar_page_cliente(id: int, request: Request):
    quarto = manager.get_by_id(id)
    if not quarto:
        return HTMLResponse(f"<h1>Quarto {id} não encontrado</h1>", status_code=404)
    quarto_tipo = quarto.tipo or "anao"
    foto_url = f"/static/imagens/{quarto_tipo.lower()}.png"
    return templates.TemplateResponse(
        "reserva_cliente.html",
        {"request": request, "quarto_id": id, "quarto_tipo": quarto_tipo, "foto_url": foto_url}
    )

# POST para solicitar reserva do cliente
@app.post("/clientes/reservar/{id}")
def reservar_cliente_post(
    id: int,
    nome_cliente: str = Form(...),
    email_cliente: str = Form(...),
    checkin: str = Form(...),
    checkout: str = Form(...),
    observacoes: str = Form("")
):
    manager.solicitar_reserva(id, checkin, checkout, observacoes)
    return RedirectResponse("/listar_quartos_cliente", status_code=303)

# Página inicial do vendedor
@app.get("/home_vendedor", response_class=HTMLResponse)
def home_vendedor(request: Request, user_name: str | None = Cookie(default=None)):
    return templates.TemplateResponse("home_vendedor.html", {"request": request, "user_name": user_name})

# Listagem de quartos com painel lateral (vendedor)
@app.get("/listar_quartos", response_class=HTMLResponse)
def listar_quartos(request: Request, q: str = "", user_type: str | None = Cookie(default=None), user_id: str | None = Cookie(default=None)):
    if user_type == "vendedor" and user_id:
        try:
            vendedor_id = int(user_id)
            quartos = manager.get_quartos_vendedor(vendedor_id=vendedor_id, filtro=q)
        except (ValueError, TypeError):
            quartos = manager.get_all(filtro=q)
    else:
        quartos = manager.get_all(filtro=q)

    resumo = manager.resumo() if user_type != "vendedor" else {}
    return templates.TemplateResponse(
        "listar_quartos.html",
        {"request": request, "quartos": quartos, "q": q, **resumo}
    )

# Página de reserva pelo vendedor
@app.get("/reservar/{id}", response_class=HTMLResponse)
def reservar_page_vendedor(id: int, request: Request):
    quarto = manager.get_by_id(id)
    reserva = reserva_manager.listar_reservas_quarto(quarto.id)  # ou get_reservas(quarto.id)
    reserva_ativa = any(
        r for r in reserva
        if r.autorizado and r.data_checkin <= date.today() <= r.data_checkout
    )
    aguardando_reserva = any(r for r in reserva if not r.autorizado and r.data_checkin <= date.today() <= r.data_checkout)

    # quarto está ocupado se houver pelo menos uma reserva ativa hoje
    quarto_tipo = quarto.tipo or "anao"
    foto_url = f"/static/imagens/{quarto_tipo.lower()}.png"

    return templates.TemplateResponse(
        "reserva_quarto.html",
        {
            "request": request,
            "quarto_id": quarto.id,
            "quarto_tipo": quarto_tipo,
            "foto_url": foto_url,
            "reserva_ativa": reserva_ativa,
            "aguardando_reserva": aguardando_reserva
        }
    )

# POST para reserva pelo vendedor
@app.post("/reservar/{id}")
def reservar_post_vendedor(
    id: int,
    checkin: str = Form(...),
    checkout: str = Form(...),
    servicos: str = Form("")
):
    quarto = manager.get_by_id(id)
    if not quarto:
        return RedirectResponse("/listar_quartos", status_code=303)

    # Converter datas de string para datetime, se necessário
    checkin_dt = datetime.strptime(checkin, "%Y-%m-%d")
    checkout_dt = datetime.strptime(checkout, "%Y-%m-%d")

    # Criar uma nova reserva
    reserva_manager.criar_reserva(
        id_quarto=id,
        id_cliente=None,
        checkin=checkin_dt,
        checkout=checkout_dt
    )

    reserva_manager.autorizar_reserva(id)

    return RedirectResponse("/listar_quartos", status_code=303)
# -----------------------
# ADD / DELETE / EDIT
# -----------------------
@app.get("/add", response_class=HTMLResponse)
def add_page(request: Request):
    return templates.TemplateResponse("add_quarto.html", {"request": request})


@app.post("/add")
def add_quarto(request: Request, codigo: str = Form(...), tipo: str = Form(...), preco_diaria: float = Form(...), user_type: str | None = Cookie(default=None), user_id: str | None = Cookie(default=None)):
    vendedor_id = int(user_id) if user_type == "vendedor" and user_id else None
    manager.add(codigo, tipo, preco_diaria, vendedor_id=vendedor_id)
    return RedirectResponse("/listar_quartos", status_code=303)


@app.get("/delete/{id}")
def delete_quarto(id: int):
    manager.delete(id)
    return RedirectResponse("/listar_quartos", status_code=303)


@app.get("/editar/{id}", response_class=HTMLResponse)
def editar_page(id: int, request: Request):
    quarto = manager.get_by_id(id)
    if not quarto:
        return HTMLResponse(f"<h1>Quarto {id} não encontrado</h1>", status_code=404)
    return templates.TemplateResponse("editar_quarto.html", {"request": request, "quarto": quarto})


@app.post("/editar/{id}")
def editar_quarto(id: int, codigo: str = Form(...), tipo: str = Form(...), preco_diaria: float = Form(...), status: str = Form(...)):
    quarto = Quarto(id=id, codigo=codigo, tipo=tipo, preco_diaria=preco_diaria, status=status)
    manager.update(quarto)
    return RedirectResponse("/listar_quartos", status_code=303)


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
def reservar_post(id: int, checkin: str = Form(...), checkout: str = Form(...), id_cliente: int = Form(...)):
    reserva_manager.criar_reserva(id_quarto=id, id_cliente=id_cliente, checkin=checkin, checkout=checkout)
    return RedirectResponse("/listar_quartos", status_code=303)


@app.get("/clientes/reservar/{id}", response_class=HTMLResponse)
def reservar_page(id: int, request: Request):
    quarto = manager.get_by_id(id)
    reserva = reserva_manager.listar_reservas_quarto(quarto.id)  # ou get_reservas(quarto.id)
    reserva_ativa = any(r for r in reserva if r.autorizado and r.data_checkin <= date.today() <= r.data_checkout)
    aguardando_reserva = any(r for r in reserva if not r.autorizado and r.data_checkin <= date.today() <= r.data_checkout)

    if not quarto:
        return HTMLResponse(f"<h1>Quarto {id} não encontrado</h1>", status_code=404)
    
    quarto_tipo = quarto.tipo if hasattr(quarto, "tipo") else "anao"
    foto_url = f"/static/imagens/{quarto_tipo.lower()}.png"
    return templates.TemplateResponse(
        "reserva_cliente.html",
        {
            "request": request,
            "quarto_id": id,
            "quarto_tipo": quarto_tipo,
            "foto_url": foto_url,
            "reserva_ativa": reserva_ativa,
            "aguardando_reserva": aguardando_reserva
        }
    )

@app.post("/clientes/reservar/{id}")
def reservar_cliente_post(
    request: Request,
    id: int,
    nome_cliente: str = Form(...),
    email_cliente: str = Form(...),
    checkin: str = Form(...),
    checkout: str = Form(...),
    observacoes: str = Form("")
):
    # transformar datas de string para date
    data_checkin = datetime.strptime(checkin, "%Y-%m-%d").date()
    data_checkout = datetime.strptime(checkout, "%Y-%m-%d").date()

    user_id = request.cookies.get("user_id")
    if not user_id:
        return RedirectResponse("/login", status_code=303)

    # criar reserva pendente
    reserva_id = reserva_manager.criar_reserva(
        id_quarto=id,
        id_cliente=int(user_id),  # você pode pegar o id do cliente via cookie ou outro método
        checkin=data_checkin,
        checkout=data_checkout
    )

    # opcional: salvar observações
    if observacoes:
        # atualizar campo servicos/observacoes se houver na tabela reserva
        pass

    # redireciona para a listagem de quartos do cliente
    return RedirectResponse("/listar_quartos_cliente", status_code=303)

# -----------------------
# RELATÓRIO / DOWNLOAD
# -----------------------
@app.get("/relatorio", response_class=HTMLResponse)
def relatorio(request: Request):
    # usa o relatório atualizado que calcula ocupação a partir de reservas
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

@app.get("/quarto/{id}", response_class=HTMLResponse)
def detalhes_quarto(id: int, request: Request):
    # pegar o quarto
    quarto = manager.get_quarto(id)
    if not quarto:
        return HTMLResponse("Quarto não encontrado", status_code=404)

    # pegar reservas autorizadas do quarto
    reservas = reserva_manager.listar_reservas_quarto(id)
    reservas_ativas = [
        r for r in reservas
        if r.autorizado and r.data_checkin <= date.today() <= r.data_checkout
    ]

    # quarto está ocupado se houver pelo menos uma reserva ativa hoje
    quarto_ocupado = len(reservas_ativas) > 0

    # se quiser mostrar nome do cliente em cada reserva ativa
    for r in reservas_ativas:
        # supondo que r tenha atributo cliente_id, você pode buscar o nome do cliente
        r.cliente_nome = r.cliente_nome if hasattr(r, "cliente_nome") else "Cliente"

    quarto_tipo = quarto.tipo if hasattr(quarto, "tipo") else "anao"
    foto_url = f"/static/imagens/{quarto_tipo.lower()}.png"

    return templates.TemplateResponse(
        "quartos_detalhe.html",
        {
            "request": request,
            "quarto": quarto,
            "quarto_ocupado": quarto_ocupado,
            "reservas_ativas": reservas_ativas,
            "foto_url": foto_url,
            "quarto_tipo": quarto_tipo
        }
    )
