#!/usr/bin/env python3
"""
Teste de carregamento dos dados IDHM
"""

import os
import sys

import pandas as pd

sys.path.append(os.path.join(os.path.dirname(__file__), "src"))


def test_idhm_loading():
    print("=" * 60)
    print("TESTE DE CARREGAMENTO DOS DADOS IDHM")
    print("=" * 60)

    # Carregar arquivo IDHM
    arquivo_idhm = "data/raw/idhm_municipios_serra_penitente.xlsx"
    df_idhm = pd.read_excel(arquivo_idhm)

    print(f"Shape original: {df_idhm.shape}")
    print(f"Colunas: {df_idhm.columns.tolist()[:10]}...")  # Primeiras 10 colunas
    print(f"Territorialidades: {df_idhm['Territorialidades'].tolist()}")

    # Filtrar municípios
    municipios_completos = ["Alto Parnaíba (MA)", "Balsas (MA)", "Tasso Fragoso (MA)"]
    df_municipios = df_idhm[df_idhm["Territorialidades"].isin(municipios_completos)].copy()

    print(f"\nMunicípios filtrados: {len(df_municipios)}")
    print(f"Municípios encontrados: {df_municipios['Territorialidades'].tolist()}")

    # Verificar colunas IDHM específicas
    colunas_idhm = [
        "IDHM 2000",
        "IDHM 2010",
        "IDHM Renda 2000",
        "IDHM Renda 2010",
        "IDHM Educação 2000",
        "IDHM Educação 2010",
        "IDHM Longevidade 2000",
        "IDHM Longevidade 2010",
    ]

    print(f"\nColunas IDHM disponíveis: {[col for col in colunas_idhm if col in df_idhm.columns]}")

    # Mostrar dados dos municípios
    for municipio in municipios_completos:
        if municipio in df_municipios["Territorialidades"].values:
            dados_mun = df_municipios[df_municipios["Territorialidades"] == municipio]
            print(f"\n--- {municipio} ---")
            for col in colunas_idhm:
                if col in dados_mun.columns:
                    valor = dados_mun[col].iloc[0]
                    print(f"{col}: {valor}")

    # Testar processamento manual
    print("\n" + "=" * 60)
    print("TESTE DE PROCESSAMENTO MANUAL")
    print("=" * 60)

    dados_processados = []

    for _, row in df_municipios.iterrows():
        municipio_nome = row["Territorialidades"].replace(" (MA)", "")

        # Dados para 2000
        if not pd.isna(row.get("IDHM 2000")):
            dados_processados.append(
                {
                    "municipio": municipio_nome,
                    "ano": 2000,
                    "idhm_": row.get("IDHM 2000"),
                    "idhm_renda": row.get("IDHM Renda 2000"),
                    "idhm_educação": row.get("IDHM Educação 2000"),
                    "idhm_longevidade": row.get("IDHM Longevidade 2000"),
                }
            )

        # Dados para 2010
        if not pd.isna(row.get("IDHM 2010")):
            dados_processados.append(
                {
                    "municipio": municipio_nome,
                    "ano": 2010,
                    "idhm_": row.get("IDHM 2010"),
                    "idhm_renda": row.get("IDHM Renda 2010"),
                    "idhm_educação": row.get("IDHM Educação 2010"),
                    "idhm_longevidade": row.get("IDHM Longevidade 2010"),
                }
            )

    print(f"Dados processados: {len(dados_processados)} registros")

    if dados_processados:
        df_processado = pd.DataFrame(dados_processados)
        print("\nDataFrame processado:")
        print(df_processado)

        # Salvar para verificação
        df_processado.to_csv("test_idhm_output.csv", index=False)
        print("\nDados salvos em: test_idhm_output.csv")
    else:
        print("ERRO: Nenhum dado foi processado!")


if __name__ == "__main__":
    test_idhm_loading()
