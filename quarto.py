class Quarto:
    def __init__(self, id: int, codigo: str, tipo: str, preco_diaria: float,
                 ocupado: bool = False, checkin: str = None,
                 checkout: str = None, servicos: str = None):
        self.id = id
        self.codigo = codigo
        self.tipo = tipo
        self.preco_diaria = preco_diaria
        self.ocupado = ocupado
        self.checkin = checkin
        self.checkout = checkout
        self.servicos = servicos

    def reservar(self, checkin: str, checkout: str, servicos: str):
        self.ocupado = True
        self.checkin = checkin
        self.checkout = checkout
        self.servicos = servicos

    def liberar(self):
        self.ocupado = False
        self.checkin = None
        self.checkout = None
        self.servicos = None

    def __repr__(self):
        return f"<Quarto {self.codigo} - {self.tipo} - {'Ocupado' if self.ocupado else 'Livre'}>"

    def get_quarto(self, quarto_id):
        conn = sqlite3.connect("banco.db")
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM quartos WHERE id = ?", (quarto_id,))
        quarto = cursor.fetchone()
        conn.close()
        return quarto
