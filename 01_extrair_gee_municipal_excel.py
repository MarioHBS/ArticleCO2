# 02_extrair_cobertura_mapbiomas.py
# Extrai estatísticas de cobertura por bioma do arquivo MapBiomas
# Fonte: mapbiomas_brazil_col_coverage_biome_state_municipality.xlsx (planilha COVERAGE_9)

import os
import pandas as pd

# 1) Defina o caminho do arquivo MapBiomas
arquivo_mapb = "data/raw/mapbiomas_brazil_col_coverage_biome_state_municipality.xlsx"

# 2) Lista de códigos IBGE dos municípios de Serra do Penitente
municipios_alvo = ["2100501", "2101400", "2112001"]

# 3) Cria diretório de saída, se necessário
os.makedirs("data/partial", exist_ok=True)

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
           "classe_codigo", "classe_level_0", "classe_level_1", "classe_level_2"]
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
output_path = "data/partial/mapbiomas_cobertura_municipal_long.csv"
df_long.to_csv(output_path, index=False)

print(f"✅ CSV long de cobertura MapBiomas gerado em: {output_path}")
