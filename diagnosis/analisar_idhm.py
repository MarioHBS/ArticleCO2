import pandas as pd
import os

# Carrega o arquivo IDHM
df_idhm = pd.read_excel('data/raw/idhm_municipios_serra_penitente.xlsx')

print("=== ANÁLISE DO ARQUIVO IDHM ===")
print(f"Shape: {df_idhm.shape}")
print(f"\nColunas disponíveis:")
for i, col in enumerate(df_idhm.columns):
    print(f"{i+1:2d}. {col}")

print(f"\nPrimeiras 5 linhas:")
print(df_idhm.head())

print(f"\nTipos de dados:")
print(df_idhm.dtypes)

print(f"\nValores únicos por coluna (primeiras 10 colunas):")
for col in df_idhm.columns[:10]:
    unique_count = df_idhm[col].nunique()
    print(f"{col}: {unique_count} valores únicos")

print(f"\nVerificação de municípios:")
if 'municipio' in df_idhm.columns:
    print(df_idhm['municipio'].unique())
elif 'Município' in df_idhm.columns:
    print(df_idhm['Município'].unique())
else:
    print("Coluna de município não identificada claramente")
    print("Primeiras colunas:", df_idhm.columns[:5].tolist())

print(f"\nVerificação de anos:")
if 'ano' in df_idhm.columns:
    print(df_idhm['ano'].unique())
elif 'Ano' in df_idhm.columns:
    print(df_idhm['Ano'].unique())
else:
    # Procura por colunas que podem ser anos
    year_cols = [col for col in df_idhm.columns if str(col).isdigit() and 1990 <= int(str(col)) <= 2030]
    print(f"Possíveis colunas de ano: {year_cols}")

print(f"\nIndicadores IDHM disponíveis:")
idhm_cols = [col for col in df_idhm.columns if 'idhm' in col.lower() or 'idh' in col.lower()]
print(f"Colunas relacionadas ao IDHM: {idhm_cols}")

print(f"\nResumo estatístico das colunas numéricas:")
print(df_idhm.describe())