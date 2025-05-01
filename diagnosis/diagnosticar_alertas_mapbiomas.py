# path: src/diagnosis/diagnosticar_alertas_mapbiomas.py

import pandas as pd
import os

# Caminho do arquivo CSV
csv_path = "data/downloads/alertas_mapbiomas.csv"

# --- Diagnóstico do arquivo


def diagnosticar_csv2(caminho_csv):
    df = pd.read_csv(caminho_csv, sep=',', engine='python')

    print(df.columns.tolist())
    print(df.head())
    print(df.shape)


def diagnosticar_csv(caminho_csv):
    print(f"Analisando o arquivo: {caminho_csv}\n")

    # Verifica o tamanho do arquivo
    file_size = os.path.getsize(caminho_csv) / (1024 * 1024)
    print(f"Tamanho do arquivo: {file_size:.2f} MB")

    # Tenta ler os primeiros bytes
    with open(caminho_csv, 'r', encoding='utf-8', errors='ignore') as f:
        primeiras_linhas = [next(f) for _ in range(10)]

    print("\nPrimeiras 10 linhas do arquivo:")
    for linha in primeiras_linhas:
        print(linha.strip())

    # Tenta detectar separador
    print("\nTentando detectar separador...")
    separadores = [',', ';', '\t', '|']
    for sep in separadores:
        try:
            df = pd.read_csv(caminho_csv, sep=sep, nrows=5)
            if df.shape[1] > 1:
                print(
                    f"Separador detectado como: '{sep}' ({df.shape[1]} colunas)")
                print(df.head())
                return sep
        except Exception as e:
            print(f"Erro com separador '{sep}': {e}")

    print("\nNenhum separador detectado claramente. Pode ser arquivo corrompido ou não ser CSV.")
    return None


if __name__ == "__main__":
    diagnosticar_csv2(csv_path)
