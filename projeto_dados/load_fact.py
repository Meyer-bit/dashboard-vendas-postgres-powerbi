import os
import pandas as pd
import psycopg
from dotenv import load_dotenv


# Carrega variaveis do arquivo .env (DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD)
load_dotenv()

DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")


def get_connection():
    """Abre conexao com PostgreSQL usando variaveis de ambiente."""
    return psycopg.connect(
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
    )


def recreate_sales_fact_table():
    """
    Recria a tabela fato para garantir schema coerente com o parquet analitico.
    """
    ddl_sql = """
    DROP TABLE IF EXISTS sales_fact;

    CREATE TABLE sales_fact (
        sale_id BIGINT,
        user_id BIGINT,
        sale_date DATE,
        product_id BIGINT,
        product_title TEXT,
        category TEXT,
        quantity BIGINT,
        unit_price DOUBLE PRECISION,
        revenue DOUBLE PRECISION
    );
    """

    conn = get_connection()
    cur = conn.cursor()
    cur.execute(ddl_sql)
    conn.commit()
    cur.close()
    conn.close()


def load_sales_fact():
    """Le sales_fact.parquet da camada analytics e insere no PostgreSQL."""
    parquet_path = "data/analytics/sales_fact.parquet"
    fact_df = pd.read_parquet(parquet_path)

    # Converte NaN para None para evitar problemas de adaptacao no psycopg.
    fact_df = fact_df.where(pd.notna(fact_df), None)

    insert_sql = """
        INSERT INTO sales_fact (
            sale_id,
            user_id,
            sale_date,
            product_id,
            product_title,
            category,
            quantity,
            unit_price,
            revenue
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
    """

    conn = get_connection()
    cur = conn.cursor()

    for _, row in fact_df.iterrows():
        cur.execute(
            insert_sql,
            (
                row["sale_id"],
                row["user_id"],
                row["sale_date"],
                row["product_id"],
                row["product_title"],
                row["category"],
                row["quantity"],
                row["unit_price"],
                row["revenue"],
            ),
        )

    conn.commit()
    cur.close()
    conn.close()


if __name__ == "__main__":
    print("Recriando tabela sales_fact...")
    recreate_sales_fact_table()

    print("Carregando dados analiticos no banco...")
    load_sales_fact()

    print("Carga concluida com sucesso!")
