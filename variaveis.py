from dataclasses import dataclass
from types import SimpleNamespace


@dataclass
class Municipio:
    id: int
    nome: str
    uf: str


# Lista de municípios alvo
MUNICIPIOS_ALVO = [
    Municipio(2100501, "Alto Parnaíba", "MA"),
    Municipio(2101400, "Balsas",        "MA"),
    Municipio(2112001, "Tasso Fragoso",  "MA"),
]

# Região de estudo
REGIAO_ESTUDO = "Serra do Penitente"

CARBONO_CONSOLIDADO = "data/generated/carbono_serra_penitente.csv"
# Novo dataset consolidado com IDHM
CARBONO_CONSOLIDADO_COM_IDHM = "data/generated/carbono_serra_penitente_com_idhm.csv"

# Caminhos de entrada
INPUT_PATHS = SimpleNamespace(
    pib_2002_2009="data/raw/pib_municipios_ibge_2002_2009.xls",
    pib_2010_2021="data/raw/pib_municipios_ibge_2010_2021.xlsx",
    mapbiomas="data/raw/cobertura_solo_mapbiomas_municipios_brasil.xlsx",
    idhm="data/raw/idhm_municipios_serra_penitente.xlsx",
    uso_timeseries="data/generated/uso_terra_serra_penitente_timeseries.csv",
    alertas="data/generated/alertas_serra_penitente.csv",
    pib_municipal="data/generated/pib_municipal_serra_penitente_ibge.csv",
    cobertura_municipal="data/generated/mapbiomas_cobertura_municipal_long.csv",
    carbon_prices_raw="data/raw/precos_carbono_eu_ets.xlsx",
    pib="data/generated/pib_municipal_serra_penitente_ibge.csv",
    precos_carbono="data/raw/precos_carbono_eu_ets.xlsx",
)

# Caminhos de saída
OUTPUT_PATHS = SimpleNamespace(
    pib_ibge_csv="data/generated/pib_municipal_serra_penitente_ibge.csv",
    mapbiomas_long_csv="data/generated/mapbiomas_cobertura_municipal_long.csv",
    alertas_csv="data/generated/alertas_serra_penitente.csv",
    model_results_csv="results/carbon_price_model_all_results.csv",
    metricas_modelos_com_idhm_csv="results/metricas_modelos_com_idhm.csv",
    feature_importance_rf_csv="results/feature_importance_random_forest_com_idhm.csv",
    feature_importance_dt_csv="results/feature_importance_decision_tree_com_idhm.csv",
    feature_importance_xgb_csv="results/feature_importance_xgboost_com_idhm.csv",
    scatter_xgboost_png="results/figures/scatter_real_vs_pred_xgboost.png",
    evolucao_pib_png="results/figures/evolucao_pib_serra_penitente.png",
    evolucao_gee_png="results/figures/evolucao_gee_serra_penitente.png",
    evolucao_desmat_png="results/figures/evolucao_desmatamento_serra_penitente.png",
    causalidade_idhm_desmat_png="results/figures/Figura06_Causalidade_IDHM_Desmatamento.png",
)

# Features padrão para modelagem
FEATURE_COLS = ['pib', 'GEE_tCO2e', 'area_desmatada_ha']

# Features expandidas incluindo IDHM
FEATURE_COLS_EXPANDIDO = [
    'pib', 'GEE_tCO2e', 'area_desmatada_ha',
    'idhm_', 'idhm_renda', 'idhm_educação', 'idhm_longevidade'
]


def granger_causality_matrix(df, columns, maxlag=4, test='ssr_chi2test', verbose=False):
    """
    Calcula matriz de causalidade de Granger entre variáveis.
    
    Args:
        df: DataFrame com dados de séries temporais
        columns: Lista de colunas para testar causalidade
        maxlag: Número máximo de lags para teste (padrão: 4)
        test: Tipo de teste estatístico (padrão: 'ssr_chi2test')
        verbose: Se True, imprime resultados detalhados
    
    Returns:
        DataFrame com matriz de p-valores da causalidade de Granger
        (linha causa coluna)
    """
    import pandas as pd
    import numpy as np
    from statsmodels.tsa.stattools import grangercausalitytests
    
    # Criar matriz de p-valores
    causality_matrix = pd.DataFrame(np.ones((len(columns), len(columns))), 
                                   columns=columns, index=columns)
    
    for col_y in columns:
        for col_x in columns:
            if col_y != col_x:
                try:
                    # Preparar dados (remover NaN)
                    data = df[[col_y, col_x]].dropna()
                    
                    if len(data) > maxlag * 2:  # Verificar se há dados suficientes
                        # Teste de causalidade: col_x causa col_y?
                        result = grangercausalitytests(data, maxlag=maxlag, verbose=False)
                        
                        # Extrair menor p-valor entre os lags testados
                        p_values = [result[lag+1][0][test][1] for lag in range(maxlag)]
                        min_p_value = min(p_values)
                        
                        causality_matrix.loc[col_x, col_y] = min_p_value
                        
                        if verbose:
                            print(f"{col_x} -> {col_y}: p-valor = {min_p_value:.4f}")
                    else:
                        if verbose:
                            print(f"Dados insuficientes para {col_x} -> {col_y}")
                            
                except Exception as e:
                    if verbose:
                        print(f"Erro ao testar {col_x} -> {col_y}: {e}")
                    causality_matrix.loc[col_x, col_y] = 1.0  # p-valor = 1 (sem causalidade)
    
    return causality_matrix
