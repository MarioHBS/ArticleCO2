# src/02_extrair_cobertura_municipal.py
# -*- coding: utf-8 -*-
"""
Script para extração de dados de cobertura do solo municipal.

Este script processa dados de cobertura do solo do MapBiomas para os municípios
da região da Serra do Penitente, extraindo estatísticas de cobertura por bioma
a partir da planilha COVERAGE_9 do arquivo MapBiomas.
"""
import os
import pandas as pd

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from variaveis import MUNICIPIOS_ALVO, INPUT_PATHS, GENERATED_PATHS

# 1) Defina o caminho do arquivo MapBiomas
arquivo_mapb = INPUT_PATHS.mapbiomas

# 2) Lista de códigos IBGE dos municípios de Serra do Penitente
municipios_alvo = ["2100501", "2101400", "2112001"]

# 3) Cria diretório de saída, se necessário
os.makedirs("data/generated", exist_ok=True)

# 4) Carrega a planilha COVERAGE_9
df_mapb = pd.read_excel(
    arquivo_mapb,
    sheet_name="COVERAGE_9",
    dtype={"geocode": str},
)

# 5) Renomeia colunas para padrão do pipeline
df_mapb = df_mapb.rename(columns={
    "geocode": "codigo_ibge",
    "municipality": "municipio",
    "state":       "uf",
    "biome":       "bioma",
    "class":       "classe_codigo",
    "class_level_0": "classe_level_0",
    "class_level_1": "classe_level_1",
    "class_level_2": "classe_level_2",
})

# 6) Identifica colunas de ano dinamicamente (strings numéricas ou ints)
anos = [
    col for col in df_mapb.columns
    if (isinstance(col, str) and col.isdigit()) or isinstance(col, int)
]

# 7) Filtra apenas municípios de interesse
df_mapb = df_mapb[df_mapb["codigo_ibge"].isin(municipios_alvo)].copy()

# 8) Converte colunas de anos para numérico
for col in anos:
    df_mapb[col] = pd.to_numeric(df_mapb[col], errors="coerce")

# 9) Transforma para formato longo
id_vars = ["codigo_ibge", "municipio", "uf", "bioma",
           "classe_codigo", "classe_level_0",
           "classe_level_1", "classe_level_2"]
df_long = df_mapb.melt(
    id_vars=id_vars,
    value_vars=anos,
    var_name="ano",
    value_name="cobertura",
)

# Garante que 'ano' seja string
df_long["ano"] = df_long["ano"].astype(str)

# 10) Ordena e exporta
df_long = df_long.sort_values(["codigo_ibge", "bioma", "classe_codigo", "ano"])
output_path = GENERATED_PATHS.mapbiomas_long_csv
df_long.to_csv(output_path, index=False)

print(f"[OK] CSV long de cobertura MapBiomas gerado em: {output_path}")
