from flask import Blueprint, request, jsonify
from repositories.admin_repo import AdminRepository
from services.auth_service import AuthService


def criar_auth_blueprint(admin_repo: AdminRepository) -> Blueprint:
    auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")

    @auth_bp.post("/login")
    def login():
        data = request.get_json(silent=True) or {}
        email = data.get("email", "")
        senha = data.get("senha", "")

        if not email or not senha:
            return jsonify({"erro": "E-mail e senha são obrigatórios."}), 400

        admin = admin_repo.autenticar(email, senha)
        if not admin:
            return jsonify({"erro": "E-mail ou senha inválidos."}), 401

        token = AuthService.gerar_token(admin.id_admin, admin.email)
        return jsonify({
            "token": token,
            "admin": admin.to_dict(),
        }), 200

    return auth_bp