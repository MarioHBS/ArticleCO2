# src/06_gerar_figuras_carbono.py
"""
06_gerar_figuras_carbono.py

Gera as figuras finais:
  Figura01 - Evolução do PIB
  Figura02 – Evolução das Emissões de GEE
  Figura03 – Evolução do Desmatamento
  Figura04 – Comparação de MSE entre Modelos
  Figura05 – Matriz de Correlação
  Figura06 – Importância de Variáveis (Random Forest)
  Figura07 – Grid 3×3 Real vs Previsto (todos os 9 modelos)
  Figura08 – Evolução do Preço de Carbono (EU ETS)
"""
import os
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LinearRegression, Lasso
from sklearn.neighbors import KNeighborsRegressor
from sklearn.ensemble import RandomForestRegressor
from sklearn.tree import DecisionTreeRegressor
from sklearn.neural_network import MLPRegressor
from sklearn.svm import SVR
from sklearn.dummy import DummyRegressor
from xgboost import XGBRegressor

from variaveis import CARBONO_CONSOLIDADO, INPUT_PATHS, FEATURE_COLS, OUTPUT_PATHS

sns.set(style='whitegrid')

# Atualiza a pasta de saída para 'figuras_consolidadas'
output_dir = 'results/figuras_consolidadas'
os.makedirs(output_dir, exist_ok=True)

# Atualiza os caminhos de saída para salvar as figuras na nova pasta
OUTPUT_PATHS.figura01 = os.path.join(output_dir, 'Figura01_Evolucao_PIB.png')
OUTPUT_PATHS.figura02 = os.path.join(output_dir, 'Figura02_Evolucao_GEE.png')
OUTPUT_PATHS.figura03 = os.path.join(
    output_dir, 'Figura03_Evolucao_Desmatamento.png')
OUTPUT_PATHS.figura04 = os.path.join(
    output_dir, 'Figura04_Comparacao_MSE_Modelos.png')
OUTPUT_PATHS.figura05 = os.path.join(
    output_dir, 'Figura05_Matriz_Correlacao.png')
OUTPUT_PATHS.figura06 = os.path.join(
    output_dir, 'Figura06_Importancia_Variaveis.png')
OUTPUT_PATHS.figura07 = os.path.join(
    output_dir, 'Figura07_Grid_Real_vs_Previsto.png')
OUTPUT_PATHS.figura08 = os.path.join(
    output_dir, 'Figura08_Evolucao_Preco_Carbono.png')

# carrega o dataset final
df = pd.read_csv(CARBONO_CONSOLIDADO, encoding='utf-8-sig')

# agregação por município e ano
df = df.groupby(['municipio', 'ano'], as_index=False).agg({
    'pib': 'first',
    'GEE_tCO2e': 'sum',
    'area_desmatada_ha': 'sum'
})
# merge preço de carbono
price = pd.read_excel(INPUT_PATHS.carbon_prices_raw,
                      sheet_name=0, header=1, engine='openpyxl')
years = [c for c in price.columns if isinstance(c, int)]
price = price.melt(id_vars=['Instrument name'], value_vars=years,
                   var_name='ano', value_name='carbon_price_usd')
price = price.query("`Instrument name`=='EU ETS'")
price = price[['ano', 'carbon_price_usd']].dropna().drop_duplicates()
price.ano = price.ano.astype(int)
df = df.merge(price, on='ano', how='left')

# prepara dataframe para modelagem
Xy = df.dropna(subset=FEATURE_COLS+['carbon_price_usd'])
X = Xy[FEATURE_COLS]
y = Xy['carbon_price_usd']
Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.2, random_state=42)
sc = StandardScaler().fit(Xtr)
Xtr_s, Xte_s = sc.transform(Xtr), sc.transform(Xte)

# lista de modelos
models = {
    'LinearRegression': LinearRegression(),
    'RandomForest':     RandomForestRegressor(random_state=0),
    'KNN':              KNeighborsRegressor(),
    'DecisionTree':     DecisionTreeRegressor(random_state=0),
    'MLP':              MLPRegressor(max_iter=1000, random_state=0),
    'Lasso':            Lasso(alpha=0.01, random_state=0),
    'SVR':              SVR(),
    'Dummy':            DummyRegressor(),
    'XGBoost':          XGBRegressor(random_state=0)
}

# 1) Figura 01 – Evolução do PIB
plt.figure(figsize=(8, 5))
sns.lineplot(df, x='ano', y='pib', hue='municipio', marker='o')
# plt.title('Figura 01. Evolução do PIB Municipal')
plt.xlabel('Ano')
plt.ylabel('PIB (R$)')
plt.tight_layout()
plt.savefig(OUTPUT_PATHS.figura01)
plt.close()

# 2) Figura 02 – Evolução do GEE
plt.figure(figsize=(8, 5))
sns.lineplot(df, x='ano', y='GEE_tCO2e', hue='municipio', marker='o')
# plt.title('Figura 02. Evolução das Emissões de GEE Municipais')
plt.xlabel('Ano')
plt.ylabel('Emissões de GEE (tCO₂e)')
plt.tight_layout()
plt.savefig(OUTPUT_PATHS.figura02)
plt.close()

# 3) Figura 03 – Evolução do Desmatamento
plt.figure(figsize=(8, 5))
sns.lineplot(df, x='ano', y='area_desmatada_ha', hue='municipio', marker='o')
# plt.title('Figura 03. Evolução do Desmatamento Municipal')
plt.xlabel('Ano')
plt.ylabel('Área Desmatada (ha)')
plt.tight_layout()
plt.savefig(OUTPUT_PATHS.figura03)
plt.close()

# 4) Figura 04 – MSE dos Modelos
mse_results = []
for name, mdl in models.items():
    mdl.fit(Xtr_s, ytr)
    pred = mdl.predict(Xte_s)
    mse_results.append({'model': name, 'MSE': ((pred-yte)**2).mean()})
mse_df = pd.DataFrame(mse_results)
plt.figure(figsize=(8, 5))
sns.barplot(data=mse_df, x='model', y='MSE')
plt.xticks(rotation=45, ha='right')
# plt.title('Figura 04. Comparação de Erro Quadrático Médio (MSE)')
plt.xlabel('Modelos')
plt.ylabel('EQM (MSE)')
plt.tight_layout()
plt.savefig(OUTPUT_PATHS.figura04)
plt.close()

# 5) Figura 05 – Matriz de Correlação
corr = df[['pib', 'GEE_tCO2e', 'area_desmatada_ha', 'carbon_price_usd']].corr()
plt.figure(figsize=(6, 6))
sns.heatmap(corr, annot=True, fmt='.2f', cmap='coolwarm',
            xticklabels=corr.columns, yticklabels=corr.columns)
# plt.title('Figura 05. Correlação entre Variáveis')
plt.tight_layout()
plt.savefig(OUTPUT_PATHS.figura05)
plt.close()

# 6) Figura 06 – Importância de Variáveis (RF)
rf = RandomForestRegressor(random_state=0).fit(Xtr_s, ytr)
imp = rf.feature_importances_
plt.figure(figsize=(6, 5))
sns.barplot(x=FEATURE_COLS, y=imp)
# plt.title('Figura 06. Importância de Variáveis – Random Forest')
plt.xlabel('Variáveis')
plt.ylabel('Importância Relativa')
plt.tight_layout()
plt.savefig(OUTPUT_PATHS.figura06)
plt.close()

# 7) Figura 07 – Grid 3×3 Real vs Previsto
fig, axes = plt.subplots(3, 3, figsize=(12, 12))
axes = axes.flatten()
for idx, (ax, (name, mdl)) in enumerate(zip(axes, models.items())):
    pred = mdl.predict(Xte_s)
    ax.scatter(yte, pred)
    m, y_ = yte.min(), yte.max()
    ax.plot([m, y_], [m, y_], 'r--')
    ax.set_title(name)
    if idx // 3 == 2:  # última linha
        ax.set_xlabel('Real')
    if idx % 3 == 0:   # primeira coluna
        ax.set_ylabel('Previsto')
# plt.suptitle('Figura 07. Real vs Previsto – Todos os Modelos',
#              y=0.92, fontsize=16)
plt.tight_layout(rect=[0, 0, 1, 0.96])
plt.savefig(OUTPUT_PATHS.figura07)
plt.close()

# 8) Figura 08 – Evolução do Preço de Carbono
price_df = price.sort_values('ano')
plt.figure(figsize=(8, 5))
sns.lineplot(price_df, x='ano', y='carbon_price_usd', marker='o')
# plt.title('Figura 08. Evolução Temporal do Preço de Carbono – EU ETS')
plt.xlabel('Ano')
plt.ylabel('Preço do Carbono (USD)')
plt.tight_layout()
plt.savefig(OUTPUT_PATHS.figura08)
plt.close()

print("✅ Todas as figuras (01–08) geradas com sucesso!")
