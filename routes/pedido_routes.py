from flask import Blueprint, request, jsonify
from config import Config
from models.cliente import Cliente
from models.pedido import Pedido, ItemPedido
from repositories.pedido_repo import PedidoRepository
from services.codigo_service import CodigoService
from services.auth_service import AuthService


def criar_pedido_blueprint(pedido_repo: PedidoRepository, codigo_service: CodigoService) -> Blueprint:
    pedido_bp = Blueprint("pedidos", __name__, url_prefix="/api")

    @pedido_bp.post("/pedidos")
    def finalizar_pedido():
        data = request.get_json(silent=True) or {}
        cliente_data = data.get("cliente") or {}
        itens_data = data.get("itens") or []

        campos_cliente = ["nome", "telefone", "rua", "bairro", "numero", "cep", "cidade"]
        for campo in campos_cliente:
            if not cliente_data.get(campo):
                return jsonify({"erro": f"Campo do cliente obrigatório: {campo}"}), 400

        if not data.get("dataEntrega") or not data.get("horarioEntrega"):
            return jsonify({"erro": "Data e horário de entrega são obrigatórios."}), 400

        if not itens_data:
            return jsonify({"erro": "O carrinho está vazio."}), 400

        try:
            cliente = Cliente(
                nome=cliente_data["nome"],
                telefone=cliente_data["telefone"],
                rua=cliente_data["rua"],
                bairro=cliente_data["bairro"],
                numero=int(cliente_data["numero"]),
                cep=cliente_data["cep"],
                cidade=cliente_data["cidade"],
                complemento=cliente_data.get("complemento", ""),
            )

            itens = [
                ItemPedido(
                    id_produto=int(item["idProduto"]),
                    qtd_produtos=int(item["qtdProdutos"]),
                    valor_unitario=float(item.get("valorUnitario", 0)),
                )
                for item in itens_data
            ]

            codigo_unico = codigo_service.gerar_codigo_unico()
            pedido = Pedido(
                codigo=codigo_unico,
                cliente=cliente,
                itens=itens,
                data_entrega=data["dataEntrega"],
                horario_entrega=data["horarioEntrega"],
                situacao="Recebido",
            )

            salvo = pedido_repo.salvar_pedido_completo(pedido)
            return jsonify({
                "mensagem": "Pedido registrado com sucesso!",
                "whatsappAdmin": Config.WHATSAPP_ADMIN,
                "pedido": salvo.to_dict(),
            }), 201

        except ValueError as e:
            return jsonify({"erro": str(e)}), 400
        except Exception as e:
            return jsonify({"erro": f"Erro interno ao salvar pedido: {str(e)}"}), 500

    @pedido_bp.get("/pedidos/<int:codigo>")
    def consultar_pedido(codigo: int):
        pedido = pedido_repo.buscar_por_codigo(codigo)
        if not pedido:
            return jsonify({"erro": "Pedido não encontrado para o código informado."}), 404

        # Retorno público focado no acompanhamento do pedido
        return jsonify({
            "codigo": pedido["codigo"],
            "situacao": pedido["situacao"],
            "dataEntrega": pedido["dataEntrega"],
            "horarioEntrega": pedido["horarioEntrega"],
            "totalPedido": pedido["totalPedido"],
            "atualizadoEm": pedido["atualizadoEm"],
            "itens": pedido["itens"],
        }), 200

    @pedido_bp.get("/admin/pedidos")
    @AuthService.admin_required
    def listar_pedidos_admin():
        pedidos = pedido_repo.listar_todos_admin()
        return jsonify(pedidos), 200

    @pedido_bp.patch("/admin/pedidos/<int:codigo>/status")
    @AuthService.admin_required
    def atualizar_status_pedido(codigo: int):
        data = request.get_json(silent=True) or {}
        nova_situacao = (data.get("situacao") or "").strip()

        status_permitidos = {"Recebido", "Em Preparo", "Saiu para Entrega", "Entregue", "Cancelado"}
        if nova_situacao not in status_permitidos:
            return jsonify({"erro": "Status inválido."}), 400

        ok = pedido_repo.atualizar_status(codigo, nova_situacao)
        if not ok:
            return jsonify({"erro": "Pedido não encontrado."}), 404

        return jsonify({"mensagem": "Status atualizado com sucesso.", "situacao": nova_situacao}), 200

    return pedido_bp