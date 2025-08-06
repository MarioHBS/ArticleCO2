from dataclasses import dataclass
from types import SimpleNamespace
import numpy as np
import pandas as pd


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

# Caminhos de entrada (apenas arquivos brutos)
INPUT_PATHS = SimpleNamespace(
    pib_2002_2009="data/raw/pib_municipios_ibge_2002_2009.xls",
    pib_2010_2021="data/raw/pib_municipios_ibge_2010_2021.xlsx",
    mapbiomas="data/raw/cobertura_solo_mapbiomas_municipios_brasil.xlsx",
    idhm="data/raw/idhm_municipios_serra_penitente.xlsx",
    precos_carbono="data/raw/precos_carbono_eu_ets.xlsx",
)

# Caminhos de scripts
SCRIPTS = SimpleNamespace(
    extrair_pib_municipal="src/01_extrair_pib_municipal.py",
    extrair_cobertura_municipal="src/02_extrair_cobertura_municipal.py",
    extrair_alertas_desmatamento="src/03_extrair_alertas_desmatamento.py",
    extrair_uso_terra_timeseries="src/04_extrair_uso_terra_timeseries.py",
    consolidar_dados_carbono="src/05_consolidar_dados_carbono.py",
    consolidar_dados_carbono_com_idhm="src/06_consolidar_dados_carbono_com_idhm.py",
    gerar_figuras_carbono="src/07_gerar_figuras_carbono.py",
    gerar_figuras_consolidadas="src/08_gerar_figuras_consolidadas.py",
    gerar_visualizacoes_idhm_desmatamento="src/09_gerar_visualizacoes_idhm_desmatamento.py",
    analisar_politicas_por_estratos_idhm="src/10_analisar_politicas_por_estratos_idhm.py",
    comparar_modelos_com_sem_idhm="src/comparar_modelos_com_sem_idhm.py",
)

# Caminhos de saída
GENERATED_PATHS = SimpleNamespace(
    pib_ibge_csv="data/generated/pib_municipal_serra_penitente_ibge.csv",
    mapbiomas_long_csv="data/generated/mapbiomas_cobertura_municipal_long.csv",
    alertas_csv="data/generated/alertas_serra_penitente.csv",
    uso_timeseries_csv="data/generated/uso_terra_serra_penitente_timeseries.csv",
    carbono_consolidado_csv="data/generated/carbono_serra_penitente.csv",
    carbono_consolidado_com_idhm_csv="data/generated/carbono_serra_penitente_com_idhm.csv",
)

# Caminhos de resultados CSV
RESULT_PATHS = SimpleNamespace(
    # Resultados de modelos
    model_results_csv="results/resultados_modelos_precificacao_carbono.csv",
    carbon_price_model_all_results_csv="results/carbon_price_model_all_results.csv",
    metricas_modelos_com_idhm_csv="results/metricas_modelos_com_idhm.csv",
    comparacao_modelos_idhm_csv="results/comparacao_modelos_idhm.csv",

    # Importância de features
    feature_importance_rf_csv="results/importancia_variaveis_random_forest_com_idhm.csv",
    feature_importance_dt_csv="results/importancia_variaveis_decision_tree_com_idhm.csv",
    feature_importance_xgb_csv="results/importancia_variaveis_xgboost_com_idhm.csv",

    # Relatórios
    relatorio_impacto_idhm_txt="results/relatorio_impacto_idhm.txt",
    relatorio_analise_estratos_desenvolvimento_txt="results/relatorio_analise_estratos_desenvolvimento.txt",
)

# Caminhos de figuras
FIGURE_PATHS = SimpleNamespace(
    # Figuras principais numeradas
    figura01_evolucao_pib_png="results/figures/Figura01_Evolucao_PIB.png",
    figura03_evolucao_gee_png="results/figures/Figura03_Evolucao_GEE.png",
    figura04_evolucao_desmatamento_png="results/figures/Figura04_Evolucao_Desmatamento.png",
    figura05_eqm_modelos_png="results/figures/Figura05_EQM_Modelos.png",
    figura06_causalidade_granger_png="results/figures/Figura06_Causalidade_Granger.png",
    figura06_causalidade_idhm_desmat_png="results/figures/Figura06_Causalidade_IDHM_Desmatamento.png",
    figura10_correlacao_idhm_desmatamento_png="results/figures/Figura10_Correlacao_IDHM_Desmatamento.png",
    figura11_evolucao_temporal_idhm_desmatamento_png="results/figures/Figura11_Evolucao_Temporal_IDHM_Desmatamento.png",
    figura12_heatmap_correlacao_idhm_png="results/figures/Figura12_Heatmap_Correlacao_IDHM.png",
    figura13_analise_estratos_desenvolvimento_png="results/figures/Figura13_Analise_Estratos_Desenvolvimento.png",
    figura14_heatmap_metricas_estratos_png="results/figures/Figura14_Heatmap_Metricas_Estratos.png",

    # Figuras de dispersão (scatter plots)
    scatter_xgboost_png="results/figures/dispersao_real_vs_pred_xgboost.png",
    scatter_r2_vs_mse_comparacao_png="results/figures/scatter_r2_vs_mse_comparacao.png",

    # Figuras de evolução temporal
    evolucao_pib_png="results/figures/evolucao_pib_serra_penitente.png",
    evolucao_gee_png="results/figures/evolucao_gee_serra_penitente.png",
    evolucao_desmat_png="results/figures/evolucao_desmatamento_serra_penitente.png",

    # Figuras de comparação de modelos
    comparacao_modelos_com_sem_idhm_png="results/figures/comparacao_modelos_com_sem_idhm.png",
    melhorias_percentuais_idhm_png="results/figures/melhorias_percentuais_idhm.png",

    # Figuras consolidadas em PDF
    figura01_paineis_gee_pib_pdf="results/figures/Figura01_Paineis_GEE_PIB.pdf",
    figura02_comparacao_mse_pdf="results/figures/Figura02_Comparacao_MSE.pdf",
    figura03_importancia_rf_pdf="results/figures/Figura03_Importancia_RF.pdf",
    figura04_matriz_causalidade_granger_pdf="results/figures/Figura04_Matriz_Causalidade_Granger.pdf",

    # Figuras de importância de variáveis
    figura08_importancia_variaveis_png="results/figures/Figura08_Importancia_Variaveis.png",
    figura09_evolucao_preco_carbono_png="results/figures/Figura09_Evolucao_Preco_Carbono.png",
)

# Aliases para compatibilidade com código existente
CARBONO_CONSOLIDADO = GENERATED_PATHS.carbono_consolidado_csv
CARBONO_CONSOLIDADO_COM_IDHM = GENERATED_PATHS.carbono_consolidado_com_idhm_csv
MUNICIPIOS = MUNICIPIOS_ALVO

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

    # Verificar quais colunas têm variação (não são constantes)
    valid_columns = []
    for col in columns:
        if col in df.columns:
            col_data = df[col].dropna()
            if len(col_data) > 0 and col_data.nunique() > 1:  # Tem mais de um valor único
                valid_columns.append(col)
            elif verbose:
                print(f"[SKIP] Coluna '{col}' tem valores constantes ou insuficientes")
        elif verbose:
            print(f"[SKIP] Coluna '{col}' não encontrada no DataFrame")

    if len(valid_columns) < 2:
        if verbose:
            print(f"[WARN] Apenas {len(valid_columns)} colunas válidas encontradas. Retornando matriz vazia.")
        return pd.DataFrame(np.ones((len(columns), len(columns))),
                           columns=columns, index=columns)

    # Criar matriz de p-valores
    causality_matrix = pd.DataFrame(np.ones((len(columns), len(columns))),
                                   columns=columns, index=columns)

    for col_y in valid_columns:
        for col_x in valid_columns:
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
