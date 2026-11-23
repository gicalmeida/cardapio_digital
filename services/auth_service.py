# services/auth_service.py
from functools import wraps
from datetime import datetime, timedelta, timezone
import jwt
from flask import request, jsonify
from config import Config

class AuthService:
    @staticmethod
    def gerar_token(admin_id: int, email: str) -> str:
        payload = {
            "sub": str(admin_id),
            "email": email,
            "role": "admin",
            "exp": datetime.now(timezone.utc) + timedelta(hours=8)
        }
        return jwt.encode(payload, Config.JWT_SECRET_KEY, algorithm="HS256")

    @staticmethod
    def admin_required(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            auth_header = request.headers.get("Authorization", "")
            if not auth_header.startswith("Bearer "):
                return jsonify({"erro": "Token de autenticação ausente."}), 401

            token = auth_header.split(" ")[1]
            try:
                payload = jwt.decode(token, Config.JWT_SECRET_KEY, algorithms=["HS256"])
                if payload.get("role") != "admin":
                    return jsonify({"erro": "Acesso negado."}), 403
            except jwt.ExpiredSignatureError:
                return jsonify({"erro": "Sessão expirada. Faça login novamente."}), 401
            except jwt.InvalidTokenError:
                return jsonify({"erro": "Token inválido."}), 401

            return f(*args, **kwargs)
        return decorated