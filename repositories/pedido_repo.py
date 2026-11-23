from database.connection import Database
from models.pedido import Pedido, ItemPedido
from models.cliente import Cliente

class PedidoRepository:
    def __init__(self, db: Database):
        self.db = db

    def salvar_pedido_completo(self, pedido: Pedido) -> Pedido:
        conn = self.db.get_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            conn.start_transaction()

            # 1. Validar preços reais e quantidade mínima direto do banco
            itens_validados = []
            for item in pedido.itens:
                cursor.execute(
                    "SELECT idProduto, nome, precoUnitario, quantidadeMinima FROM produto WHERE idProduto = %s AND ativo = 1",
                    (item.id_produto,)
                )
                prod_db = cursor.fetchone()
                if not prod_db:
                    raise ValueError(f"Produto ID {item.id_produto} não encontrado ou inativo.")
                if item.qtd_produtos < prod_db["quantidadeMinima"]:
                    raise ValueError(
                        f"Quantidade mínima para '{prod_db['nome']}' é {prod_db['quantidadeMinima']}."
                    )
                itens_validados.append(
                    ItemPedido(
                        id_produto=prod_db["idProduto"],
                        qtd_produtos=item.qtd_produtos,
                        valor_unitario=float(prod_db["precoUnitario"]),
                        codigo_pedido=pedido.codigo,
                        nome_produto=prod_db["nome"]
                    )
                )

            pedido.itens = itens_validados
            pedido.total_pedido = pedido.calcular_total()

            # 2. Inserir Cliente
            sql_cliente = """
                INSERT INTO cliente (codigoPedido, rua, bairro, numero, cep, cidade, complemento, nome, telefone)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            c = pedido.cliente
            cursor.execute(sql_cliente, (
                pedido.codigo, c.rua, c.bairro, c.numero,
                c.cep, c.cidade, c.complemento, c.nome, c.telefone
            ))
            c.id_endereco = cursor.lastrowid

            # 3. Inserir Pedido
            sql_pedido = """
                INSERT INTO pedido (codigo, totalPedido, idCliente, dataEntrega, horarioEntrega)
                VALUES (%s, %s, %s, %s, %s)
            """
            cursor.execute(sql_pedido, (
                pedido.codigo, pedido.total_pedido, c.id_endereco,
                pedido.data_entrega, pedido.horario_entrega
            ))

            # 4. Inserir Itens do Pedido
            sql_item = """
                INSERT INTO item_pedido (codigoPedido, idProduto, qtdProdutos, valorUnitario)
                VALUES (%s, %s, %s, %s)
            """
            for item in pedido.itens:
                cursor.execute(sql_item, (
                    pedido.codigo, item.id_produto, item.qtd_produtos, item.valor_unitario
                ))

            # 5. Inserir Status Inicial
            sql_status = "INSERT INTO status (situacao, pedido_codigo) VALUES (%s, %s)"
            cursor.execute(sql_status, ("Recebido", pedido.codigo))

            conn.commit()
            return pedido

        except Exception as e:
            conn.rollback()
            raise e
        finally:
            cursor.close()
            conn.close()

    def buscar_por_codigo(self, codigo: int) -> dict | None:
        conn = self.db.get_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            sql = """
                SELECT p.codigo, p.totalPedido, p.dataEntrega, p.horarioEntrega,
                       s.situacao, s.atualizadoEm,
                       c.nome AS clienteNome, c.telefone, c.rua, c.numero, c.bairro, c.cidade, c.complemento, c.cep
                FROM pedido p
                INNER JOIN status s ON s.pedido_codigo = p.codigo
                INNER JOIN cliente c ON c.idendereco = p.idCliente
                WHERE p.codigo = %s
            """
            cursor.execute(sql, (codigo,))
            row = cursor.fetchone()
            if not row:
                return None

            cursor.execute("""
                SELECT ip.idProduto, pr.nome, ip.qtdProdutos, ip.valorUnitario
                FROM item_pedido ip
                INNER JOIN produto pr ON pr.idProduto = ip.idProduto
                WHERE ip.codigoPedido = %s
            """, (codigo,))
            itens = cursor.fetchall()

            return {
                "codigo": row["codigo"],
                "totalPedido": float(row["totalPedido"]),
                "dataEntrega": str(row["dataEntrega"]),
                "horarioEntrega": str(row["horarioEntrega"]),
                "situacao": row["situacao"],
                "atualizadoEm": str(row["atualizadoEm"]),
                "cliente": {
                    "nome": row["clienteNome"],
                    "telefone": row["telefone"],
                    "endereco": f"{row['rua']}, {row['numero']} - {row['bairro']}, {row['cidade']} (CEP: {row['cep']})",
                    "complemento": row["complemento"]
                },
                "itens": [
                    {
                        "idProduto": i["idProduto"],
                        "nome": i["nome"],
                        "qtdProdutos": i["qtdProdutos"],
                        "valorUnitario": float(i["valorUnitario"])
                    } for i in itens
                ]
            }
        finally:
            cursor.close()
            conn.close()

    def listar_todos_admin(self) -> list[dict]:
        conn = self.db.get_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute("SELECT codigo FROM pedido ORDER BY dataEntrega DESC, horarioEntrega DESC")
            codigos = [r["codigo"] for r in cursor.fetchall()]
            return [self.buscar_por_codigo(cod) for cod in codigos]
        finally:
            cursor.close()
            conn.close()

    def atualizar_status(self, codigo: int, nova_situacao: str) -> bool:
        conn = self.db.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                "UPDATE status SET situacao = %s WHERE pedido_codigo = %s",
                (nova_situacao, codigo)
            )
            conn.commit()
            return cursor.rowcount > 0
        finally:
            cursor.close()
            conn.close()