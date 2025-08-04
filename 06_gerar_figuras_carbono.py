# 06_gerar_figuras_carbono.py
"""
Gera todas as figuras finais do artigo com nomenclatura numerada e explicativa:

Figura01_Evolucao_PIB.png
    - Evolução do PIB Municipal (antes em etapa 04)
Figura02_Evolucao_GEE.png
    - Evolução das Emissões de GEE Municipais (antes em etapa 04)
Figura03_Evolucao_Desmatamento.png
    - Evolução do Desmatamento Municipal (antes em etapa 04)
Figura04_EQM_Modelos.png
    - Barplot de EQM (MSE) comparando os 9 modelos treinados (antes em etapa 08)
Figura05_Correlacoes.png
    - Heatmap de causalidade de Granger entre PIB, GEE, desmatamento e preço de carbono (antes em etapa 08)
Figura07_x.png  (x = 1..9)
    - Scatters Real vs Previsto para cada modelo: 1=LinearRegression, 2=RandomForest, 3=KNN, 4=DecisionTree,
      5=MLP, 6=Lasso, 7=SVR, 8=Dummy, 9=XGBoost (antes em etapa 07)
Figura08_Importancia_Variaveis.png
    - Importância relativa das variáveis (Random Forest) (antes em etapa 08)
Figura09_Evolucao_Preco_Carbono.png
    - Evolução temporal do preço do carbono (EU ETS) (antes em etapa 08)
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
from variaveis import INPUT_PATHS, GENERATED_PATHS, RESULT_PATHS, FEATURE_COLS, FEATURE_COLS_EXPANDIDO, CARBONO_CONSOLIDADO_COM_IDHM, granger_causality_matrix

sns.set(style='whitegrid')
fig_dir = os.path.dirname(RESULT_PATHS.evolucao_pib_png)
os.makedirs(fig_dir, exist_ok=True)

# contador de figuras
fig_num = 1

# 1) Carregar dados consolidados e verificar
print("[INFO] Carregando dados consolidados de:", GENERATED_PATHS.carbono_consolidado_csv)
df = pd.read_csv(GENERATED_PATHS.carbono_consolidado_csv, encoding='utf-8-sig')
print(
    f"[INFO] DataFrame carregado: {df.shape[0]} linhas, {df.shape[1]} colunas")

# 2) Ler e mesclar preços de carbono (EU ETS)
print("[INFO] Carregando série de preços de carbono de:",
      INPUT_PATHS.carbon_prices_raw)
price_raw = pd.read_excel(
    INPUT_PATHS.carbon_prices_raw,
    sheet_name=0,
    header=1
)
print(
    f"[INFO] Série de preços carregada: {price_raw.shape[0]} linhas, {price_raw.shape[1]} colunas")
year_cols = [c for c in price_raw.columns if isinstance(c, int)]
price_df = price_raw.melt(
    id_vars=['Instrument name'],
    value_vars=year_cols,
    var_name='ano',
    value_name='carbon_price_usd'
)
price_df = price_df[price_df['Instrument name'] == 'EU ETS']
price_df['ano'] = price_df['ano'].astype(int)
price_df['carbon_price_usd'] = pd.to_numeric(
    price_df['carbon_price_usd'], errors='coerce')
price_df = price_df[['ano', 'carbon_price_usd']].dropna().drop_duplicates()
print(f"[INFO] Preços filtrados EU ETS: {price_df.shape[0]} anos")

# 3) Mesclar preços
df = df.merge(price_df, on='ano', how='left')
print(
    f"[INFO] Após merge de preços: {df.shape[0]} linhas, {df.shape[1]} colunas")

# 4) Agregar por município e ano
print("[INFO] Agregando dados por município e ano...")
df_agg = df.groupby(['municipio', 'ano'], as_index=False).agg({
    'pib': 'first',
    'GEE_tCO2e': 'sum',
    'area_desmatada_ha': 'sum',
    'carbon_price_usd': 'first'
})
print(f"[INFO] DataFrame agregado: {df_agg.shape[0]} registros únicos")

# --- Figura 01: Evolução do PIB Municipal ---
print("[INFO] Gerando Figura 01")
path = os.path.join(fig_dir, f'Figura{fig_num:02d}_Evolucao_PIB.png')
plt.figure(figsize=(8, 5))
sns.lineplot(data=df_agg, x='ano', y='pib', hue='municipio', marker='o')
plt.xlabel('Ano')
plt.ylabel('PIB (R$)')
plt.title('Figura 01. Evolução do PIB Municipal')
plt.tight_layout()
plt.savefig(path)
plt.close()
print(f"[OK] Figura {fig_num:02d} salva em {path}")
fig_num += 1

# --- Figura 06: Causalidade IDHM × Desmatamento ---
print("[INFO] Gerando Figura 06")
if os.path.exists(CARBONO_CONSOLIDADO_COM_IDHM):
    df_idhm_full = pd.read_csv(CARBONO_CONSOLIDADO_COM_IDHM, encoding='utf-8-sig')
    idhm_cols = [c for c in df_idhm_full.columns if c.startswith('idhm_')]
    caus_cols2 = idhm_cols + ['area_desmatada_ha']
    df_idhm_sorted = df_idhm_full.sort_values('ano')
    matrix2 = granger_causality_matrix(df_idhm_sorted, caus_cols2, maxlag=2, verbose=True)
    path = RESULT_PATHS.causalidade_idhm_desmat_png
    plt.figure(figsize=(8, 6))
    sns.heatmap(1 - matrix2, annot=True, fmt='.3f', cmap='Reds',
                xticklabels=caus_cols2, yticklabels=caus_cols2,
                cbar_kws={'label': 'Força da Causalidade (1 - p-valor)'})
    plt.xticks(rotation=45)
    plt.yticks(rotation=0)
    plt.title('Figura 06. Causalidade de Granger – IDHM × Desmatamento')
    plt.tight_layout()
    plt.savefig(path)
    plt.close()
    print(f"[OK] Figura 06 salva em {path}")
else:
    print(f"[WARN] {CARBONO_CONSOLIDADO_COM_IDHM} não encontrado. Figura 06 não gerada.")
fig_num += 1

# --- Figura 02: Evolução das Emissões de GEE Municipais ---
print("[INFO] Gerando Figura 02")
path = os.path.join(fig_dir, f'Figura{fig_num:02d}_Evolucao_GEE.png')
plt.figure(figsize=(8, 5))
sns.lineplot(data=df_agg, x='ano', y='GEE_tCO2e', hue='municipio', marker='o')
plt.xlabel('Ano')
plt.ylabel('Emissões de GEE (tCO2e)')
plt.title('Figura 02. Evolução das Emissões de GEE Municipais')
plt.tight_layout()
plt.savefig(path)
plt.close()
print(f"[OK] Figura {fig_num:02d} salva em {path}")
fig_num += 1

# --- Figura 03: Evolução do Desmatamento Municipal ---
print("[INFO] Gerando Figura 03")
path = os.path.join(fig_dir, f'Figura{fig_num:02d}_Evolucao_Desmatamento.png')
plt.figure(figsize=(8, 5))
sns.lineplot(data=df_agg, x='ano', y='area_desmatada_ha',
             hue='municipio', marker='o')
plt.xlabel('Ano')
plt.ylabel('Área Desmatada (ha)')
plt.title('Figura 03. Evolução do Desmatamento Municipal')
plt.tight_layout()
plt.savefig(path)
plt.close()
print(f"[OK] Figura {fig_num:02d} salva em {path}")
fig_num += 1

# --- Figura 04: Comparação de EQM (MSE) dos Modelos ---
print("[INFO] Carregando métricas de modelos")
df_res = pd.read_csv(RESULT_PATHS.model_results_csv)
print(f"[INFO] Métricas carregadas: {df_res.shape[0]} modelos")
print("[INFO] Gerando Figura 04")
path = os.path.join(fig_dir, f'Figura{fig_num:02d}_EQM_Modelos.png')
plt.figure(figsize=(8, 5))
sns.barplot(data=df_res, x='model', y='MSE')
plt.xticks(rotation=45, ha='right')
plt.ylabel('EQM (MSE)')
plt.xlabel('Modelos')
plt.title('Figura 04. Comparação de Erro Quadrático Médio (MSE)')
plt.tight_layout()
plt.savefig(path)
plt.close()
print(f"[OK] Figura {fig_num:02d} salva em {path}")
fig_num += 1

# --- Figura 05: Causalidade de Granger entre Variáveis ---
print("[INFO] Gerando Figura 05")
causality_cols = FEATURE_COLS + ['carbon_price_usd']
# Ordenar dados por ano para análise temporal
df_sorted = df_agg.sort_values('ano')
causality_matrix = granger_causality_matrix(df_sorted, causality_cols, maxlag=2, verbose=True)
path = os.path.join(fig_dir, f'Figura{fig_num:02d}_Causalidade_Granger.png')
plt.figure(figsize=(8, 6))
# Usar 1-p_valor para mostrar força da causalidade (valores altos = causalidade forte)
causality_strength = 1 - causality_matrix
sns.heatmap(causality_strength, annot=True, fmt='.3f', cmap='Reds',
            xticklabels=causality_cols, yticklabels=causality_cols,
            cbar_kws={'label': 'Força da Causalidade (1 - p-valor)'})
plt.xticks(rotation=45)
plt.yticks(rotation=0)
plt.title('Figura 05. Causalidade de Granger entre Variáveis\n(Linha causa Coluna)')
plt.tight_layout()
plt.savefig(path)
plt.close()
print(f"[OK] Figura {fig_num:02d} salva em {path}")
fig_num += 1

# --- Preparar dados para scatter ------------------------------------------------
print("[INFO] Preparando dados para scatters")
model_df = df_agg.dropna(subset=FEATURE_COLS + ['carbon_price_usd'])
print(f"[INFO] Amostras válidas para modelagem: {model_df.shape}")
X = model_df[FEATURE_COLS]
y = model_df['carbon_price_usd']
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42)
scaler = StandardScaler()
X_train_s = scaler.fit_transform(X_train)
X_test_s = scaler.transform(X_test)

# --- Figura 07_x: Scatter Real vs Previsto para cada modelo ---
print("[INFO] Gerando scatters para cada modelo")
models = {
    'LinearRegression': LinearRegression(),
    'RandomForest': RandomForestRegressor(random_state=42),
    'KNN': KNeighborsRegressor(),
    'DecisionTree': DecisionTreeRegressor(random_state=42),
    'MLP': MLPRegressor(max_iter=1000, random_state=42),
    'Lasso': Lasso(alpha=0.01, random_state=42),
    'SVR': SVR(kernel='rbf'),
    'Dummy': DummyRegressor(),
    'XGBoost': XGBRegressor(random_state=42)
}
for idx, (name, model) in enumerate(models.items(), start=1):
    print(f"[INFO] Treinando modelo {name} (scatter {idx})")
    model.fit(X_train_s, y_train)
    y_pred = model.predict(X_test_s)
    filename = f"Figura07_{idx}_{name}.png"
    path = os.path.join(fig_dir, filename)
    plt.figure(figsize=(6, 6))
    sns.scatterplot(x=y_test, y=y_pred)
    plt.plot([y_test.min(), y_test.max()], [y_test.min(), y_test.max()], 'r--')
    plt.xlabel('Real')
    plt.ylabel('Previsto')
    plt.title(f'Figura 07_{idx}. Real vs Previsto – {name}')
    plt.tight_layout()
    plt.savefig(path)
    plt.close()
    print(f"[OK] Figura07_{idx} salva em {path}")

# --- Figura 08: Importância de variáveis – Random Forest ---
print("[INFO] Gerando Figura 08")
model_rf = RandomForestRegressor(random_state=42)
model_rf.fit(X_train_s, y_train)
importances = model_rf.feature_importances_
path = os.path.join(fig_dir, 'Figura08_Importancia_Variaveis.png')
plt.figure(figsize=(6, 5))
sns.barplot(x=FEATURE_COLS, y=importances)
plt.xticks(rotation=45)
plt.ylabel('Importância Relativa')
plt.xlabel('Variáveis')
plt.title('Figura 08. Importância de Variáveis – Random Forest')
plt.tight_layout()
plt.savefig(path)
plt.close()
print(f"[OK] Figura08 salva em {path}")

# --- Figura 09: Evolução temporal do preço de carbono ---
print("[INFO] Gerando Figura 09")
path = os.path.join(fig_dir, 'Figura09_Evolucao_Preco_Carbono.png')
plt.figure(figsize=(8, 5))
sns.lineplot(data=price_df, x='ano', y='carbon_price_usd', marker='o')
plt.xlabel('Ano')
plt.ylabel('Preço do Carbono (USD)')
plt.title('Figura 09. Evolução Temporal do Preço de Carbono – EU ETS')
plt.tight_layout()
plt.savefig(path)
plt.close()
print(f"[OK] Figura09 salva em {path}")

print('[OK] Todas as figuras numeradas geradas com sucesso!')
