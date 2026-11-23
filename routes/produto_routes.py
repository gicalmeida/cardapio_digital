from flask import Blueprint, request, jsonify
from models.produto import Produto
from repositories.produto_repo import ProdutoRepository
from services.auth_service import AuthService


def criar_produto_blueprint(produto_repo: ProdutoRepository) -> Blueprint:
    produto_bp = Blueprint("produtos", __name__, url_prefix="/api/produtos")

    @produto_bp.get("")
    def listar_produtos():
        produtos = produto_repo.listar_ativos()
        return jsonify(produtos), 200

    @produto_bp.post("")
    @AuthService.admin_required
    def criar_produto():
        data = request.get_json(silent=True) or {}
        try:
            nome = data.get("nome", "").strip()
            preco = data.get("precoUnitario")
            qtd_min = data.get("quantidadeMinima", 1)
            descricao = data.get("descricao", "")
            imagem_url = data.get("imagemUrl")

            if not nome or preco is None or float(preco) <= 0:
                return jsonify({"erro": "Nome e preço unitário válido são obrigatórios."}), 400

            novo = Produto(
                nome=nome,
                preco_unitario=float(preco),
                quantidade_minima=int(qtd_min),
                descricao=descricao,
                imagem_url=imagem_url,
            )
            criado = produto_repo.criar(novo)
            return jsonify(criado), 201
        except (ValueError, TypeError) as e:
            return jsonify({"erro": f"Dados inválidos: {str(e)}"}), 400

    @produto_bp.put("/<int:id_produto>")
    @AuthService.admin_required
    def editar_produto(id_produto: int):
        data = request.get_json(silent=True) or {}
        try:
            produto_atualizado = Produto(
                nome=data["nome"],
                preco_unitario=float(data["precoUnitario"]),
                quantidade_minima=int(data.get("quantidadeMinima", 1)),
                descricao=data.get("descricao", ""),
                imagem_url=data.get("imagemUrl"),
                id_produto=id_produto,
            )
            ok = produto_repo.atualizar(id_produto, produto_atualizado)
            if not ok:
                return jsonify({"erro": "Produto não encontrado."}), 404
            return jsonify({"mensagem": "Produto atualizado com sucesso."}), 200
        except (KeyError, ValueError, TypeError):
            return jsonify({"erro": "Campos obrigatórios ausentes ou inválidos."}), 400

    @produto_bp.delete("/<int:id_produto>")
    @AuthService.admin_required
    def excluir_produto(id_produto: int):
        ok = produto_repo.excluir_logico(id_produto)
        if not ok:
            return jsonify({"erro": "Produto não encontrado."}), 404
        return jsonify({"mensagem": "Produto removido da vitrine com sucesso."}), 200

    return produto_bp