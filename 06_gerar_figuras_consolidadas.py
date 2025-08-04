# -*- coding: utf-8 -*-
# src/06_gerar_figuras_carbono.py
"""
06_gerar_figuras_carbono.py

Gera as figuras finais em formato vetorial PDF para uso em LaTeX

  Figura01 – Painéis sincronizados:
              (a) Emissões de GEE 1985-2023
              (b) PIB municipal 2002-2021
  Figura02 – Comparação de MSE entre Modelos (TimeSeriesSplit k=10)
  Figura03 – Importância de Variáveis (Random Forest)
  Figura04 – Matriz de Causalidade de Granger
"""

import os
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import warnings

from variaveis import (
    INPUT_PATHS,
    FEATURE_COLS,
    GENERATED_PATHS,
    RESULT_PATHS,
    granger_causality_matrix,
)
from sklearn.model_selection import TimeSeriesSplit
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LinearRegression, Lasso
from sklearn.neighbors import KNeighborsRegressor
from sklearn.ensemble import RandomForestRegressor
from sklearn.tree import DecisionTreeRegressor
from sklearn.neural_network import MLPRegressor
from sklearn.svm import SVR
from sklearn.dummy import DummyRegressor
from xgboost import XGBRegressor

# Supress warnings about missing glyphs
warnings.filterwarnings("ignore", message="Glyph 8322")
# Supress MLPRegressor convergence warnings
warnings.filterwarnings("ignore", category=UserWarning, module="sklearn")
# Supress statsmodels FutureWarning about verbose parameter
warnings.filterwarnings("ignore", message="verbose is deprecated")

sns.set(style="whitegrid")

# ---------------------------------------------------------------------------
# 0 ▪ Pastas e saídas em PDF
# ---------------------------------------------------------------------------
output_dir = "results/figuras_consolidadas"
os.makedirs(output_dir, exist_ok=True)

figura01_path = os.path.join(
    output_dir, "Figura01_Paineis_GEE_PIB.pdf")
figura02_path = os.path.join(output_dir, "Figura02_Comparacao_MSE.pdf")
figura03_path = os.path.join(output_dir, "Figura03_Importancia_RF.pdf")
figura04_path = os.path.join(
    output_dir, "Figura04_Matriz_Causalidade_Granger.pdf")

# ---------------------------------------------------------------------------
# 1 ▪ Carrega e prepara dados
# ---------------------------------------------------------------------------
df = pd.read_csv(GENERATED_PATHS.carbono_consolidado_csv, encoding="utf-8-sig")
df = df.groupby(["municipio", "ano"], as_index=False).agg({
    "pib": "first",
    "GEE_tCO2e": "sum",
    "area_desmatada_ha": "sum",
})

price = (
    pd.read_excel(INPUT_PATHS.carbon_prices_raw,
                  sheet_name=0, header=1, engine="openpyxl")
    .melt(id_vars=["Instrument name"], var_name="ano", value_name="carbon_price_usd")
    .query("`Instrument name` == 'EU ETS'")
    .loc[:, ["ano", "carbon_price_usd"]]
    .dropna(subset=["carbon_price_usd"])
)
price["ano"] = pd.to_numeric(price["ano"], errors="coerce")
price = price.dropna(subset=["ano"]).astype({"ano": int}).drop_duplicates()
df = df.merge(price, on="ano", how="left")

# ---------------------------------------------------------------------------
# 2 ▪ FIGURA 01 – Painéis GEE × PIB
# ---------------------------------------------------------------------------
gee = df.groupby(["ano", "municipio"])["GEE_tCO2e"].sum().reset_index()
pib = df.groupby(["ano", "municipio"])["pib"].sum().reset_index()

fig, (ax1, ax2) = plt.subplots(2, 1, sharex=True, figsize=(7.0, 6.5), dpi=300)
for mun, g in gee.groupby("municipio"):
    ax1.plot(g["ano"], g["GEE_tCO2e"], label=mun, linewidth=1)
ax1.axvspan(2002, 2021, color="grey", alpha=0.15)
ax1.set_ylabel("GEE (tCO$_2$e)")
ax1.set_title("(a) Emissões de GEE – 1985-2023", loc="left", fontsize=9)

for mun, g in pib.groupby("municipio"):
    ax2.plot(g["ano"], g["pib"], label=mun, linewidth=1)
ax2.set_xlim(1985, 2023)
ax2.set_ylabel("PIB (R$ milhões)")
ax2.set_xlabel("Ano")
ax2.set_title("(b) PIB municipal – 2002-2021", loc="left", fontsize=9)

fig.legend(loc="upper center", ncol=len(
    gee["municipio"].unique()), frameon=False, fontsize=7)
plt.tight_layout(rect=[0, 0, 1, 0.93])
fig.savefig(figura01_path, format="pdf", bbox_inches="tight")
plt.close()

# ---------------------------------------------------------------------------
# 3 ▪ FIGURA 02 – EQM dos modelos com TimeSeriesSplit k=10
# ---------------------------------------------------------------------------
# Prepara dados de features e target
Xy = df.dropna(subset=FEATURE_COLS + ["carbon_price_usd"])
Xy = Xy.sort_values("ano").reset_index(drop=True)
X = Xy[FEATURE_COLS]
y = Xy["carbon_price_usd"]

# Configura validacao temporal k-fold
tscv = TimeSeriesSplit(n_splits=10)
models = {
    "Linear": LinearRegression(),
    "RandomForest": RandomForestRegressor(random_state=0),
    "KNN": KNeighborsRegressor(),
    "DecisionTree": DecisionTreeRegressor(random_state=0),
    "MLP": MLPRegressor(max_iter=2000, random_state=0),
    "Lasso": Lasso(alpha=0.01, random_state=0),
    "SVR": SVR(),
    "Dummy": DummyRegressor(),
    "XGBoost": XGBRegressor(random_state=0),
}

mse_results = []
for name, mdl in models.items():
    fold_mse = []
    for train_idx, test_idx in tscv.split(X):
        X_train, X_test = X.iloc[train_idx], X.iloc[test_idx]
        y_train, y_test = y.iloc[train_idx], y.iloc[test_idx]
        scaler = StandardScaler().fit(X_train)
        X_train_s, X_test_s = scaler.transform(
            X_train), scaler.transform(X_test)
        mdl.fit(X_train_s, y_train)
        pred = mdl.predict(X_test_s)
        fold_mse.append(((pred - y_test) ** 2).mean())
    mse_results.append({"Model": name, "MSE": np.mean(fold_mse)})

mse_df = pd.DataFrame(mse_results).sort_values("MSE")
plt.figure(figsize=(7, 4))
sns.barplot(data=mse_df, x="Model", y="MSE")
plt.xticks(rotation=45, ha="right", fontsize=8)
plt.ylabel("EQM (MSE)")
plt.tight_layout()
plt.savefig(figura02_path, format="pdf", bbox_inches="tight")
plt.close()

# ---------------------------------------------------------------------------
# 4 ▪ FIGURA 03 – Importância de variáveis (RF)
# ---------------------------------------------------------------------------
rf = RandomForestRegressor(random_state=0).fit(
    StandardScaler().fit_transform(X), y
)
plt.figure(figsize=(6, 4))
sns.barplot(x=FEATURE_COLS, y=rf.feature_importances_)
plt.ylabel("Importância relativa")
plt.tight_layout()
plt.savefig(figura03_path, format="pdf", bbox_inches="tight")
plt.close()

# ---------------------------------------------------------------------------
# 5 ▪ FIGURA 04 – Matriz de Causalidade de Granger
# ---------------------------------------------------------------------------
causality_cols = ["pib", "GEE_tCO2e", "area_desmatada_ha", "carbon_price_usd"]
# Ordenar dados por ano para análise temporal
df_sorted = df.sort_values("ano")
causality_matrix = granger_causality_matrix(df_sorted, causality_cols, maxlag=2, verbose=False)
# Usar 1-p_valor para mostrar força da causalidade
causality_strength = 1 - causality_matrix
plt.figure(figsize=(6.5, 6))
sns.heatmap(causality_strength, annot=True, fmt=".3f",
            cmap="Reds", linewidths=0.5, square=True,
            cbar_kws={'label': 'Força da Causalidade (1 - p-valor)'})
plt.title('Causalidade de Granger entre Variáveis\n(Linha causa Coluna)', fontsize=10)
plt.tight_layout()
plt.savefig(figura04_path, format="pdf", bbox_inches="tight")
plt.close()

print("[OK] Figuras 01-04 em PDF vetorial com validacao temporal k=10 geradas com sucesso!")
