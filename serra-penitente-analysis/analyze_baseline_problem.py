import pandas as pd

# Carregar dados
df = pd.read_csv("data/generated/carbono_serra_penitente_com_idhm.csv")

print("=== ANÁLISE DETALHADA POR MUNICÍPIO ===")
print(f"\nMunicípios únicos: {df['municipio'].unique()}")
print("\nDados por município e ano (primeiros 20):")
print(df[["municipio", "ano", "GEE_tCO2e"]].head(20))

print("\nVariação por município:")
for mun in df["municipio"].unique():
    subset = df[df["municipio"] == mun]
    print(
        f"{mun}: min={subset['GEE_tCO2e'].min():.0f}, "
        f"max={subset['GEE_tCO2e'].max():.0f}, "
        f"std={subset['GEE_tCO2e'].std():.0f}"
    )

print("\n=== ANÁLISE DE CORRELAÇÕES ===")
print("Correlação entre features numéricas:")
numeric_cols = [
    "pib",
    "GEE_tCO2e",
    "area_desmatada_ha",
    "idhm_",
    "idhm_renda",
    "idhm_educação",
    "idhm_longevidade",
]
corr_matrix = df[numeric_cols].corr()
print(corr_matrix["GEE_tCO2e"].sort_values(ascending=False))

print("\n=== VERIFICAÇÃO DE DADOS CONSTANTES ===")
for col in numeric_cols:
    unique_vals = df[col].nunique()
    print(f"{col}: {unique_vals} valores únicos")
    if unique_vals <= 5:
        print(f"  Valores: {sorted(df[col].unique())}")
