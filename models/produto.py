# models/produto.py
class Produto:
    def __init__(self, nome: str, preco_unitario: float, quantidade_minima: int = 1,
                 descricao: str = "", imagem_url: str = None, id_produto: int = None, ativo: int = 1):
        self.id_produto = id_produto
        self.nome = nome
        self.preco_unitario = float(preco_unitario)
        self.quantidade_minima = int(quantidade_minima)
        self.descricao = descricao
        self.imagem_url = imagem_url
        self.ativo = ativo

    def to_dict(self) -> dict:
        return {
            "idProduto": self.id_produto,
            "nome": self.nome,
            "precoUnitario": self.preco_unitario,
            "quantidadeMinima": self.quantidade_minima,
            "descricao": self.descricao,
            "imagemUrl": self.imagem_url,
            "ativo": bool(self.ativo)
        }