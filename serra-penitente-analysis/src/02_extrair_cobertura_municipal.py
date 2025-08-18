# src/02_extrair_cobertura_municipal.py
"""Script para extração de dados de cobertura do solo municipal.

Este script processa dados de cobertura do solo do MapBiomas para os municípios
da região da Serra do Penitente, extraindo estatísticas de cobertura por bioma
a partir da planilha COVERAGE_9 do arquivo MapBiomas.
"""

import logging
import os
import sys

import pandas as pd
from variaveis import GENERATED_PATHS, INPUT_PATHS

sys.path.append(os.path.dirname(os.path.abspath(__file__)))


def load_mapbiomas_data(arquivo_path: str) -> pd.DataFrame:
    """
    Carrega dados de cobertura do MapBiomas.
    """
    try:
        if not os.path.exists(arquivo_path):
            raise FileNotFoundError(f"Arquivo não encontrado: {arquivo_path}")

        logging.info(f"Carregando dados MapBiomas de: {arquivo_path}")
        df = pd.read_excel(
            arquivo_path,
            sheet_name="COVERAGE_9",
            dtype={"geocode": str},
        )

        if df.empty:
            raise ValueError(f"Arquivo está vazio: {arquivo_path}")

        logging.info(f"Dados carregados: {df.shape[0]} registros, {df.shape[1]} colunas")
        return df

    except FileNotFoundError:
        logging.exception(f"Arquivo não encontrado: {arquivo_path}")
        raise
    except Exception as e:
        logging.exception(f"Erro ao carregar dados MapBiomas: {e!s}")
        raise


def rename_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Renomeia colunas para padrão do pipeline.
    """
    df_renamed = df.rename(columns={
        "geocode": "codigo_ibge",
        "municipality": "municipio",
        "state": "uf",
        "biome": "bioma",
        "class": "classe_codigo",
        "class_level_0": "classe_level_0",
        "class_level_1": "classe_level_1",
        "class_level_2": "classe_level_2",
    })

    # Verificar colunas essenciais
    required_cols = ["codigo_ibge", "municipio", "bioma"]
    missing_cols = [col for col in required_cols if col not in df_renamed.columns]
    if missing_cols:
        logging.warning(f"Colunas ausentes após renomeação: {missing_cols}")

    return df_renamed


def get_year_columns(df: pd.DataFrame) -> list:
    """
    Identifica colunas de ano dinamicamente.
    """
    anos = [
        col for col in df.columns
        if (isinstance(col, str) and col.isdigit()) or isinstance(col, int)
    ]
    min_year = "N/A" if not anos else min(anos)
    max_year = "N/A" if not anos else max(anos)
    logging.info(f"Colunas de ano identificadas: {len(anos)} anos ({min_year}-{max_year})")
    return anos


def filter_municipalities(df: pd.DataFrame, municipios_alvo: list) -> pd.DataFrame:
    """
    Filtra apenas municípios de interesse.
    """
    df_filtered = df[df["codigo_ibge"].isin(municipios_alvo)].copy()
    logging.info(
        f"Dados filtrados: {len(df_filtered)} registros para {len(municipios_alvo)} municípios",
    )
    return df_filtered


def convert_year_columns(df: pd.DataFrame, anos: list) -> pd.DataFrame:
    """
    Converte colunas de ano para numérico.
    """
    df_converted = df.copy()
    for col in anos:
        df_converted[col] = pd.to_numeric(df_converted[col], errors="coerce")
    logging.info(f"Colunas de ano convertidas para numérico: {len(anos)} colunas")
    return df_converted


def transform_to_long_format(df: pd.DataFrame, anos: list) -> pd.DataFrame:
    """
    Transforma para formato longo.
    """
    id_vars = [
        "codigo_ibge", "municipio", "uf", "bioma",
        "classe_codigo", "classe_level_0",
        "classe_level_1", "classe_level_2",
    ]

    df_long = df.melt(
        id_vars=id_vars,
        value_vars=anos,
        var_name="ano",
        value_name="cobertura",
    )

    # Converte ano para string (padrão do pipeline)
    df_long["ano"] = df_long["ano"].astype(str)

    # Ordena dados
    df_long = df_long.sort_values(["codigo_ibge", "bioma", "classe_codigo", "ano"])

    logging.info(f"Dados transformados para formato longo: {len(df_long)} registros")
    return df_long


def save_data(df: pd.DataFrame, output_path: str):
    """
    Salva dados em CSV.
    """
    try:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        df.to_csv(output_path, index=False)
        logging.info(
            f"CSV de cobertura MapBiomas salvo: {output_path} "
            f"({len(df)} registros)",
        )
    except Exception as e:
        logging.exception(f"Erro ao salvar CSV: {e!s}")
        raise


def main():
    # Configurar logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
    )

    try:
        logging.info("Iniciando extração de dados de cobertura municipal")

        # Lista de códigos IBGE dos municípios de Serra do Penitente
        municipios_alvo = ["2100501", "2101400", "2112001"]

        # 1) Carrega dados
        df_mapb = load_mapbiomas_data(INPUT_PATHS.mapbiomas)

        # 2) Renomeia colunas
        df_mapb = rename_columns(df_mapb)

        # 3) Identifica colunas de ano
        anos = get_year_columns(df_mapb)

        # 4) Filtra municípios
        df_mapb = filter_municipalities(df_mapb, municipios_alvo)

        # 5) Converte colunas de ano
        df_mapb = convert_year_columns(df_mapb, anos)

        # 6) Transforma para formato longo
        df_long = transform_to_long_format(df_mapb, anos)

        # 7) Salva dados
        save_data(df_long, GENERATED_PATHS.mapbiomas_long_csv)

        logging.info("Extração de dados de cobertura concluída com sucesso")

    except Exception as e:
        logging.exception(f"Erro durante a extração de cobertura: {e!s}")
        raise


if __name__ == "__main__":
    main()
