#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para consolidar dados de PIB, GEE, alertas de desmatamento e IDHM
para predição do preço de carbono na região da Serra do Penitente.

Este script expande o pipeline original incluindo indicadores do IDHM
como features adicionais para melhorar a predição do preço de carbono.
"""
import os
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LinearRegression, Lasso
from sklearn.ensemble import RandomForestRegressor
from sklearn.neighbors import KNeighborsRegressor
from sklearn.tree import DecisionTreeRegressor
from sklearn.neural_network import MLPRegressor
from sklearn.svm import SVR
from sklearn.dummy import DummyRegressor
from xgboost import XGBRegressor
from sklearn.metrics import r2_score, mean_squared_error
import warnings
warnings.filterwarnings('ignore')

# Criar pasta results se não existir
os.makedirs('results', exist_ok=True)

# Importar configurações
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from variaveis import (
    MUNICIPIOS_ALVO, REGIAO_ESTUDO,
    INPUT_PATHS, GENERATED_PATHS, RESULT_PATHS, FEATURE_COLS, FEATURE_COLS_EXPANDIDO
)

def carregar_dados_idhm():
    """
    Carrega e processa os dados do IDHM.
    
    Returns:
        pd.DataFrame: DataFrame com dados do IDHM processados
    """
    print("Carregando dados do IDHM...")
    
    # Carregar arquivo IDHM
    df_idhm = pd.read_excel(INPUT_PATHS.idhm)
    
    print(f"Shape original do IDHM: {df_idhm.shape}")
    print(f"Colunas disponíveis: {len(df_idhm.columns)}")
    
    # Identificar coluna de territorialidades (municípios)
    col_municipio = 'Territorialidades'
    
    # Filtrar apenas os municípios de interesse
    municipios_interesse = [mun.nome for mun in MUNICIPIOS_ALVO]
    df_idhm_filtrado = df_idhm[df_idhm[col_municipio].isin(municipios_interesse)].copy()
    
    print(f"Municípios encontrados no IDHM: {df_idhm_filtrado[col_municipio].unique()}")
    
    # Selecionar indicadores IDHM principais para os anos disponíveis
    # Focar nos indicadores mais relevantes: IDHM geral, Renda, Educação, Longevidade
    indicadores_principais = [
        'IDHM 2010', 'IDHM Renda 2010', 'IDHM Educação 2010', 'IDHM Longevidade 2010',
        'IDHM 2000', 'IDHM Renda 2000', 'IDHM Educação 2000', 'IDHM Longevidade 2000'
    ]
    
    # Verificar quais indicadores estão disponíveis
    indicadores_disponiveis = [col for col in indicadores_principais if col in df_idhm.columns]
    print(f"Indicadores IDHM disponíveis: {indicadores_disponiveis}")
    
    # Selecionar colunas relevantes
    colunas_selecionadas = [col_municipio] + indicadores_disponiveis
    df_idhm_selecionado = df_idhm_filtrado[colunas_selecionadas].copy()
    
    # Converter para formato longo para facilitar merge com outros dados
    dados_processados = []
    
    for _, row in df_idhm_selecionado.iterrows():
        municipio = row[col_municipio]
        
        # Extrair dados para cada ano disponível
        for ano in [2000, 2010]:
            registro = {
                'municipio': municipio,
                'ano': ano
            }
            
            # Adicionar indicadores do ano específico
            for indicador in indicadores_disponiveis:
                if str(ano) in indicador:
                    # Simplificar nome do indicador
                    nome_simples = indicador.replace(f' {ano}', '').replace('IDHM ', 'idhm_')
                    nome_simples = nome_simples.lower().replace(' ', '_')
                    registro[nome_simples] = row[indicador]
            
            dados_processados.append(registro)
    
    df_idhm_processado = pd.DataFrame(dados_processados)
    
    # Remover registros com todos os valores NaN (exceto municipio e ano)
    colunas_indicadores = [col for col in df_idhm_processado.columns if col not in ['municipio', 'ano']]
    df_idhm_processado = df_idhm_processado.dropna(subset=colunas_indicadores, how='all')
    
    print(f"Shape final do IDHM processado: {df_idhm_processado.shape}")
    print(f"Colunas do IDHM processado: {df_idhm_processado.columns.tolist()}")
    
    return df_idhm_processado

def consolidar_dados_com_idhm():
    """
    Consolida dados de PIB, GEE, alertas e IDHM.
    
    Returns:
        pd.DataFrame: DataFrame consolidado com todas as features
    """
    print("Iniciando consolidação de dados com IDHM...")
    
    # 1. Carregar dados existentes (PIB, GEE, alertas)
    print("Carregando dados de PIB...")
    try:
        df_pib = pd.read_csv(INPUT_PATHS.pib, encoding='utf-8', sep=',')
        print(f"PIB carregado: {df_pib.shape}")
    except Exception as e:
        print(f"Erro ao carregar PIB com utf-8: {e}")
        try:
            df_pib = pd.read_csv(INPUT_PATHS.pib, encoding='latin-1', sep=',')
            print(f"PIB carregado com latin-1: {df_pib.shape}")
        except Exception as e2:
            print(f"Erro ao carregar PIB com latin-1: {e2}")
            raise
    
    # Usar dados consolidados de carbono em vez de mapbiomas
    print("Carregando dados consolidados de carbono...")
    df_carbono = pd.read_csv(GENERATED_PATHS.carbono_consolidado_csv)
    print(f"Dados de carbono carregados: {df_carbono.shape}")
    
    # Extrair GEE dos dados consolidados
    df_gee = df_carbono[['municipio', 'ano', 'GEE_tCO2e']].copy()
    print(f"GEE extraído dos dados consolidados: {df_gee.shape}")
    
    # Extrair alertas dos dados consolidados
    df_alertas = df_carbono[['municipio', 'ano', 'area_desmatada_ha']].copy()
    print(f"Alertas extraídos dos dados consolidados: {df_alertas.shape}")
    
    # 2. Carregar dados do IDHM
    df_idhm = carregar_dados_idhm()
    
    # 3. Processar dados existentes
    print("Processando dados do PIB...")
    # O arquivo PIB já tem as colunas corretas
    df_pib = df_pib[df_pib['municipio'].isin([m.nome for m in MUNICIPIOS_ALVO])]
    df_pib = df_pib[['municipio', 'ano', 'pib']].copy()
    
    # Processar GEE
    df_gee = df_gee.rename(columns={'municipality': 'municipio', 'year': 'ano', 'sum': 'GEE_tCO2e'})
    df_gee = df_gee[['municipio', 'ano', 'GEE_tCO2e']]
    
    # Processar alertas
    df_alertas = df_alertas.rename(columns={'municipality': 'municipio', 'year': 'ano', 'area_ha': 'area_desmatada_ha'})
    df_alertas = df_alertas.groupby(['municipio', 'ano'])['area_desmatada_ha'].sum().reset_index()
    
    # 4. Merge dos dados existentes
    print("Fazendo merge dos dados existentes...")
    df_consolidado = df_pib.merge(df_gee, on=['municipio', 'ano'], how='outer')
    df_consolidado = df_consolidado.merge(df_alertas, on=['municipio', 'ano'], how='outer')
    
    # 5. Integrar dados do IDHM
    print("Integrando dados do IDHM...")
    if not df_idhm.empty and 'municipio' in df_idhm.columns:
        df_consolidado = df_consolidado.merge(df_idhm, on=['municipio', 'ano'], how='left')
        print(f"Dados do IDHM integrados. Shape final: {df_consolidado.shape}")
    else:
        print("[AVISO] Dados do IDHM estão vazios ou sem coluna 'municipio'. Continuando sem IDHM...")
        # Adicionar colunas IDHM vazias para manter compatibilidade
        for col in FEATURE_COLS_EXPANDIDO:
            if col not in df_consolidado.columns and 'idhm' in col:
                df_consolidado[col] = None
    
    # 6. Filtrar apenas municípios de interesse
    municipios_interesse = [mun.nome for mun in MUNICIPIOS_ALVO]
    df_consolidado = df_consolidado[df_consolidado['municipio'].isin(municipios_interesse)]
    
    # 7. Preencher valores NaN
    df_consolidado = df_consolidado.fillna(0)
    
    print(f"Shape final dos dados consolidados: {df_consolidado.shape}")
    print(f"Colunas disponíveis: {df_consolidado.columns.tolist()}")
    print(f"Período coberto: {df_consolidado['ano'].min()} - {df_consolidado['ano'].max()}")
    
    return df_consolidado

def treinar_modelos_expandidos(df_consolidado):
    """
    Treina modelos de predição com features expandidas incluindo IDHM.
    
    Args:
        df_consolidado (pd.DataFrame): DataFrame com todas as features
    
    Returns:
        dict: Resultados dos modelos
    """
    print("Iniciando treinamento de modelos com features expandidas...")
    
    # Carregar preços de carbono
    print("[INFO] Carregando preços de carbono...")
    price_raw = pd.read_excel(
        INPUT_PATHS.carbon_prices_raw,
        sheet_name=0,
        header=1,
        engine='openpyxl'
    )
    instrument_col = 'Instrument name'
    # identifica anos nas colunas
    year_cols = [c for c in price_raw.columns if isinstance(c, int)]

    df_precos = (
        price_raw
        .melt(id_vars=[instrument_col], value_vars=year_cols,
              var_name='ano', value_name='preco_carbono')
        .query(f"`{instrument_col}` == 'EU ETS'")
    )
    df_precos['ano'] = df_precos['ano'].astype(int)
    df_precos['preco_carbono'] = pd.to_numeric(
        df_precos['preco_carbono'], errors='coerce')
    df_precos = df_precos[['ano', 'preco_carbono']].dropna().drop_duplicates()
    
    # Merge com preços de carbono
    df_final = df_consolidado.merge(df_precos, on='ano', how='inner')
    
    print(f"Dados finais para modelagem: {df_final.shape}")
    
    # Definir features expandidas
    feature_cols_base = ['pib', 'GEE_tCO2e', 'area_desmatada_ha']
    feature_cols_idhm = [col for col in df_final.columns if col.startswith('idhm_')]
    feature_cols_expandidas = feature_cols_base + feature_cols_idhm
    
    print(f"Features base: {feature_cols_base}")
    print(f"Features IDHM: {feature_cols_idhm}")
    print(f"Features expandidas: {feature_cols_expandidas}")
    
    # Preparar dados para modelagem
    X = df_final[feature_cols_expandidas]
    y = df_final['preco_carbono']
    
    # Remover linhas com NaN
    mask = ~(X.isna().any(axis=1) | y.isna())
    X = X[mask]
    y = y[mask]
    
    print(f"Dados para treinamento: {X.shape[0]} amostras, {X.shape[1]} features")
    
    if X.shape[0] == 0:
        print("Erro: Nenhuma amostra válida para treinamento!")
        return {}
    
    # Split dos dados
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # Normalização
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    # Definir modelos
    modelos = {
        'Linear Regression': LinearRegression(),
        'Random Forest': RandomForestRegressor(n_estimators=100, random_state=42),
        'KNN': KNeighborsRegressor(n_neighbors=3),
        'Decision Tree': DecisionTreeRegressor(random_state=42),
        'MLP Regressor': MLPRegressor(hidden_layer_sizes=(100,), max_iter=1000, random_state=42),
        'Lasso': Lasso(alpha=0.1, random_state=42),
        'SVR': SVR(kernel='rbf'),
        'Dummy': DummyRegressor(strategy='mean'),
        'XGBoost': XGBRegressor(random_state=42, verbosity=0)
    }
    
    # Treinar e avaliar modelos
    resultados = []
    
    for nome, modelo in modelos.items():
        print(f"Treinando {nome}...")
        
        try:
            # Treinar modelo
            if nome in ['Linear Regression', 'MLP Regressor', 'Lasso', 'SVR']:
                modelo.fit(X_train_scaled, y_train)
                y_pred = modelo.predict(X_test_scaled)
            else:
                modelo.fit(X_train, y_train)
                y_pred = modelo.predict(X_test)
            
            # Calcular métricas
            r2 = r2_score(y_test, y_pred)
            mse = mean_squared_error(y_test, y_pred)
            
            resultados.append({
                'modelo': nome,
                'r2_score': r2,
                'mse': mse,
                'features_utilizadas': len(feature_cols_expandidas),
                'features_idhm': len(feature_cols_idhm)
            })
            
            print(f"{nome}: R² = {r2:.4f}, MSE = {mse:.4f}")
            
            # Salvar importância das features para modelos tree-based
            if hasattr(modelo, 'feature_importances_'):
                importancias = pd.DataFrame({
                    'feature': feature_cols_expandidas,
                    'importancia': modelo.feature_importances_
                }).sort_values('importancia', ascending=False)
                
                print(f"\nTop 5 features mais importantes ({nome}):")
                print(importancias.head())
                
                # Salvar importâncias
                nome_arquivo = nome.lower().replace(" ", "_")
                if nome_arquivo == "random_forest":
                    caminho_arquivo = RESULT_PATHS.feature_importance_rf_csv
                elif nome_arquivo == "decision_tree":
                    caminho_arquivo = RESULT_PATHS.feature_importance_dt_csv
                elif nome_arquivo == "xgboost":
                    caminho_arquivo = RESULT_PATHS.feature_importance_xgb_csv
                else:
                    caminho_arquivo = f'results/feature_importance_{nome_arquivo}_com_idhm.csv'
                importancias.to_csv(caminho_arquivo, index=False)
        
        except Exception as e:
            print(f"Erro ao treinar {nome}: {e}")
            resultados.append({
                'modelo': nome,
                'r2_score': np.nan,
                'mse': np.nan,
                'features_utilizadas': len(feature_cols_expandidas),
                'features_idhm': len(feature_cols_idhm)
            })
    
    return resultados

def main():
    """
    Função principal do script.
    """
    print("=" * 60)
    print("CONSOLIDAÇÃO DE DADOS COM IDHM PARA PREDIÇÃO DE PREÇO DE CARBONO")
    print("=" * 60)
    
    try:
        # 1. Consolidar dados
        df_consolidado = consolidar_dados_com_idhm()
        
        # 2. Salvar dados consolidados
        output_path = RESULT_PATHS.carbono_consolidado_com_idhm_csv
        df_consolidado.to_csv(output_path, index=False)
        print(f"\nDados consolidados salvos em: {output_path}")
        
        # 3. Treinar modelos
        resultados = treinar_modelos_expandidos(df_consolidado)
        
        # 4. Salvar resultados
        if resultados:
            df_resultados = pd.DataFrame(resultados)
            df_resultados.to_csv(RESULT_PATHS.metricas_modelos_com_idhm_csv, index=False)
            print(f"\nMétricas dos modelos salvas em: {RESULT_PATHS.metricas_modelos_com_idhm_csv}")
            
            # Exibir resumo dos resultados
            print("\n" + "="*50)
            print("RESUMO DOS RESULTADOS")
            print("="*50)
            print(df_resultados.sort_values('r2_score', ascending=False))
        
        print("\n[OK] Pipeline executado com sucesso!")
        
    except Exception as e:
        print(f"[ERROR] Erro na execução: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()