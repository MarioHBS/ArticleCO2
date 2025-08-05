# src/01_extrair_pib_municipal.py
# -*- coding: utf-8 -*-
"""
Script para extração e processamento de dados do PIB municipal.

Este script processa dados do PIB municipal do IBGE para os municípios
da região da Serra do Penitente, consolidando informações de diferentes
períodos (2002-2009 e 2010-2021) em um único dataset padronizado.
"""
import os
import argparse
import logging
from pathlib import Path

import pandas as pd
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from variaveis import INPUT_PATHS, GENERATED_PATHS, MUNICIPIOS
from validacao import validate_pib_schema, check_data_integrity


def load_pib(path: Path) -> pd.DataFrame:
    """
    Carrega planilha de PIB (XLS ou XLSX), renomeia colunas dinamicamente
    e retorna DataFrame com ['codigo_ibge','municipio','ano','pib'].
    """
    try:
        if not path.exists():
            raise FileNotFoundError(f"Arquivo não encontrado: {path}")
        
        logging.info(f"Carregando arquivo PIB: {path}")
        engine = "xlrd" if path.suffix.lower() == ".xls" else "openpyxl"
        df = pd.read_excel(path, engine=engine)
        
        if df.empty:
            raise ValueError(f"Arquivo PIB está vazio: {path}")
        
        logging.info(f"Arquivo carregado com {len(df)} linhas e {len(df.columns)} colunas")

        # Detecta colunas conforme cabeçalhos reais
        try:
            code_col = next(
                c for c in df.columns if "Código" in c and "Município" in c)
            name_col = next(c for c in df.columns if "Nome" in c and "Município" in c)
            year_col = next(c for c in df.columns if c.strip().lower() == "ano")
            pib_col = next(c for c in df.columns if "Produto Interno Bruto" in c)
        except StopIteration as e:
            logging.error(f"Colunas esperadas não encontradas no arquivo {path}")
            logging.error(f"Colunas disponíveis: {list(df.columns)}")
            raise ValueError(f"Schema inválido no arquivo {path}: colunas obrigatórias não encontradas") from e

        df = df.rename(columns={
            code_col:   "codigo_ibge",
            name_col:   "municipio",
            year_col:   "ano",
            pib_col:    "pib"
        })

        # Garante apenas as 4 colunas necessárias
        result_df = df[["codigo_ibge", "municipio", "ano", "pib"]]
        
        # Validação de schema
        try:
            validate_pib_schema(result_df)
            logging.info("Schema PIB validado com sucesso")
        except ValueError as e:
            logging.error(f"Erro de validação de schema: {str(e)}")
            raise
        
        # Verificação de integridade dos dados
        check_data_integrity(result_df, f"PIB - {path.name}")
            
        logging.info(f"Dados PIB processados: {len(result_df)} registros válidos")
        return result_df
        
    except Exception as e:
        logging.error(f"Erro ao carregar arquivo PIB {path}: {str(e)}")
        raise


def filter_municipios(df: pd.DataFrame) -> pd.DataFrame:
    """
    Filtra apenas os municípios definidos em variaveis.MUNICIPIOS.
    """
    ids = [m.id for m in MUNICIPIOS]
    return df[df["codigo_ibge"].isin(ids)]


def main(input_old: str, input_new: str, output_csv: str):
    try:
        logging.info(f"Iniciando extração de PIB: {input_old}, {input_new}")
        
        # Carrega arquivos PIB
        old_df = load_pib(Path(input_old))
        new_df = load_pib(Path(input_new))

        # Consolida dados
        logging.info("Consolidando dados de PIB")
        df = pd.concat([old_df, new_df], ignore_index=True)
        
        # Remove duplicatas se existirem
        initial_count = len(df)
        df = df.drop_duplicates(subset=["codigo_ibge", "ano"], keep="last")
        if len(df) < initial_count:
            logging.warning(f"Removidas {initial_count - len(df)} linhas duplicadas")
        
        # Filtra municípios de interesse
        df = filter_municipios(df)
        logging.info(f"Dados filtrados para {len(df)} registros dos municípios alvo")
        
        if df.empty:
            raise ValueError("Nenhum dado encontrado para os municípios especificados")
        
        df = df.sort_values(["codigo_ibge", "ano"])

        # Garante que a pasta de saída existe
        out_dir = os.path.dirname(output_csv)
        os.makedirs(out_dir, exist_ok=True)

        # Salva arquivo final
        df.to_csv(output_csv, index=False, encoding="utf-8-sig")
        logging.info(f"Arquivo PIB salvo com sucesso: {output_csv} ({len(df)} registros)")
        
    except Exception as e:
        logging.error(f"Erro durante execução do pipeline PIB: {str(e)}")
        raise


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Extrai e consolida série temporal de PIB municipal."
    )
    parser.add_argument(
        "--input-old", default=INPUT_PATHS.pib_2002_2009,
        help="Caminho do arquivo XLS (2002–2009)"
    )
    parser.add_argument(
        "--input-new", default=INPUT_PATHS.pib_2010_2021,
        help="Caminho do arquivo XLSX (2010–2021)"
    )
    parser.add_argument(
        "--output", default=GENERATED_PATHS.pib_ibge_csv,
        help="CSV de saída consolidado"
    )
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s"
    )
    main(args.input_old, args.input_new, args.output)
