# 07_predizer_preco_carbono.py
# Predição de Preço de Carbono — script final com paths de variables.py

import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import r2_score, mean_squared_error
from sklearn.linear_model import LinearRegression, Lasso
from sklearn.neighbors import KNeighborsRegressor
from sklearn.ensemble import RandomForestRegressor
from sklearn.tree import DecisionTreeRegressor
from sklearn.neural_network import MLPRegressor
from sklearn.svm import SVR
from sklearn.dummy import DummyRegressor
from xgboost import XGBRegressor
from variaveis import FEATURE_COLS, INPUT_PATHS, OUTPUT_PATHS

# Configuração de plots
sns.set(style='whitegrid')
os.makedirs(os.path.dirname(OUTPUT_PATHS.scatter_xgboost_png), exist_ok=True)

# 1) Carregar dataset consolidado (PIB, GEE, desmatamento)
df = pd.read_csv(INPUT_PATHS.carbono_consolidado, encoding='utf-8-sig')
print("Colunas iniciais:", df.columns.tolist())

# 2) Carregar preços de carbono
price_path = INPUT_PATHS.carbon_prices_raw
xls = pd.ExcelFile(price_path)
sheet = xls.sheet_names[0]
price_raw = pd.read_excel(xls, sheet_name=sheet, header=1)
print("Colunas do sheet de preços:", price_raw.columns.tolist())

# Identificar a coluna de instrumento (Instrument name)
instrument_col = 'Instrument name'
# Identificar colunas de anos (tipos int)
year_cols = [c for c in price_raw.columns if isinstance(c, int)]

# 3) Transformar preços em formato long
df_price = price_raw.melt(
    id_vars=[instrument_col],
    value_vars=year_cols,
    var_name='ano',
    value_name='carbon_price_usd'
)
# Filtrar apenas o EU ETS
df_price = df_price[df_price[instrument_col] == 'EU ETS']
# Converter tipos
df_price['ano'] = df_price['ano'].astype(int)
df_price['carbon_price_usd'] = pd.to_numeric(
    df_price['carbon_price_usd'], errors='coerce')
# Selecionar e limpar
df_price = df_price[['ano', 'carbon_price_usd']].dropna().drop_duplicates()
print(f"Preços disponíveis: {df_price['ano'].min()}–{df_price['ano'].max()}")

# 4) Mesclar preços ao dataset principal
df = df.merge(df_price, on='ano', how='inner')
print("Dataset após merge:", df.shape)

# 4.1) Agregar dados por município e ano para evitar duplicações
# Mantém uma linha única por município-ano
df = (
    df.groupby(['municipio', 'ano'], as_index=False)
      .agg({
          'pib': 'first',                  # PIB já é único por muni-ano
          'GEE_tCO2e': 'sum',              # soma emissões de todas as classes
          'area_desmatada_ha': 'sum',      # soma área desmatada total
          'carbon_price_usd': 'first'      # preço único por ano
      })
)
print("Após agregação município-ano:", df.shape)

# 5) Preparar features e target
feature_cols = FEATURE_COLS
for col in feature_cols:
    df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
target_col = 'carbon_price_usd'

# 6) Divisão treino/teste
X = df[feature_cols]
y = df[target_col]
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42)

# 7) Padronização
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# 8) Definir e treinar modelos
modelos = {
    'Linear Regression': LinearRegression(),
    'Random Forest': RandomForestRegressor(random_state=42),
    'KNN Regressor': KNeighborsRegressor(),
    'Decision Tree': DecisionTreeRegressor(random_state=42),
    'MLP Regressor': MLPRegressor(max_iter=1000, random_state=42),
    'Lasso': Lasso(alpha=0.01, random_state=42),
    'SVR': SVR(kernel='rbf'),
    'Dummy': DummyRegressor(),
    'XGBoost': XGBRegressor(random_state=42)
}

results = []
for name, model in modelos.items():
    print(f"Treinando {name}...")
    model.fit(X_train_scaled, y_train)
    preds = model.predict(X_test_scaled)
    r2 = r2_score(y_test, preds)
    mse = mean_squared_error(y_test, preds)
    print(f"{name} → R²: {r2:.3f}, MSE: {mse:.3f}")
    results.append({'model': name, 'R2': r2, 'MSE': mse})

# 9) Salvar resultados
df_res = pd.DataFrame(results)
df_res.to_csv(OUTPUT_PATHS.model_results_csv, index=False)
print("Resultados salvos em:", OUTPUT_PATHS.model_results_csv)

# 10) Gerar scatter Real vs Previsto para cada modelo
fig_dir = os.path.dirname(OUTPUT_PATHS.scatter_xgboost_png)
for model_name, model in modelos.items():
    y_pred = model.predict(X_test_scaled)
    slug = model_name.lower().replace(' ', '_')
    scatter_path = os.path.join(fig_dir, f"scatter_real_vs_pred_{slug}.png")
    plt.figure(figsize=(6, 6))
    sns.scatterplot(x=y_test, y=y_pred)
    plt.plot([y.min(), y.max()], [y.min(), y.max()], 'r--')
    plt.xlabel('Real')
    plt.ylabel('Previsto')
    plt.title(f'Real vs Previsto – {model_name}')
    plt.tight_layout()
    plt.savefig(scatter_path)
    plt.close()
    print(f"Scatter salvo para {model_name} em: {scatter_path}")
