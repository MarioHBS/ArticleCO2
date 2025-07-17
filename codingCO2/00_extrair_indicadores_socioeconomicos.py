import pandas as pd
from variaveis import INPUT_PATHS, PROCESSED_PATHS

# Carregar o arquivo de indicadores socioeconômicos
df_socio = pd.read_excel(INPUT_PATHS.indicadores_socioeconomicos)
print(f"Shape inicial: {df_socio.shape}")

# 1. Filtrar dados relevantes dos 3 municípios de interesse
municipios_interesse = ['Alto Parnaíba (MA)', 'Balsas (MA)', 'Tasso Fragoso (MA)']
df_socio = df_socio[df_socio['Territorialidades'].isin(municipios_interesse)].copy()
print(f"Shape após filtro de municípios: {df_socio.shape}")

if df_socio.empty:
    print("Nenhum município de interesse encontrado no arquivo. O script será encerrado.")
    exit()

# Renomear coluna para facilitar o merge
df_socio.rename(columns={'Territorialidades': 'municipio'}, inplace=True)

# 2. Selecionar indicadores-chave
indicadores_selecionados = [
    'municipio',
    'IDHM 2010',
    'IDHM Renda 2010',
    'IDHM Longevidade 2010',
    'IDHM Educação 2010',
    'Renda per capita 2010',
    'Taxa de analfabetismo - 18 a 24 anos 2010',
    'Taxa de analfabetismo - 25 a 29 anos 2010'
]

# Garantir que todas as colunas selecionadas existam
colunas_existentes = [col for col in indicadores_selecionados if col in df_socio.columns]
if len(colunas_existentes) != len(indicadores_selecionados):
    print(f"Aviso: colunas não encontradas: {set(indicadores_selecionados) - set(colunas_existentes)}")

df_filtrado = df_socio[colunas_existentes]
print(f"Shape após seleção de colunas: {df_filtrado.shape}")

# 3. Harmonizar períodos temporais
anos_interesse = range(2002, 2022)
df_final = pd.DataFrame()

for ano in anos_interesse:
    df_ano = df_filtrado.copy()
    df_ano['ano'] = ano
    df_final = pd.concat([df_final, df_ano])

print(f"Shape final: {df_final.shape}")

# Salvar os dados processados
output_path = PROCESSED_PATHS.indicadores_socioeconomicos
df_final.to_csv(output_path, index=False, encoding='utf-8-sig')

print(f"Dados socioeconômicos processados e salvos em: {output_path}")