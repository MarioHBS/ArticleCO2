# path: src/carbono_serra_penitente.py

import pandas as pd
import os
import matplotlib.pyplot as plt
import seaborn as sns

# Criar diretórios, se necessário
os.makedirs("data/generated", exist_ok=True)
os.makedirs("results/figures", exist_ok=True)

# Carregar datasets pré-processados
df_pib = pd.read_csv("data/generated/pib_municipal_serra_penitente.csv")
df_gee = pd.read_csv("data/generated/gee_serra_penitente.csv")
df_desmatamento = pd.read_csv("data/generated/desmatamento_serra_penitente.csv")

# Ajustar nomes de colunas para padronizar
if 'Município' in df_gee.columns:
    df_gee = df_gee.rename(columns={"Município": "municipio", "Ano": "ano"})
if 'Município' in df_desmatamento.columns:
    df_desmatamento = df_desmatamento.rename(columns={"Município": "municipio", "Ano": "ano"})

# Merge dos datasets
df_final = df_pib.merge(df_gee, on=["municipio", "ano"], how="outer")
df_final = df_final.merge(df_desmatamento, on=["municipio", "ano"], how="outer")

# Organizar colunas
df_final = df_final[["municipio", "ano", "pib", "GEE_tCO2e", "area_desmatada_ha"]]

# Salvar dataset final
df_final.to_csv("data/generated/carbono_serra_penitente.csv", index=False)
print("✅ Dataset final gerado: data/generated/carbono_serra_penitente.csv")

# --- Gráficos comparativos --- #

# Evolução do PIB
plt.figure(figsize=(10, 6))
sns.lineplot(data=df_final, x="ano", y="pib", hue="municipio", marker="o")
plt.title("Evolução do PIB - Municípios da Serra do Penitente")
plt.ylabel("PIB (R$)")
plt.xlabel("Ano")
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig("results/figures/evolucao_pib_serra_penitente.png")
plt.close()

# Evolução das Emissões de GEE
plt.figure(figsize=(10, 6))
sns.lineplot(data=df_final, x="ano", y="GEE_tCO2e", hue="municipio", marker="o")
plt.title("Evolução das Emissões de GEE - Serra do Penitente")
plt.ylabel("Emissões de GEE (tCO2e)")
plt.xlabel("Ano")
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig("results/figures/evolucao_gee_serra_penitente.png")
plt.close()

# Evolução da Área Desmatada
plt.figure(figsize=(10, 6))
sns.lineplot(data=df_final, x="ano", y="area_desmatada_ha", hue="municipio", marker="o")
plt.title("Evolução da Área Desmatada - Serra do Penitente")
plt.ylabel("Área Desmatada (hectares)")
plt.xlabel("Ano")
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig("results/figures/evolucao_desmatamento_serra_penitente.png")
plt.close()