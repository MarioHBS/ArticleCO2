# -*- coding: utf-8 -*-
# src/06_gerar_figuras_carbono.py
"""
06_gerar_figuras_carbono.py

Gera as figuras finais para o artigo (versão com painéis GEE-PIB):

  Figura01 – Painéis sincronizados:
              (a) Emissões de GEE 1985-2023
              (b) PIB municipal 2002-2021
  Figura02 – Comparação de MSE entre Modelos
  Figura03 – Importância de Variáveis (Random Forest)
  Figura04 – Matriz de Correlação
------------------------------------------------------------------------------
Figuras exploratórias (opcionais / suplemento):
  • Evolução do Desmatamento
  • Grid 3×3 Real vs Previsto
  • Evolução do Preço do Carbono                       (comentadas por padrão)
------------------------------------------------------------------------------
Para manter o código compacto, Seaborn usa o estilo ‘whitegrid’ padrão IEEE.
"""

from variaveis import (
    CARBONO_CONSOLIDADO,
    INPUT_PATHS,
    FEATURE_COLS,
    OUTPUT_PATHS,        # dataclass usado para guardar caminhos
)
from xgboost import XGBRegressor
from sklearn.dummy import DummyRegressor
from sklearn.svm import SVR
from sklearn.neural_network import MLPRegressor
from sklearn.tree import DecisionTreeRegressor
from sklearn.ensemble import RandomForestRegressor
from sklearn.neighbors import KNeighborsRegressor
from sklearn.linear_model import LinearRegression, Lasso
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
import os
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import warnings
warnings.filterwarnings("ignore", message="Glyph 8322")


sns.set(style="whitegrid")

# ---------------------------------------------------------------------------
# 0 ▪ Pastas e nomes de saída
# ---------------------------------------------------------------------------
output_dir = "results/figuras_consolidadas"
os.makedirs(output_dir, exist_ok=True)

OUTPUT_PATHS.figura01 = os.path.join(
    output_dir, "Figura01_Paineis_GEE_PIB.png")
OUTPUT_PATHS.figura02 = os.path.join(output_dir, "Figura02_Comparacao_MSE.png")
OUTPUT_PATHS.figura03 = os.path.join(output_dir, "Figura03_Importancia_RF.png")
OUTPUT_PATHS.figura04 = os.path.join(
    output_dir, "Figura04_Matriz_Correlacao.png")

# ---------------------------------------------------------------------------
# 1 ▪ Carrega e prepara dados
# ---------------------------------------------------------------------------
df = pd.read_csv(CARBONO_CONSOLIDADO, encoding="utf-8-sig")

df = (
    df.groupby(["municipio", "ano"], as_index=False)
      .agg({
          "pib": "first",
          "GEE_tCO2e": "sum",
          "area_desmatada_ha": "sum",
      })
)

# Preço do carbono (para matriz de correlação)
price = (
    pd.read_excel(INPUT_PATHS.carbon_prices_raw,
                  sheet_name=0, header=1, engine="openpyxl")
    .melt(id_vars=["Instrument name"], var_name="ano", value_name="carbon_price_usd")
    .query("`Instrument name` == 'EU ETS'")
    .loc[:, ["ano", "carbon_price_usd"]]
    .dropna(subset=["carbon_price_usd"])
)

# ▪ converter “ano” para numérico; lixo vira NaN
price["ano"] = pd.to_numeric(price["ano"], errors="coerce")
# ▪ descartar linhas onde não há ano válido
price = price.dropna(subset=["ano"]).astype({"ano": int}).drop_duplicates()

df = df.merge(price, on="ano", how="left")

# ---------------------------------------------------------------------------
# 2 ▪ FIGURA 01 – Painéis GEE × PIB (eixo x compartilhado)
# ---------------------------------------------------------------------------
gee = (
    df.groupby(["ano", "municipio"])["GEE_tCO2e"]
    .sum()
    .reset_index()
)
pib = (
    df.groupby(["ano", "municipio"])["pib"]
    .sum()
    .reset_index()
)

fig, (ax1, ax2) = plt.subplots(
    2, 1, sharex=True, figsize=(7.0, 6.5), dpi=300
)

# (a) Emissões de GEE
for mun, g in gee.groupby("municipio"):
    ax1.plot(g["ano"], g["GEE_tCO2e"], label=mun, linewidth=1)
ax1.axvspan(2002, 2021, color="grey", alpha=0.15)
ax1.set_ylabel("GEE (tCO₂e)")
ax1.set_title("(a) Emissões de GEE – 1985-2023", loc="left", fontsize=9)

# (b) PIB municipal
for mun, g in pib.groupby("municipio"):
    ax2.plot(g["ano"], g["pib"], label=mun, linewidth=1)
ax2.set_xlim(1985, 2023)
ax2.set_ylabel("PIB (R$ milhões)")
ax2.set_xlabel("Ano")
ax2.set_title("(b) PIB municipal – 2002-2021", loc="left", fontsize=9)

# legenda única
fig.legend(
    loc="upper center",
    ncol=len(gee["municipio"].unique()),
    frameon=False,
    fontsize=7,
)
plt.tight_layout(rect=[0, 0, 1, 0.93])
fig.savefig(OUTPUT_PATHS.figura01, bbox_inches="tight")
plt.close()

# ---------------------------------------------------------------------------
# 3 ▪ FIGURA 02 – EQM dos modelos
# ---------------------------------------------------------------------------
Xy = df.dropna(subset=FEATURE_COLS + ["carbon_price_usd"])
X = Xy[FEATURE_COLS]
y = Xy["carbon_price_usd"]
Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.2, random_state=42)
scaler = StandardScaler().fit(Xtr)
Xtr_s, Xte_s = scaler.transform(Xtr), scaler.transform(Xte)

models = {
    "Linear": LinearRegression(),
    "RandomForest": RandomForestRegressor(random_state=0),
    "KNN": KNeighborsRegressor(),
    "DecisionTree": DecisionTreeRegressor(random_state=0),
    "MLP": MLPRegressor(max_iter=1000, random_state=0),
    "Lasso": Lasso(alpha=0.01, random_state=0),
    "SVR": SVR(),
    "Dummy": DummyRegressor(),
    "XGBoost": XGBRegressor(random_state=0),
}

mse = []
for nome, mdl in models.items():
    mdl.fit(Xtr_s, ytr)
    pred = mdl.predict(Xte_s)
    mse.append({"Model": nome, "MSE": ((pred - yte) ** 2).mean()})

mse_df = pd.DataFrame(mse).sort_values("MSE")
plt.figure(figsize=(7, 4))
sns.barplot(data=mse_df, x="Model", y="MSE")
plt.xticks(rotation=45, ha="right", fontsize=8)
plt.xlabel("")
plt.ylabel("EQM (MSE)")
plt.tight_layout()
plt.savefig(OUTPUT_PATHS.figura02)
plt.close()

# ---------------------------------------------------------------------------
# 4 ▪ FIGURA 03 – Importância de variáveis (Random Forest)
# ---------------------------------------------------------------------------
rf = RandomForestRegressor(random_state=0).fit(Xtr_s, ytr)
plt.figure(figsize=(6, 4))
sns.barplot(
    x=FEATURE_COLS,
    y=rf.feature_importances_,
)
plt.ylabel("Importância relativa")
plt.xlabel("")
plt.tight_layout()
plt.savefig(OUTPUT_PATHS.figura03)
plt.close()

# ---------------------------------------------------------------------------
# 5 ▪ FIGURA 04 – Matriz de correlação
# ---------------------------------------------------------------------------
corr = df[["pib", "GEE_tCO2e", "area_desmatada_ha", "carbon_price_usd"]].corr()
plt.figure(figsize=(5.5, 5))
sns.heatmap(
    corr,
    annot=True,
    fmt=".2f",
    cmap="coolwarm",
    linewidths=0.5,
    square=True,
)
plt.tight_layout()
plt.savefig(OUTPUT_PATHS.figura04)
plt.close()

print("✅ Figuras 01-04 geradas (modelo de painéis) com sucesso!")
