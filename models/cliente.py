# models/cliente.py
class Cliente:
    def __init__(self, nome: str, telefone: str, rua: str, bairro: str,
                 numero: int, cep: int, cidade: str, complemento: str = "",
                 id_endereco: int = None, codigo_pedido: int = None):
        self.id_endereco = id_endereco
        self.codigo_pedido = codigo_pedido
        self.nome = nome
        self.telefone = telefone
        self.rua = rua
        self.bairro = bairro
        self.numero = int(numero)
        self.cep = int(str(cep).replace("-", "").strip())
        self.cidade = cidade
        self.complemento = complemento

    def to_dict(self) -> dict:
        return {
            "idendereco": self.id_endereco,
            "nome": self.nome,
            "telefone": self.telefone,
            "rua": self.rua,
            "bairro": self.bairro,
            "numero": self.numero,
            "cep": self.cep,
            "cidade": self.cidade,
            "complemento": self.complemento
        }