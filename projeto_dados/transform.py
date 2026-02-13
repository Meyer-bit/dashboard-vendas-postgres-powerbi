import os
import ast
import pandas as pd


class Transformer:
    """
    Camada analitica:
    - Le vendas e produtos normalizados (parquet)
    - Explode itens de cada venda
    - Faz merge com dimensao de produtos
    - Calcula receita
    - Gera sales_fact.parquet para carga no banco
    """

    def __init__(self, input_dir, output_dir):
        self.input_dir = input_dir
        self.output_dir = output_dir

        # Caminhos fixos esperados na camada processed.
        self.sales_path = os.path.join(input_dir, "sales_raw.parquet")
        self.products_path = os.path.join(input_dir, "products_raw.parquet")

        # Arquivo final da camada analytics.
        self.output_path = os.path.join(output_dir, "sales_fact.parquet")

        os.makedirs(output_dir, exist_ok=True)

    def load_sales_data(self):
        """Le vendas, transforma data e explode a lista de produtos por venda."""
        if not os.path.exists(self.sales_path):
            raise FileNotFoundError(f"Arquivo nao encontrado: {self.sales_path}")

        sales_df = pd.read_parquet(self.sales_path)

        # Converte data ISO para coluna de data (sem hora) para uso no BI.
        sales_df["sale_date"] = pd.to_datetime(sales_df["date"], utc=True).dt.date

        # O campo products veio como texto representando lista de dicts.
        sales_df["products"] = sales_df["products"].apply(ast.literal_eval)

        # Uma venda pode ter varios produtos: explode gera uma linha por item.
        sales_df = sales_df.explode("products")

        # Extrai product_id e quantity de cada item explodido.
        sales_df["product_id"] = sales_df["products"].apply(lambda item: item["productId"])
        sales_df["quantity"] = sales_df["products"].apply(lambda item: item["quantity"])

        # Remove colunas tecnicas e padroniza nomes da fato.
        sales_df = sales_df.drop(columns=["products", "__v", "date"], errors="ignore")
        sales_df = sales_df.rename(columns={"id": "sale_id", "userId": "user_id"})

        return sales_df

    def load_products_data(self):
        """Le produtos e seleciona colunas necessarias para enriquecer a fato."""
        if not os.path.exists(self.products_path):
            raise FileNotFoundError(f"Arquivo nao encontrado: {self.products_path}")

        products_df = pd.read_parquet(self.products_path)

        required_columns = ["id", "title", "category", "price"]
        missing_columns = [col for col in required_columns if col not in products_df.columns]

        if missing_columns:
            raise ValueError(f"Colunas ausentes em products_raw.parquet: {missing_columns}")

        products_df = products_df[required_columns].rename(
            columns={
                "id": "product_id",
                "title": "product_title",
                "price": "unit_price",
            }
        )

        return products_df

    def build_sales_fact(self, sales_df, products_df):
        """Faz merge vendas x produtos e calcula a metrica de receita."""
        fact_df = sales_df.merge(products_df, on="product_id", how="left")

        # Ajusta nulos para nao quebrar carga e manter leitura no BI.
        fact_df["product_title"] = fact_df["product_title"].fillna("Unknown product")
        fact_df["category"] = fact_df["category"].fillna("Unknown category")

        # Garante tipos numericos antes do calculo de receita.
        fact_df["quantity"] = pd.to_numeric(fact_df["quantity"], errors="coerce").fillna(0).astype("int64")
        fact_df["unit_price"] = pd.to_numeric(fact_df["unit_price"], errors="coerce").fillna(0.0)

        # Receita por linha da fato (item vendido).
        fact_df["revenue"] = fact_df["quantity"] * fact_df["unit_price"]

        # Ordem final de colunas para manter padrao no load SQL.
        fact_df = fact_df[
            [
                "sale_id",
                "user_id",
                "sale_date",
                "product_id",
                "product_title",
                "category",
                "quantity",
                "unit_price",
                "revenue",
            ]
        ]

        return fact_df

    def run(self):
        """Executa a transformacao completa e salva a tabela fato em parquet."""
        sales_df = self.load_sales_data()
        products_df = self.load_products_data()
        fact_df = self.build_sales_fact(sales_df, products_df)

        fact_df.to_parquet(self.output_path, index=False)
        print(f"Dados transformados salvos em {self.output_path}")


if __name__ == "__main__":
    transformer = Transformer(input_dir="data/processed", output_dir="data/analytics")
    transformer.run()
