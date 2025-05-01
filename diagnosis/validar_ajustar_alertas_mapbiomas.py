# path: src/diagnosis/validar_ajustar_alertas_mapbiomas.py

import pandas as pd
import os

# Caminho do arquivo CSV
csv_path = "data/downloads/alertas_mapbiomas.csv"

# --- Diagnosticar e Ajustar


def validar_csv(caminho_csv):
    print(f"Analisando arquivo: {caminho_csv}\n")

    file_size = os.path.getsize(caminho_csv) / (1024 * 1024)
    print(f"Tamanho do arquivo: {file_size:.2f} MB\n")

    # Testar diferentes separadores
    separadores = [',', ';', '\t', '|']

    for sep in separadores:
        try:
            print(f"Tentando separador: '{sep}'...")
            df = pd.read_csv(caminho_csv, sep=sep, nrows=100, engine='python')
            if df.shape[1] > 1:
                print(
                    f"Separador '{sep}' parece correto! ({df.shape[1]} colunas detectadas)")
                print(df.head())

                # Agora ler tudo com separador correto
                df_full = pd.read_csv(caminho_csv, sep=sep, engine='python')

                # Salvar CSV corrigido
                output_path = "data/generated/alertas_mapbiomas_corrigido.csv"
                os.makedirs("data/generated", exist_ok=True)
                df_full.to_csv(output_path, index=False)

                print(f"\n✅ CSV corrigido salvo em: {output_path}")
                return
        except Exception as e:
            print(f"Erro com separador '{sep}': {e}\n")

    print("\n❗ Não foi possível identificar separador correto.")


def test_format(caminho_csv):
    with open(caminho_csv, 'r', encoding='utf-8', errors='ignore') as f:
        conteudo = f.read(2000)  # ler primeiros 2000 caracteres

    print(conteudo)


if __name__ == "__main__":
    # validar_csv(csv_path)
    test_format(csv_path)
