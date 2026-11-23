# models/pedido.py
from models.cliente import Cliente


class ItemPedido:
    def __init__(
        self,
        id_produto: int,
        qtd_produtos: int,
        valor_unitario: float,
        codigo_pedido: int = None,
        nome_produto: str = None,
    ):
        self.codigo_pedido = codigo_pedido
        self.id_produto = int(id_produto)
        self.qtd_produtos = int(qtd_produtos)
        self.valor_unitario = float(valor_unitario)
        self.nome_produto = nome_produto

    @property
    def subtotal(self) -> float:
        return round(self.qtd_produtos * self.valor_unitario, 2)

    def to_dict(self) -> dict:
        return {
            "idProduto": self.id_produto,
            "nome": self.nome_produto,
            "qtdProdutos": self.qtd_produtos,
            "valorUnitario": self.valor_unitario,
            "subtotal": self.subtotal,
        }


class Pedido:
    def __init__(
        self,
        codigo: int,
        cliente: Cliente,
        itens: list[ItemPedido],
        data_entrega: str,
        horario_entrega: str,
        situacao: str = "Recebido",
    ):
        self.codigo = codigo
        self.cliente = cliente
        self.itens = itens
        self.data_entrega = data_entrega
        self.horario_entrega = horario_entrega
        self.situacao = situacao
        self.total_pedido = self.calcular_total()

    def calcular_total(self) -> float:
        return round(sum(item.subtotal for item in self.itens), 2)

    def to_dict(self) -> dict:
        return {
            "codigo": self.codigo,
            "totalPedido": self.total_pedido,
            "dataEntrega": str(self.data_entrega),
            "horarioEntrega": str(self.horario_entrega),
            "situacao": self.situacao,
            "cliente": self.cliente.to_dict(),
            "itens": [item.to_dict() for item in self.itens],
        }