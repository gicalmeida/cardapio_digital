import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_PORT = int(os.getenv("DB_PORT", "3306"))
    DB_USER = os.getenv("DB_USER", "root")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "051224")
    DB_NAME = os.getenv("DB_NAME", "cardapio_digital")
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "chave_troque_em_producao")
    WHATSAPP_ADMIN = os.getenv("WHATSAPP_ADMIN", "5511955552894")