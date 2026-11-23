from database.connection import Database
from models.produto import Produto


class ProdutoRepository:
    def __init__(self, db: Database):
        self.db = db

    def listar_ativos(self) -> list[dict]:
        conn = self.db.get_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute(
                """
                SELECT idProduto, nome, precoUnitario, quantidadeMinima, descricao, imagemUrl, ativo
                FROM produto
                WHERE ativo = 1
                ORDER BY idProduto DESC
                """
            )
            rows = cursor.fetchall()
            return [
                Produto(
                    id_produto=r["idProduto"],
                    nome=r["nome"],
                    preco_unitario=r["precoUnitario"],
                    quantidade_minima=r["quantidadeMinima"],
                    descricao=r["descricao"] or "",
                    imagem_url=r["imagemUrl"],
                    ativo=r["ativo"],
                ).to_dict()
                for r in rows
            ]
        finally:
            cursor.close()
            conn.close()

    def criar(self, produto: Produto) -> dict:
        conn = self.db.get_connection()
        cursor = conn.cursor()
        try:
            sql = """
                INSERT INTO produto (nome, precoUnitario, quantidadeMinima, descricao, imagemUrl, ativo)
                VALUES (%s, %s, %s, %s, %s, 1)
            """
            cursor.execute(
                sql,
                (
                    produto.nome.strip(),
                    produto.preco_unitario,
                    produto.quantidade_minima,
                    produto.descricao.strip(),
                    produto.imagem_url,
                ),
            )
            conn.commit()
            produto.id_produto = cursor.lastrowid
            produto.ativo = 1
            return produto.to_dict()
        finally:
            cursor.close()
            conn.close()

    def atualizar(self, id_produto: int, produto: Produto) -> bool:
        conn = self.db.get_connection()
        cursor = conn.cursor()
        try:
            sql = """
                UPDATE produto
                SET nome = %s,
                    precoUnitario = %s,
                    quantidadeMinima = %s,
                    descricao = %s,
                    imagemUrl = %s
                WHERE idProduto = %s AND ativo = 1
            """
            cursor.execute(
                sql,
                (
                    produto.nome.strip(),
                    produto.preco_unitario,
                    produto.quantidade_minima,
                    produto.descricao.strip(),
                    produto.imagem_url,
                    id_produto,
                ),
            )
            conn.commit()
            return cursor.rowcount > 0
        finally:
            cursor.close()
            conn.close()

    def excluir_logico(self, id_produto: int) -> bool:
        conn = self.db.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("UPDATE produto SET ativo = 0 WHERE idProduto = %s", (id_produto,))
            conn.commit()
            return cursor.rowcount > 0
        finally:
            cursor.close()
            conn.close()