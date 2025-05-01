# path: src/gerar_todas_figuras_carbono.py

import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import pandas as pd
import os
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error
from sklearn.model_selection import train_test_split

# Definindo o caminho base para salvar as figuras
base_path = 'results/figures/'
os.makedirs(base_path, exist_ok=True)

# --- Dados simulados para ilustração --- #
# Idealmente aqui carregaríamos seu dataset real
# df = pd.read_csv('data/generated/carbono_serra_penitente.csv')

np.random.seed(42)
y_true = np.random.uniform(7, 16, 50)
y_pred = y_true + np.random.normal(0, 1, 50)

X_sim = pd.DataFrame({
    'GEE_tCO2e': np.random.uniform(1e5, 5e5, 50),
    'area_desmatada_ha': np.random.uniform(100, 1000, 50),
    'pib': np.random.uniform(1e9, 5e9, 50),
})

# --- Figura 1: EQM dos Modelos --- #
modelos = ['Baseline', 'LR', 'MLP', 'KNN', 'RF', 'DT']
eqm = [0.15, 0.12, 0.08, 0.05, 0.02, 0.01]

fig1_path = base_path + 'figura1_eqm_modelos.png'

plt.figure(figsize=(8, 5))
colors = sns.color_palette('husl', len(modelos))
colors[0] = 'orange'
sns.barplot(x=modelos, y=eqm, palette=colors)
plt.ylabel('Erro Quadrático Médio (EQM)')
plt.xlabel('Modelos')
plt.tight_layout()
plt.savefig(fig1_path)
plt.close()

# --- Figura 2: Correlação entre Atributos --- #
atributos = ['GEE_tCO2e', 'area_desmatada_ha', 'pib', 'carbon_price_usd']
correlacoes = np.corrcoef(X_sim.T)

fig2_path = base_path + 'figura2_correlacoes.png'

plt.figure(figsize=(8, 6))
sns.heatmap(correlacoes, annot=True, xticklabels=atributos,
            yticklabels=atributos, cmap='coolwarm')
plt.tight_layout()
plt.savefig(fig2_path)
plt.close()

# --- Figura 3: Dispersão Real vs Predito --- #
fig3_path = base_path + 'figura3_dispersion_real_predito.png'

plt.figure(figsize=(7, 7))
plt.scatter(y_true, y_pred, alpha=0.7)
plt.plot([y_true.min(), y_true.max()], [y_true.min(), y_true.max()], 'r--')
plt.xlabel('Preço do Carbono Real (USD)')
plt.ylabel('Preço do Carbono Predito (USD)')
plt.title('Dispersão: Real vs Predito')
plt.tight_layout()
plt.savefig(fig3_path)
plt.close()

# --- Figura 4: Importância das Variáveis (Random Forest) --- #
model_rf = RandomForestRegressor(random_state=42)
model_rf.fit(X_sim, y_true)
importancias = model_rf.feature_importances_

fig4_path = base_path + 'figura4_importancia_variaveis.png'

plt.figure(figsize=(8, 6))
sns.barplot(x=X_sim.columns, y=importancias)
plt.ylabel('Importância Relativa')
plt.xlabel('Variáveis')
plt.title('Importância das Variáveis no Modelo Random Forest')
plt.tight_layout()
plt.savefig(fig4_path)
plt.close()

# --- Figura 5: Evolução Temporal do Preço do Carbono --- #
anos = np.arange(2018, 2024)
precos_estimados = [7, 8, 9, 11, 16, 16]

fig5_path = base_path + 'figura5_evolucao_preco_carbono.png'

plt.figure(figsize=(8, 6))
plt.plot(anos, precos_estimados, marker='o')
plt.xlabel('Ano')
plt.ylabel('Preço Estimado do Carbono (USD)')
plt.title('Evolução Temporal do Preço do Carbono')
plt.grid(True)
plt.tight_layout()
plt.savefig(fig5_path)
plt.close()

print("✅ Todas as figuras geradas com sucesso!")
