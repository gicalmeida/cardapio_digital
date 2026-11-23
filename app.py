from flask import Flask, jsonify
from flask_cors import CORS
from database.connection import Database
from repositories.admin_repo import AdminRepository
from repositories.produto_repo import ProdutoRepository
from repositories.pedido_repo import PedidoRepository
from services.codigo_service import CodigoService
from routes.auth_routes import criar_auth_blueprint
from routes.produto_routes import criar_produto_blueprint
from routes.pedido_routes import criar_pedido_blueprint


class AplicacaoCardapio:
    def __init__(self):
        self.app = Flask(__name__)
        CORS(self.app, resources={r"/api/*": {"origins": "*"}})

        self.db = Database()
        self.codigo_service = CodigoService(self.db)

        self.admin_repo = AdminRepository(self.db)
        self.produto_repo = ProdutoRepository(self.db)
        self.pedido_repo = PedidoRepository(self.db)

        self._registrar_rotas()
        self._registrar_erros()

    def _registrar_rotas(self):
        self.app.register_blueprint(criar_auth_blueprint(self.admin_repo))
        self.app.register_blueprint(criar_produto_blueprint(self.produto_repo))
        self.app.register_blueprint(criar_pedido_blueprint(self.pedido_repo, self.codigo_service))

        @self.app.get("/api/rotas")
        def listar_rotas():
            return jsonify(sorted([str(r) for r in self.app.url_map.iter_rules()])), 200

    def _registrar_erros(self):
        @self.app.errorhandler(404)
        def nao_encontrado(e):
            return jsonify({"erro": "Rota não encontrada."}), 404

        @self.app.errorhandler(500)
        def erro_interno(e):
            return jsonify({"erro": "Erro interno no servidor."}), 500

    def rodar(self, host: str = "0.0.0.0", port: int = 5000, debug: bool = True):
        self.app.run(host=host, port=port, debug=debug)


aplicacao = AplicacaoCardapio()
app = aplicacao.app

if __name__ == "__main__":
    aplicacao.rodar()