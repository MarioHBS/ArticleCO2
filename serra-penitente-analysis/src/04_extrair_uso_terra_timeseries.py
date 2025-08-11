# src/04_extrair_uso_terra_timeseries.py
# -*- coding: utf-8 -*-
"""Script para extração de séries temporais de uso da terra.

Este script processa dados históricos de uso e cobertura da terra do MapBiomas
para os municípios da Serra do Penitente, gerando séries temporais detalhadas
por categoria de uso da terra para análise de mudanças ao longo do tempo.
"""

import logging
import os
import sys

import pandas as pd

from variaveis import GENERATED_PATHS, INPUT_PATHS

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

RAW_EXCEL = INPUT_PATHS.mapbiomas
PARTIAL_OUT = GENERATED_PATHS.uso_timeseries_csv
SHEET_NAME = "COVERAGE_9"
# Alto Parnaíba, Balsas, Tasso Fragoso
SERRA_CODES = [2100501, 2101400, 2112001]


def load_coverage_excel(fp: str, sheet_name: str = SHEET_NAME) -> pd.DataFrame:
    """Carrega dados de cobertura do solo do arquivo Excel do MapBiomas."""
    try:
        if not os.path.exists(fp):
            raise FileNotFoundError(f"Arquivo não encontrado: {fp}")

        logging.info(f"Carregando dados de cobertura de: {fp}")
        df = pd.read_excel(fp, sheet_name=sheet_name)

        if df.empty:
            raise ValueError(f"Arquivo está vazio: {fp}")

        logging.info(f"Dados carregados: {df.shape[0]} registros, {df.shape[1]} colunas")

        df = df.rename(columns={
            'geocode': 'codigo_ibge',
            'municipality': 'municipio',
            'class': 'uso'
        })

        # Verificar colunas essenciais
        required_cols = ['codigo_ibge', 'municipio', 'uso']
        missing_cols = [col for col in required_cols if col not in df.columns]
        if missing_cols:
            logging.warning(f"Colunas ausentes após renomeação: {missing_cols}")

        return df

    except FileNotFoundError:
        logging.error(f"Arquivo não encontrado: {fp}")
        raise
    except Exception as e:
        logging.error(f"Erro ao carregar arquivo Excel: {str(e)}")
        raise


def transform_long(df: pd.DataFrame) -> pd.DataFrame:
    """
    Transforma de “largura” para “longo”:
    Cada linha = um município + uso + ano + área (ha e km2)
    """
    # detecta colunas-numéricas (anos)
    year_cols = [c for c in df.columns if isinstance(c, (int, float))]
    id_vars = ['codigo_ibge', 'municipio', 'uso']
    df_long = df.melt(
        id_vars=id_vars,
        value_vars=year_cols,
        var_name='year',
        value_name='area_ha'
    )
    df_long['year'] = df_long['year'].astype(int)
    df_long['area_ha'] = df_long['area_ha'].astype(float)
    # 1 hectare = 0.01 km²
    df_long['area_km2'] = df_long['area_ha'] * 0.01
    return df_long


def filter_municipalities(df: pd.DataFrame, codes: list[int]) -> pd.DataFrame:
    """Filtra apenas os municípios de Serra do Penitente."""
    return df[df['codigo_ibge'].isin(codes)].reset_index(drop=True)


def summarize_by_use_year(df: pd.DataFrame) -> pd.DataFrame:
    """
    Agrega por município, uso e ano, somando áreas.
    Retorna DataFrame com colunas:
      codigo_ibge, municipio, year, uso, area_ha, area_km2
    """
    summary = (
        df
        .groupby(
            ['codigo_ibge', 'municipio', 'year', 'uso'],
            as_index=False
        )[['area_ha', 'area_km2']]
        .sum()
    )
    return summary


def save_partial(df: pd.DataFrame, out_fp: str):
    """Salva o CSV parcial em data/generated."""
    try:
        os.makedirs(os.path.dirname(out_fp), exist_ok=True)
        df.to_csv(out_fp, index=False, encoding='utf-8-sig')
        logging.info(f"CSV de uso da terra salvo com sucesso: {out_fp} ({len(df)} registros)")
    except Exception as e:
        logging.error(f"Erro ao salvar CSV: {str(e)}")
        raise


def main():
    # Configurar logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s"
    )

    try:
        logging.info("Iniciando extração de séries temporais de uso da terra")

        # 1) Carrega o Excel bruto
        df_raw = load_coverage_excel(RAW_EXCEL)

        # 2) Transforma em formato longo
        logging.info("Transformando dados para formato longo")
        df_long = transform_long(df_raw)
        logging.info(f"Dados transformados: {len(df_long)} registros")

        # 3) Filtra apenas Serra do Penitente
        logging.info(f"Filtrando municípios da Serra do Penitente: {SERRA_CODES}")
        df_serra = filter_municipalities(df_long, SERRA_CODES)
        logging.info(f"Dados filtrados: {len(df_serra)} registros")

        # 4) Agrega por município, uso e ano
        logging.info("Agregando dados por município, uso e ano")
        df_summary = summarize_by_use_year(df_serra)
        logging.info(f"Dados agregados: {len(df_summary)} registros únicos")

        # 5) Salva parcial
        save_partial(df_summary, PARTIAL_OUT)

        logging.info("Extração de séries temporais concluída com sucesso")

    except Exception as e:
        logging.error(f"Erro durante a extração de séries temporais: {str(e)}")
        raise


if __name__ == "__main__":
    main()
