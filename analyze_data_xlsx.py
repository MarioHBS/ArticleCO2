import pandas as pd
import numpy as np
import sys

# Redirect output to a file
sys.stdout = open('analysis_results.txt', 'w', encoding='utf-8')

# Carregar o arquivo data.xlsx
file_path = 'data/raw/indicadores_socioeconomicos_serra_penitente.xlsx'
print(f"Analisando o arquivo: {file_path}")
print("="*60)

try:
    # Ler o arquivo Excel
    df = pd.read_excel(file_path)
    
    print(f"Dimensões do dataset: {df.shape}")
    print(f"Número de linhas: {df.shape[0]}")
    print(f"Número de colunas: {df.shape[1]}")
    print("\n" + "="*60)
    
    # Mostrar todas as colunas
    print("\nTodas as colunas:")
    for i, col in enumerate(df.columns, 1):
        print(f"{i:2d}. {col}")
    
    # Buscar por colunas relacionadas ao IDH
    print("\n" + "="*60)
    print("BUSCA POR IDH E INDICADORES SOCIAIS:")
    print("="*60)
    
    # Termos relacionados ao IDH
    idh_terms = ['idh', 'desenvolvimento', 'humano', 'longevidade', 'educacao', 'educação', 'renda']
    
    idh_columns = []
    for col in df.columns:
        col_lower = str(col).lower()
        for term in idh_terms:
            if term in col_lower:
                idh_columns.append(col)
                break
    
    if idh_columns:
        print(f"\nColunas relacionadas ao IDH encontradas ({len(idh_columns)}):")
        for i, col in enumerate(idh_columns, 1):
            print(f"{i:2d}. {col}")
    else:
        print("\nNenhuma coluna explicitamente relacionada ao IDH foi encontrada.")
    
    # Buscar outros indicadores sociais
    print("\n" + "-"*40)
    print("OUTROS INDICADORES SOCIAIS:")
    print("-"*40)
    
    social_terms = ['social', 'pobreza', 'população', 'populacao', 'demografico', 'demográfico', 
                   'saude', 'saúde', 'mortalidade', 'natalidade', 'alfabetizacao', 'alfabetização',
                   'analfabetismo', 'escolaridade', 'emprego', 'desemprego', 'trabalho', 'atividade']
    
    social_columns = []
    for col in df.columns:
        col_lower = str(col).lower()
        for term in social_terms:
            if term in col_lower and col not in idh_columns:
                social_columns.append(col)
                break
    
    if social_columns:
        print(f"\nOutros indicadores sociais encontrados ({len(social_columns)}):")
        for i, col in enumerate(social_columns[:20], 1):  # Mostrar apenas os primeiros 20
            print(f"{i:2d}. {col}")
        if len(social_columns) > 20:
            print(f"... e mais {len(social_columns) - 20} colunas")
    
    # Verificar se há coluna de territorialidades/municípios
    print("\n" + "-"*40)
    print("COLUNAS DE IDENTIFICAÇÃO:")
    print("-"*40)
    
    location_terms = ['territorio', 'territorialidade', 'municipio', 'município', 'cidade', 'local', 'codigo', 'código']
    location_columns = []
    
    for col in df.columns:
        col_lower = str(col).lower()
        for term in location_terms:
            if term in col_lower:
                location_columns.append(col)
                break
    
    if location_columns:
        print(f"\nColunas de identificação encontradas:")
        for col in location_columns:
            print(f"- {col}")
            # Mostrar valores únicos se for uma coluna de identificação
            unique_vals = df[col].unique()
            if len(unique_vals) <= 10:
                print(f"  Valores únicos: {list(unique_vals)}")
            else:
                print(f"  Número de valores únicos: {len(unique_vals)}")
                print(f"  Primeiros valores: {list(unique_vals[:5])}")
    
    # Mostrar informações sobre anos/períodos
    print("\n" + "-"*40)
    print("INFORMAÇÕES TEMPORAIS:")
    print("-"*40)
    
    year_columns = []
    for col in df.columns:
        col_lower = str(col).lower()
        if 'ano' in col_lower or 'year' in col_lower or any(str(year) in str(col) for year in range(2000, 2025)):
            year_columns.append(col)
    
    if year_columns:
        print(f"\nColunas relacionadas a anos encontradas:")
        for col in year_columns[:10]:  # Mostrar apenas as primeiras 10
            print(f"- {col}")
    
    # Mostrar amostra dos dados
    print("\n" + "="*60)
    print("AMOSTRA DOS DADOS:")
    print("="*60)
    print("\nPrimeiras 3 linhas:")
    print(df.head(3).to_string())
    
    # Informações sobre valores faltantes
    print("\n" + "-"*40)
    print("VALORES FALTANTES:")
    print("-"*40)
    missing_info = df.isnull().sum()
    missing_cols = missing_info[missing_info > 0]
    
    if len(missing_cols) > 0:
        print(f"\nColunas com valores faltantes ({len(missing_cols)} de {len(df.columns)}):")
        for col, missing_count in missing_cols.head(10).items():
            percentage = (missing_count / len(df)) * 100
            print(f"- {col}: {missing_count} ({percentage:.1f}%)")
        if len(missing_cols) > 10:
            print(f"... e mais {len(missing_cols) - 10} colunas com valores faltantes")
    else:
        print("\nNenhum valor faltante encontrado.")
    
    print("\n" + "="*60)
    print("RESUMO DA ANÁLISE:")
    print("="*60)
    print(f"✓ Dataset carregado com sucesso")
    print(f"✓ Dimensões: {df.shape[0]} linhas × {df.shape[1]} colunas")
    print(f"✓ Colunas relacionadas ao IDH: {len(idh_columns)}")
    print(f"✓ Outros indicadores sociais: {len(social_columns)}")
    print(f"✓ Colunas de identificação: {len(location_columns)}")
    print(f"✓ Colunas temporais: {len(year_columns)}")
    
except Exception as e:
    print(f"Erro ao carregar o arquivo: {e}")
    print("Verifique se o arquivo existe e está no formato correto.")
finally:
    # Close the file
    if 'sys' in locals() and sys.stdout != sys.__stdout__:
        sys.stdout.close()
        # Restore original stdout
        sys.stdout = sys.__stdout__