from werkzeug.security import check_password_hash
from database.connection import Database
from models.administradora import Administradora


class AdminRepository:
    def __init__(self, db: Database):
        self.db = db

    def buscar_por_email(self, email: str) -> Administradora | None:
        conn = self.db.get_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute(
                "SELECT idAdmin, email, senhaHash, nome FROM administradora WHERE email = %s",
                (email.strip().lower(),),
            )
            row = cursor.fetchone()
            if not row:
                return None
            return Administradora(
                id_admin=row["idAdmin"],
                email=row["email"],
                senha_hash=row["senhaHash"],
                nome=row["nome"],
            )
        finally:
            cursor.close()
            conn.close()

    def autenticar(self, email: str, senha: str) -> Administradora | None:
        admin = self.buscar_por_email(email)
        if not admin:
            return None
        if not check_password_hash(admin.senha_hash, senha):
            return None
        return admin