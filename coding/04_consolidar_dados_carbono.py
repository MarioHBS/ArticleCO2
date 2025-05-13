# 04_consolidar_dados_carbono.py
# Consolida dados, gera modelo de precificação e salva métricas

import os
import ast

import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import r2_score, mean_squared_error
from sklearn.linear_model import LinearRegression, Lasso
from sklearn.neighbors import KNeighborsRegressor
from sklearn.tree import DecisionTreeRegressor
from sklearn.ensemble import RandomForestRegressor
from sklearn.neural_network import MLPRegressor
from sklearn.svm import SVR
from sklearn.dummy import DummyRegressor
from xgboost import XGBRegressor

from variaveis import INPUT_PATHS, OUTPUT_PATHS, FEATURE_COLS

# 1) Cria diretórios de saída
os.makedirs("results/figures", exist_ok=True)
os.makedirs("data/generated", exist_ok=True)

# 2) Carrega datasets pré-processados
df_pib = pd.read_csv(INPUT_PATHS.pib_municipal,       encoding='utf-8-sig')
df_gee = pd.read_csv(INPUT_PATHS.cobertura_municipal, encoding='utf-8-sig')
df_alertas = pd.read_csv(INPUT_PATHS.alertas,             encoding='utf-8-sig')

# 3) Extrai 'municipio' de crossedCitiesList e o 'ano'


def extract_municipio(crossed_str):
    try:
        recs = ast.literal_eval(crossed_str)
        for rec in recs:
            if rec.get('source', '').lower() == 'município':
                return rec.get('name')
    except Exception:
        return None


df_alertas['municipio'] = df_alertas['crossedCitiesList'].apply(
    extract_municipio)
df_alertas['ano'] = pd.to_datetime(df_alertas['detectedAt']).dt.year

# 4) Renomeia coluna de cobertura para GEE_tCO2e, se necessário
if 'GEE_tCO2e' not in df_gee.columns:
    if 'cobertura' in df_gee.columns:
        df_gee.rename(columns={'cobertura': 'GEE_tCO2e'}, inplace=True)
    else:
        raise KeyError("Coluna 'GEE_tCO2e' não encontrada em df_gee")

# 5) Agrupa dados por município e ano
df_desmat = (
    df_alertas
    .groupby(['municipio', 'ano'], as_index=False)['areaHa']
    .sum()
    .rename(columns={'areaHa': 'area_desmatada_ha'})
)

df_merge_pib = (
    df_pib
    .groupby(['municipio', 'ano'], as_index=False)['pib']
    .sum()
)

df_merge_gee = (
    df_gee
    .groupby(['municipio', 'ano'], as_index=False)['GEE_tCO2e']
    .sum()
)

# 6) Merge final
df_final = pd.merge(df_merge_pib, df_merge_gee, on=[
                    'municipio', 'ano'], how='outer')
df_final = pd.merge(df_final,    df_desmat,     on=[
                    'municipio', 'ano'], how='outer')

# 7) Seleciona colunas e exporta CSV consolidado
df_final = df_final[['municipio', 'ano',
                     'pib', 'GEE_tCO2e', 'area_desmatada_ha']]
df_final.to_csv(
    'data/generated/carbono_serra_penitente.csv',
    index=False,
    encoding='utf-8-sig'
)
print('✅ Dataset final gerado: data/generated/carbono_serra_penitente.csv')

# --- Removida aqui a geração de figuras 1–3, pois são recriadas em 05_gerar_figuras_carbono.py ---

# 8) Predição de preço de carbono e salvamento de métricas

# 8.1) Carrega preços de carbono (EU ETS)
price_raw = pd.read_excel(
    INPUT_PATHS.carbon_prices_raw,
    sheet_name=0,
    header=1,
    engine='openpyxl'
)
instrument_col = 'Instrument name'
# identifica anos nas colunas
year_cols = [c for c in price_raw.columns if isinstance(c, int)]

df_price = (
    price_raw
    .melt(id_vars=[instrument_col], value_vars=year_cols,
          var_name='ano', value_name='carbon_price_usd')
    .query(f"`{instrument_col}` == 'EU ETS'")
)
df_price['ano'] = df_price['ano'].astype(int)
df_price['carbon_price_usd'] = pd.to_numeric(
    df_price['carbon_price_usd'], errors='coerce')
df_price = df_price[['ano', 'carbon_price_usd']].dropna().drop_duplicates()

# 8.2) Mescla preços ao dataset
df_model = df_final.merge(df_price, on='ano', how='inner')

# 8.3) Agrega único por município-ano
df_model = (
    df_model
    .groupby(['municipio', 'ano'], as_index=False)
    .agg({
        'pib': 'first',
        'GEE_tCO2e': 'sum',
        'area_desmatada_ha': 'sum',
        'carbon_price_usd': 'first'
    })
)

# 8.4) Prepara features e target
for feat in FEATURE_COLS:
    df_model[feat] = pd.to_numeric(df_model[feat], errors='coerce').fillna(0)
X = df_model[FEATURE_COLS]
y = df_model['carbon_price_usd']

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)
scaler = StandardScaler()
X_train_s = scaler.fit_transform(X_train)
X_test_s = scaler.transform(X_test)

# 8.5) Define e treina modelos, coleta métricas
models = {
    'Linear Regression': LinearRegression(),
    'Random Forest':     RandomForestRegressor(random_state=42),
    'KNN':               KNeighborsRegressor(),
    'Decision Tree':     DecisionTreeRegressor(random_state=42),
    'MLP Regressor':     MLPRegressor(max_iter=1000, random_state=42),
    'Lasso':             Lasso(alpha=0.01, random_state=42),
    'SVR':               SVR(kernel='rbf'),
    'Dummy':             DummyRegressor(),
    'XGBoost':           XGBRegressor(random_state=42)
}

results = []
for name, model in models.items():
    model.fit(X_train_s, y_train)
    preds = model.predict(X_test_s)
    results.append({
        'model': name,
        'R2':    r2_score(y_test, preds),
        'MSE':   mean_squared_error(y_test, preds)
    })

# 8.6) Salva métricas em CSV
df_res = pd.DataFrame(results)
df_res.to_csv(
    OUTPUT_PATHS.model_results_csv,
    index=False,
    encoding='utf-8-sig'
)
print(f"✅ Métricas salvas em {OUTPUT_PATHS.model_results_csv}")
