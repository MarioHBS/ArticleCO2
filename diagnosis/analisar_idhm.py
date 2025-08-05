import pandas as pd
import os

# Carrega o arquivo IDHM
df_idhm = pd.read_excel('data/raw/idhm_municipios_serra_penitente.xlsx')

# Salva o arquivo na pasta diagnosis
output_file = os.path.join('diagnosis', 'analise_idhm_output.txt')

# Executar a análise e salvar diretamente no arquivo
try:
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("=== ANALISE DO ARQUIVO IDHM ===\n")
        f.write(f"Shape: {df_idhm.shape}\n")
        f.write("\nColunas disponiveis:\n")
        for i, col in enumerate(df_idhm.columns):
            # Remove caracteres especiais que podem causar problemas
            col_clean = str(col).encode('ascii', 'ignore').decode('ascii')
            f.write(f"{i+1:2d}. {col_clean}\n")
        
        f.write("\nTipos de dados:\n")
        for col, dtype in df_idhm.dtypes.items():
            col_clean = str(col).encode('ascii', 'ignore').decode('ascii')
            f.write(f"{col_clean}: {dtype}\n")
        
        f.write("\nValores unicos por coluna (primeiras 10 colunas):\n")
        for col in df_idhm.columns[:10]:
            unique_count = df_idhm[col].nunique()
            col_clean = str(col).encode('ascii', 'ignore').decode('ascii')
            f.write(f"{col_clean}: {unique_count} valores unicos\n")
        
        f.write("\nVerificacao de municipios:\n")
        if 'municipio' in df_idhm.columns:
            municipios = df_idhm['municipio'].unique()
            f.write(f"Municipios encontrados: {len(municipios)}\n")
        elif 'Municipio' in df_idhm.columns:
            municipios = df_idhm['Municipio'].unique()
            f.write(f"Municipios encontrados: {len(municipios)}\n")
        else:
            f.write("Coluna de municipio nao identificada claramente\n")
            primeiras_cols = [str(col).encode('ascii', 'ignore').decode('ascii') for col in df_idhm.columns[:5]]
            f.write(f"Primeiras colunas: {primeiras_cols}\n")
        
        f.write("\nVerificacao de anos:\n")
        if 'ano' in df_idhm.columns:
            anos = df_idhm['ano'].unique()
            f.write(f"Anos encontrados: {sorted(anos)}\n")
        elif 'Ano' in df_idhm.columns:
            anos = df_idhm['Ano'].unique()
            f.write(f"Anos encontrados: {sorted(anos)}\n")
        else:
            # Procura por colunas que podem ser anos
            year_cols = [col for col in df_idhm.columns if str(col).isdigit() and 1990 <= int(str(col)) <= 2030]
            f.write(f"Possiveis colunas de ano: {year_cols}\n")
        
        f.write("\nIndicadores IDHM disponiveis:\n")
        idhm_cols = [col for col in df_idhm.columns if 'idhm' in str(col).lower() or 'idh' in str(col).lower()]
        idhm_cols_clean = [str(col).encode('ascii', 'ignore').decode('ascii') for col in idhm_cols]
        f.write(f"Colunas relacionadas ao IDHM: {idhm_cols_clean}\n")
        
        f.write("\nResumo estatistico:\n")
        f.write(f"Total de linhas: {len(df_idhm)}\n")
        f.write(f"Total de colunas: {len(df_idhm.columns)}\n")
        f.write(f"Colunas numericas: {len(df_idhm.select_dtypes(include=['number']).columns)}\n")
        
except Exception as e:
    print(f"Erro ao salvar arquivo: {e}")
    # Tenta salvar com codificação mais simples
    with open(output_file, 'w', encoding='latin-1') as f:
        f.write("=== ANALISE DO ARQUIVO IDHM ===\n")
        f.write(f"Shape: {df_idhm.shape}\n")
        f.write(f"Total de colunas: {len(df_idhm.columns)}\n")

print(f"Analise salva em: {output_file}")