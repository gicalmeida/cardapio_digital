import random
from database.connection import Database

class CodigoService:
    def __init__(self, db: Database):
        self.db = db

    def gerar_codigo_unico(self) -> int:
        conn = self.db.get_connection()
        cursor = conn.cursor()
        try:
            while True:
                # Gera inteiro aleatório entre 100000 e 999999
                candidato = random.randint(100000, 999999)
                cursor.execute("SELECT 1 FROM pedido WHERE codigo = %s", (candidato,))
                if cursor.fetchone() is None:
                    return candidato
        finally:
            cursor.close()
            conn.close()