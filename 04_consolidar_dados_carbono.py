# 04_consolidar_dados_carbono.py
# Consolida PIB, cobertura MapBiomas e alertas de desmatamento

import os
import ast
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# 1) Cria diretórios de saída
os.makedirs("results/figures", exist_ok=True)
os.makedirs("data/generated", exist_ok=True)

# 2) Carrega datasets pré-processados
# PIB municipal
df_pib = pd.read_csv(
    "data/partial/pib_municipal_serra_penitente_ibge.csv", encoding="utf-8-sig")
# Cobertura MapBiomas (long form)
df_gee = pd.read_csv(
    "data/partial/mapbiomas_cobertura_municipal_long.csv", encoding="utf-8-sig")
# Alertas de desmatamento
df_alertas = pd.read_csv(
    "data/partial/alertas_serra_penitente.csv", encoding="utf-8-sig")

# 3) Processa alertas para agrupar área por município e ano
if df_alertas['crossedCitiesList'].dtype == object:
    df_alertas['crossedCitiesList'] = df_alertas['crossedCitiesList'].apply(
        ast.literal_eval)

df_alertas = df_alertas.explode('crossedCitiesList')
# Extrai nome do município
df_alertas['municipio'] = df_alertas['crossedCitiesList'].apply(
    lambda x: x.get('name'))

# Filtra apenas municípios-alvo (presentes em df_pib)
municipios_target = df_pib['municipio'].unique().tolist()
df_alertas = df_alertas[df_alertas['municipio'].isin(municipios_target)].copy()

# Extrai ano da data de detecção
df_alertas['ano'] = pd.to_datetime(df_alertas['detectedAt']).dt.year

# Agrupa soma de área desmatada (ha)
df_desmat = (
    df_alertas
    .groupby(['municipio', 'ano'], as_index=False)
    ['areaHa']
    .sum()
    .rename(columns={'areaHa': 'area_desmatada_ha'})
)

# 4) Ajusta coluna de PIB em df_pib
# Identifica coluna de Produto Interno Bruto e renomeia para 'pib'
gdp_cols = [col for col in df_pib.columns if 'Produto Interno Bruto' in col]
if not gdp_cols:
    raise KeyError("Coluna de Produto Interno Bruto não encontrada em df_pib")
df_pib.rename(columns={gdp_cols[0]: 'pib'}, inplace=True)

# 5) Prepara dataframes para merge
# PIB
df_merge_pib = df_pib[['municipio', 'ano', 'pib']]
# GEE: renomeia 'cobertura' se presente
df_gee.rename(columns={'cobertura': 'GEE_tCO2e'}, inplace=True)
df_merge_gee = df_gee[['municipio', 'ano', 'GEE_tCO2e']]

# 6) Realiza os merges
df_final = pd.merge(df_merge_pib, df_merge_gee, on=[
                    'municipio', 'ano'], how='outer')
df_final = pd.merge(df_final, df_desmat, on=['municipio', 'ano'], how='outer')

# 7) Seleciona e ordena colunas finais
df_final = df_final[['municipio', 'ano',
                     'pib', 'GEE_tCO2e', 'area_desmatada_ha']]

# 8) Exporta para CSV com encoding para preservar acentuação
df_final.to_csv('data/generated/carbono_serra_penitente.csv',
                index=False, encoding='utf-8-sig')
print('✅ Dataset final gerado: data/generated/carbono_serra_penitente.csv')

# --- Gráficos --- #
# Evolução do PIB
plt.figure(figsize=(10, 6))
sns.lineplot(data=df_final, x='ano', y='pib', hue='municipio', marker='o')
plt.title('Evolução do PIB - Serra do Penitente')
plt.ylabel('PIB (R$)')
plt.xlabel('Ano')
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig('results/figures/evolucao_pib_serra_penitente.png')
plt.close()

# Evolução de GEE
plt.figure(figsize=(10, 6))
sns.lineplot(data=df_final, x='ano', y='GEE_tCO2e',
             hue='municipio', marker='o')
plt.title('Evolução de GEE - Serra do Penitente')
plt.ylabel('GEE (tCO2e)')
plt.xlabel('Ano')
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig('results/figures/evolucao_gee_serra_penitente.png')
plt.close()

# Evolução da área desmatada
plt.figure(figsize=(10, 6))
sns.lineplot(data=df_final, x='ano', y='area_desmatada_ha',
             hue='municipio', marker='o')
plt.title('Evolução da Área Desmatada - Serra do Penitente')
plt.ylabel('Área Desmatada (ha)')
plt.xlabel('Ano')
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig('results/figures/evolucao_desmatamento_serra_penitente.png')
plt.close()
