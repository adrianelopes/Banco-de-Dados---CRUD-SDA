from fastapi import FastAPI, Request, Form, Cookie
from fastapi.responses import HTMLResponse, RedirectResponse, FileResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from pathlib import Path
import csv
from datetime import date, datetime

from database import create_tables
from queries import QuartoManager, ReservaManager, autenticar, criar_conta, criar_conta_vendedor
from quarto import Quarto

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
def home_comum(request: Request, user_name: str | None = Cookie(default=None)):
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
            nome = dados.get("nome_vendedor")
            user_id = dados.get("id_vendedor")
            redirect_target = "/home_vendedor"

        response = RedirectResponse(redirect_target, status_code=303)
        response.set_cookie("user_type", tipo)
        response.set_cookie("user_name", nome)
        response.set_cookie("user_email", email)
        response.set_cookie("user_id", str(user_id))
        return response

    return templates.TemplateResponse("login.html", {"request": request, "error": "Email ou senha incorretos"})


@app.get("/criar_conta", response_class=HTMLResponse)
def criar_conta_get(request: Request, tipo: str = "cliente"):
    return templaees.TemplateResponse("criar_conta.html", {"request": request, "error": "", "tipo": tipo})


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
    response.set_cookie("user_type", tipo)
    response.set_cookie("user_name", nome)
    response.set_cookie("user_email", email)
    response.set_cookie("user_id", str(user_id))
    return response


@app.get("/logout")
def logout():
    response = RedirectResponse("/", status_code=303)
    for cookie in ["user_type", "user_name", "user_email", "user_id"]:
        response.delete_cookie(cookie)
    return response


# -----------------------
# CRUD QUARTOS
# -----------------------
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

    return templates.TemplateResponse("listar_quartos.html", {"request": request, "quartos": quartos, "q": q})

# Listagem de quartos para cliente
@app.get("/listar_quartos_cliente", response_class=HTMLResponse)
def listar_quartos_cliente(request: Request, q: str = ""):
    quartos = manager.get_all(filtro=q)
    return templates.TemplateResponse(
        "listar_quartos_clientes.html",
        {"request": request, "quartos": quartos, "q": q}
    )

@app.get("/add", response_class=HTMLResponse)
def add_page(request: Request):
    return templates.TemplateResponse("add_quarto.html", {"request": request})


@app.post("/add")
def add_quarto(request: Request, codigo: str = Form(...), tipo: str = Form(...), preco_diaria: float = Form(...),
               user_type: str | None = Cookie(default=None), user_id: str | None = Cookie(default=None)):
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
def editar_quarto(id: int, codigo: str = Form(...), tipo: str = Form(...), preco_diaria: float = Form(...)):
    quarto = Quarto(id=id, codigo=codigo, tipo=tipo, preco_diaria=preco_diaria)
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
    
    # buscar reservas autorizadas para mostrar como bloqueadas
    reservas = reserva_manager.listar_reservas_quarto(id)
    bloqueios = [
        {
            "checkin": r['data_checkin'].strftime("%d/%m/%Y"),
            "checkout": r['data_checkout'].strftime("%d/%m/%Y")
        }
        for r in reservas
    ]

    quarto_tipo = quarto.tipo if hasattr(quarto, "tipo") else "anao"
    foto_url = f"/static/imagens/{quarto_tipo.lower()}.png"

    return templates.TemplateResponse(
        "reservar_quarto.html",
        {
            "request": request,
            "quarto_id": id,
            "quarto_tipo": quarto_tipo,
            "foto_url": foto_url,
            "bloqueios": bloqueios  # lista de períodos bloqueados
        }
    )


@app.post("/reservar/{id}")
def reservar_post(id: int, checkin: str = Form(...), checkout: str = Form(...), user_id: str | None = Cookie(default=None)):
    if not user_id:
        return RedirectResponse("/login", status_code=303)

    data_checkin = datetime.strptime(checkin, "%Y-%m-%d").date()
    data_checkout = datetime.strptime(checkout, "%Y-%m-%d").date()

    # Buscar reservas existentes para este quarto
    reservas = reserva_manager.listar_reservas_quarto(id)

    if reservas:
        # Verificar conflito de datas
        conflito = any(
            (res["data_checkin"] <= data_checkout and res["data_checkout"] >= data_checkin)
            for res in reservas
        )

        if conflito:
            # Redireciona para a listagem com aviso de conflito
            return RedirectResponse(f"/listar_quartos_cliente?erro=Data de reserva coincide com outra reserva", status_code=303)

    # Se não houver conflito, cria a reserva
    reserva_manager.criar_reserva(
        id_quarto=id,
        id_cliente=int(user_id),
        checkin=data_checkin,
        checkout=data_checkout
    )

    return RedirectResponse("/listar_quartos_cliente", status_code=303)
    

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

# Página para o cliente ver suas reservas
@app.get("/minhas_reservas", response_class=HTMLResponse)
def minhas_reservas(request: Request, user_id: str | None = Cookie(default=None), user_type: str | None = Cookie(default=None)):
    if not user_id or user_type != "cliente":
        return RedirectResponse("/login", status_code=303)
    
    reservas = reserva_manager.listar_reservas_cliente(int(user_id))

    for r in reservas:
        # Se vier RealDictRow, convertendo para objeto dinâmico
        data_checkin = r['data_checkin']
        data_checkout = r['data_checkout']

        quarto = manager.get_by_id(r["id_quarto"])  # pega o objeto Quarto completo
        r.quarto_nome = f"{quarto.codigo} ({quarto.tipo})" if quarto else f"Quarto {r.id_quarto}"
        r.data_checkin_str = data_checkin.strftime("%d/%m/%Y")
        r.data_checkout_str = data_checkout.strftime("%d/%m/%Y")
        r.status = "Autorizada" if getattr(r, "autorizado", r['autorizado']) else "Pendente"

    return templates.TemplateResponse(
        "minhas_reservas.html",
        {"request": request, "reservas": reservas}
    )
