from dataclasses import dataclass
from types import SimpleNamespace


@dataclass
class Municipio:
    id: int
    nome: str
    uf: str


# Lista de municípios alvo
MUNICIPIOS = [
    Municipio(2100501, "Alto Parnaíba", "MA"),
    Municipio(2101400, "Balsas",        "MA"),
    Municipio(2112001, "Tasso Fragoso",  "MA"),
]

# Região de estudo
REGIAO = "Serra do Penitente"

CARBONO_CONSOLIDADO = "data/generated/carbono_serra_penitente.csv"

# Caminhos de entrada
INPUT_PATHS = SimpleNamespace(
    pib_2002_2009="data/raw/PIB dos Municípios - base de dados 2002-2009.xls",
    pib_2010_2021="data/raw/PIB dos Municípios - base de dados 2010-2021.xlsx",
    mapbiomas="data/raw/mapbiomas_brazil_col_coverage_biome_state_municipality.xlsx",
    uso_timeseries="data/partial/uso_terra_serra_penitente_timeseries.csv",
    alertas="data/partial/alertas_serra_penitente.csv",
    pib_municipal="data/partial/pib_municipal_serra_penitente_ibge.csv",
    cobertura_municipal="data/partial/mapbiomas_cobertura_municipal_long.csv",
    carbon_prices_raw="data/raw/carbon-prices-latest.xlsx",
)

# Caminhos de saída
OUTPUT_PATHS = SimpleNamespace(
    pib_ibge_csv="data/partial/pib_municipal_serra_penitente_ibge.csv",
    mapbiomas_long_csv="data/partial/mapbiomas_cobertura_municipal_long.csv",
    alertas_csv="data/partial/alertas_serra_penitente.csv",
    model_results_csv="results/carbon_price_model_all_results.csv",
    scatter_xgboost_png="results/figures/scatter_real_vs_pred_xgboost.png",
    evolucao_pib_png="results/figures/evolucao_pib_serra_penitente.png",
    evolucao_gee_png="results/figures/evolucao_gee_serra_penitente.png",
    evolucao_desmat_png="results/figures/evolucao_desmatamento_serra_penitente.png",
)

# Features padrão para modelagem
FEATURE_COLS = ['pib', 'GEE_tCO2e', 'area_desmatada_ha']
