# 00_extrair_pib_municipal.py
# -*- coding: utf-8 -*-
import os
import argparse
import logging
from pathlib import Path

import pandas as pd
from variaveis import INPUT_PATHS, OUTPUT_PATHS, MUNICIPIOS


def load_pib(path: Path) -> pd.DataFrame:
    """
    Carrega planilha de PIB (XLS ou XLSX), renomeia colunas dinamicamente
    e retorna DataFrame com ['codigo_ibge','municipio','ano','pib'].
    """
    engine = "xlrd" if path.suffix.lower() == ".xls" else "openpyxl"
    df = pd.read_excel(path, engine=engine)

    # Detecta colunas conforme cabeçalhos reais
    code_col = next(
        c for c in df.columns if "Código" in c and "Município" in c)
    name_col = next(c for c in df.columns if "Nome" in c and "Município" in c)
    year_col = next(c for c in df.columns if c.strip().lower() == "ano")
    pib_col = next(c for c in df.columns if "Produto Interno Bruto" in c)

    df = df.rename(columns={
        code_col:   "codigo_ibge",
        name_col:   "municipio",
        year_col:   "ano",
        pib_col:    "pib"
    })

    # Garante apenas as 4 colunas necessárias
    return df[["codigo_ibge", "municipio", "ano", "pib"]]


def filter_municipios(df: pd.DataFrame) -> pd.DataFrame:
    """
    Filtra apenas os municípios definidos em variaveis.MUNICIPIOS.
    """
    ids = [m.id for m in MUNICIPIOS]
    return df[df["codigo_ibge"].isin(ids)]


def main(input_old: str, input_new: str, output_csv: str):
    logging.info(f"Iniciando extração de PIB: {input_old}, {input_new}")
    old_df = load_pib(Path(input_old))
    new_df = load_pib(Path(input_new))

    df = pd.concat([old_df, new_df], ignore_index=True)
    df = filter_municipios(df)
    df = df.sort_values(["codigo_ibge", "ano"])

    # garante que a pasta de saída existe
    out_dir = os.path.dirname(output_csv)
    os.makedirs(out_dir, exist_ok=True)

    df.to_csv(output_csv, index=False, encoding="utf-8-sig")
    logging.info(f"Arquivo PIB salvo em: {output_csv}")


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
        "--output", default=OUTPUT_PATHS.pib_ibge_csv,
        help="CSV de saída consolidado"
    )
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s"
    )
    main(args.input_old, args.input_new, args.output)
