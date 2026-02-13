import os
import requests
import pandas as pd

# Endpoint de vendas (carts): traz usuario, data e lista de itens (productId + quantity)
CARTS_ENDPOINT = "https://fakestoreapi.com/carts"

# Endpoint de produtos: traz preco, categoria e titulo de cada produto
PRODUCTS_ENDPOINT = "https://fakestoreapi.com/products"

# Caminhos de saida da camada raw
RAW_DIR = "data/raw"
SALES_OUTPUT_PATH = os.path.join(RAW_DIR, "sales_raw.csv")
PRODUCTS_OUTPUT_PATH = os.path.join(RAW_DIR, "products_raw.csv")


def extract_data(endpoint):
    """Faz uma chamada HTTP para a API e devolve JSON (lista de dicts)."""
    try:
        response = requests.get(endpoint, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.ConnectionError as exc:
        print(f"Erro de conexao: {exc}")
        return None
    except requests.exceptions.Timeout as exc:
        print(f"Timeout: {exc}")
        return None
    except requests.exceptions.RequestException as exc:
        print(f"Erro inesperado: {exc}")
        return None


def save_dataframe(data, output_path, dataset_name):
    """Converte JSON para DataFrame e salva em CSV."""
    df = pd.DataFrame(data)
    df.to_csv(output_path, index=False)
    print(f"{dataset_name}: {len(df)} linhas salvas em {output_path}")


if __name__ == "__main__":
    # Garante que a pasta raw existe antes de salvar arquivos.
    os.makedirs(RAW_DIR, exist_ok=True)

    print("Extraindo vendas (carts)...")
    sales_data = extract_data(CARTS_ENDPOINT)

    print("Extraindo produtos...")
    products_data = extract_data(PRODUCTS_ENDPOINT)

    # Se algum dataset falhar, encerra para evitar pipeline inconsistente.
    if not sales_data or not products_data:
        print("Falha na extracao. Verifique API e conexao.")
        raise SystemExit(1)

    # Salva as duas fontes que serao usadas nas proximas etapas.
    save_dataframe(sales_data, SALES_OUTPUT_PATH, "Vendas")
    save_dataframe(products_data, PRODUCTS_OUTPUT_PATH, "Produtos")

    print("Extracao concluida.")
