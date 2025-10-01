from typing import Optional, Any
from datetime import date

class Quarto:
    def __init__(
        self,
        id: Optional[int] = None,
        codigo: Optional[str] = "",
        tipo: Optional[str] = "",
        preco_diaria: Optional[Any] = 0.0,  # aceita Decimal ou float ou str
        ocupado: bool = False,
        checkin: Optional[str] = None,
        checkout: Optional[str] = None,
        servicos: Optional[str] = None,
        vendedor_id: Optional[int] = None,
        status: Optional[str] = None
    ):
        self.id = id
        self.codigo = codigo
        self.tipo = tipo

        
        try:
            if preco_diaria is None:
                self.preco_diaria = 0.0
            else:
                self.preco_diaria = float(preco_diaria)
        except (TypeError, ValueError):
            self.preco_diaria = 0.0

        self.ocupado = bool(ocupado)
        self.status = "ocupado" if ocupado else "livre"
        self.checkin = checkin
        self.checkout = checkout
        self.servicos = servicos
        self.vendedor_id = vendedor_id

    def reservar(self, checkin: str, checkout: str, servicos: str = ""):
        self.ocupado = True
        self.status = "ocupado"
        self.checkin = checkin
        self.checkout = checkout
        self.servicos = servicos

    def liberar(self):
        self.ocupado = False
        self.status = "livre"
        self.checkin = None
        self.checkout = None
        self.servicos = None

    def __repr__(self):
        status = "Ocupado" if self.ocupado else "Livre"
        return f"<Quarto id={self.id} codigo={self.codigo} tipo={self.tipo} preco={self.preco_diaria} {status} vendedor_id={self.vendedor_id}>"
