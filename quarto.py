from typing import Optional, Any


class Quarto:
    def __init__(
        self,
        id: Optional[int] = None,
        codigo: Optional[str] = "",
        tipo: Optional[str] = "",
        preco_diaria: Optional[Any] = 0.0,  # aceita Decimal, float ou str
        vendedor_id: Optional[int] = None,
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

        self.vendedor_id = vendedor_id

    # Métodos auxiliares
    def __repr__(self):
        return f"<Quarto id={self.id} codigo={self.codigo} tipo={self.tipo} preco={self.preco_diaria} vendedor_id={self.vendedor_id}>"

    def to_dict(self):
        return {
            "id": self.id,
            "codigo": self.codigo,
            "tipo": self.tipo,
            "preco_diaria": self.preco_diaria,
            "vendedor_id": self.vendedor_id,
        }
