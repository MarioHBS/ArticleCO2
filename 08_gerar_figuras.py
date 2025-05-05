# Este script gera duas figuras para o artigo sobre o modelo de previsão do
# preço do carbono.
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import os

# Figura 1: EQM dos modelos no treinamento
modelos = ['Baseline', 'LR', 'MLP', 'KNN', 'RF', 'DT']
eqm = [0.15, 0.12, 0.08, 0.05, 0.02, 0.01]  # valores ilustrativos

# Definindo o caminho base para salvar as figuras
base_path = 'results/figures/'
os.makedirs(base_path, exist_ok=True)

# Ajustando os caminhos para salvar as figuras reutilizando a variável base_path
fig1_path = base_path + 'figura1_eqm_modelos.png'
fig2_path = base_path + 'figura2_correlacoes.png'

plt.figure(figsize=(8, 5))
# Adicionando cores diferentes para cada coluna na Figura 1
colors = sns.color_palette('husl', len(modelos))
# Ajustando a cor da primeira coluna para laranja
colors[0] = 'orange'
sns.barplot(x=modelos, y=eqm, palette=colors)
plt.ylabel('Erro Quadrático Médio (EQM)')
plt.xlabel('Modelos')
# plt.title('Figura 1 - EQM dos Modelos no Conjunto de Treinamento')
plt.tight_layout()
plt.savefig(fig1_path)
plt.close()

# Figura 2: Mapa de calor das correlações
atributos = ['Emissões GEE', 'Área Desmatada', 'PIB', 'Preço do Carbono']
correlacoes = np.array([
    [1.00,  0.75,  0.65,  0.80],
    [0.75,  1.00,  0.60,  0.78],
    [0.65,  0.60,  1.00,  0.72],
    [0.80,  0.78,  0.72,  1.00]
])

plt.figure(figsize=(8, 6))
sns.heatmap(correlacoes, annot=True, xticklabels=atributos,
            yticklabels=atributos, cmap='coolwarm')
# plt.title('Figura 2 - Correlação entre Atributos e Preço do Carbono')
plt.tight_layout()
plt.savefig(fig2_path)
plt.close()

fig1_path, fig2_path
