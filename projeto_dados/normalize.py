import os
import pandas as pd


class Normalizer:
    """
    Camada de normalizacao:
    - Le arquivos raw (CSV/JSON)
    - Remove duplicatas
    - Salva em Parquet na pasta processed
    """

    def __init__(self, input_dir, output_dir):
        self.input_dir = input_dir
        self.output_dir = output_dir

        # Garante que a pasta de saida exista.
        os.makedirs(output_dir, exist_ok=True)

    def load_df_from_file(self, file_name, ext):
        """Le um arquivo raw e retorna DataFrame (ou None para extensao nao suportada)."""
        input_path = os.path.join(self.input_dir, file_name)

        if ext.lower() == ".csv":
            return pd.read_csv(input_path)

        if ext.lower() == ".json":
            try:
                return pd.read_json(input_path)
            except ValueError:
                # Suporta JSON lines caso o JSON nao esteja em array unico.
                return pd.read_json(input_path, lines=True)

        return None

    def normalize_data(self):
        """Normaliza todos os arquivos da pasta raw para parquet em processed."""
        for file_name in os.listdir(self.input_dir):
            name, ext = os.path.splitext(file_name)
            df = self.load_df_from_file(file_name, ext)

            # Ignora arquivos que nao forem CSV/JSON.
            if df is None:
                continue

            # Limpeza minima para evitar duplicidade no pipeline.
            df = df.drop_duplicates().reset_index(drop=True)

            output_path = os.path.join(self.output_dir, f"{name}.parquet")
            df.to_parquet(output_path, index=False)
            print(f"Arquivo {file_name} processado com sucesso e salvo em {output_path}")


if __name__ == "__main__":
    normalizer = Normalizer(input_dir="data/raw", output_dir="data/processed")
    normalizer.normalize_data()
