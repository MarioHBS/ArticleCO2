# 06_treinar_modelo_carbono.py
# Treinamento e avaliação de modelos de precificação de carbono usando dados do IBGE e preços do Carbon Pricing Dashboard (WB)

import os
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LinearRegression, Lasso
from sklearn.ensemble import RandomForestRegressor
from sklearn.neural_network import MLPRegressor
from sklearn.svm import SVR
from xgboost import XGBRegressor
from sklearn.metrics import r2_score, mean_squared_error

# 1) Criar diretório de resultados
os.makedirs("results", exist_ok=True)

# 2) Carregar dataset consolidado (PIB, GEE, desmatamento)
df = pd.read_csv("data/generated/carbono_serra_penitente.csv",
                 encoding="utf-8-sig")
print("Colunas iniciais:", df.columns.tolist())

# 3) Renomear colunas para compatibilidade com o modelo
df.rename(columns={
    'pib': 'gdp',
    'GEE_tCO2e': 'total_ghg',
    'area_desmatada_ha': 'shape_Area'
}, inplace=True)
print("Após renomeação:", df.columns.tolist())

# 4) Carregar preços de carbono do World Bank Carbon Pricing Dashboard
xlsx_path = "data/raw/carbon-prices-latest.xlsx"
sheet = "Compliance_Price"
xls = pd.ExcelFile(xlsx_path)
# Header na segunda linha (índice 1)
df_price_raw = pd.read_excel(xls, sheet_name=sheet, header=1)

# Identificar colunas de ano
year_cols = [col for col in df_price_raw.columns if (
    isinstance(col, str) and col.isdigit()) or isinstance(col, int)]

# Transformar em formato longo
df_price = df_price_raw.melt(
    id_vars=["Name of the initiative"],
    value_vars=year_cols,
    var_name="ano",
    value_name="carbon_price_usd"
)
# Filtrar instrumento de compliance (ex: "EU ETS")
instrument = "EU ETS"
df_price = df_price[df_price["Name of the initiative"] == instrument]
# Converter tipos
df_price["ano"] = df_price["ano"].astype(int)
df_price["carbon_price_usd"] = pd.to_numeric(
    df_price["carbon_price_usd"], errors="coerce")
df_price = df_price[["ano", "carbon_price_usd"]].dropna().drop_duplicates()
print(f"Preços disponíveis: {df_price['ano'].min()}–{df_price['ano'].max()}")

# 5) Mesclar preços ao dataframe principal
# Faz merge por 'ano'
df = df.merge(df_price, on="ano", how="inner")
print("Colunas após merge:", df.columns.tolist())

# 6) Selecionar features e target e remover missing values
feature_cols = ['total_ghg', 'shape_Area', 'gdp']
target_col = 'carbon_price_usd'
df = df.dropna(subset=feature_cols + [target_col])
X = df[feature_cols]
y = df[target_col]

# 7) Divisão treino/teste
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# 8) Padronização dos dados
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# 9) Definir e treinar múltiplos modelos
models = {
    'Linear Regression': LinearRegression(),
    'Random Forest': RandomForestRegressor(random_state=42),
    'MLP Regressor': MLPRegressor(max_iter=1000, random_state=42),
    'Lasso': Lasso(alpha=0.01, random_state=42),
    'SVR': SVR(kernel='rbf'),
    'XGBoost': XGBRegressor(random_state=42)
}

results = []
for name, model in models.items():
    print(f"Treinando {name}...")
    model.fit(X_train_scaled, y_train)
    preds = model.predict(X_test_scaled)
    r2 = r2_score(y_test, preds)
    mse = mean_squared_error(y_test, preds)
    print(f"{name} -> R2: {r2:.3f}, MSE: {mse:.3f}")
    results.append({'model': name, 'R2': r2, 'MSE': mse})

# 10) Salvar resultados
df_results = pd.DataFrame(results)
df_results.to_csv("results/carbon_model_results.csv", index=False)
print("✅ Resultados salvos em results/carbon_model_results.csv")
