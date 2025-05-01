# path: src/filtrar_desmatamento_serra_penitente.py

import pandas as pd
import os
import matplotlib.pyplot as plt
import seaborn as sns

# Criar diretório de saída
os.makedirs("data/generated", exist_ok=True)
os.makedirs("results/figures", exist_ok=True)

# Carregar o arquivo gerado pelo MapBiomas
input_path = "data/downloads/alertas_mapbiomas.csv"
df = pd.read_csv(input_path)

# Exibir colunas disponíveis
print("Colunas disponíveis:", df.columns.tolist())

# Definir municípios alvo
municipios_alvo = ["Balsas", "Tasso Fragoso", "Alto Parnaíba"]

# Verificar possíveis nomes de colunas
municipio_col = None
ano_col = None
area_col = None

# Inferir nomes das colunas automaticamente
for col in df.columns:
    if "municip" in col.lower():
        municipio_col = col
    if "ano" in col.lower() or "year" in col.lower():
        ano_col = col
    if "area" in col.lower() and ("ha" in col.lower() or "desmatada" in col.lower()):
        area_col = col

# Garantir que encontramos as colunas
if not all([municipio_col, ano_col, area_col]):
    raise ValueError(
        "Não foi possível identificar as colunas corretas. Verifique o CSV.")

print(
    f"Usando as colunas: Município = {municipio_col}, Ano = {ano_col}, Área Desmatada = {area_col}")

# Filtrar apenas os dados dos 3 municípios
df_filtrado = df[df[municipio_col].isin(municipios_alvo)]

# Agrupar por município e ano
df_agrupado = df_filtrado.groupby([municipio_col, ano_col])[
    area_col].sum().reset_index()

# Renomear colunas padronizadas
df_agrupado.columns = ["municipio", "ano", "area_desmatada_ha"]

# Salvar CSV
output_path = "data/generated/desmatamento_serra_penitente.csv"
df_agrupado.to_csv(output_path, index=False)

print(f"✅ Dataset salvo em: {output_path}")
print(df_agrupado.head())

# Gerar gráfico de linha
plt.figure(figsize=(10, 6))
sns.lineplot(data=df_agrupado, x="ano", y="area_desmatada_ha",
             hue="municipio", marker="o")
plt.title("Evolução do Desmatamento nos Municípios da Serra do Penitente (2000-2023)")
plt.xlabel("Ano")
plt.ylabel("Área Desmatada (ha)")
plt.grid(True)
plt.legend(title="Município")
plt.tight_layout()

# Salvar figura
graph_output_path = "results/figures/evolucao_desmatamento_serra_penitente.png"
plt.savefig(graph_output_path)
plt.close()

print(f"✅ Gráfico salvo em: {graph_output_path}")
