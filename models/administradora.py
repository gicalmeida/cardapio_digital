class Administradora:
    def __init__(self, email: str, senha_hash: str, nome: str = "", id_admin: int = None):
        self.id_admin = id_admin
        self.email = email
        self.senha_hash = senha_hash
        self.nome = nome

    def to_dict(self) -> dict:
        return {
            "idAdmin": self.id_admin,
            "email": self.email,
            "nome": self.nome,
        }