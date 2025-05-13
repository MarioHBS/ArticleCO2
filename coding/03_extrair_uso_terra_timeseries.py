# path: src/04_uso_terra.py

import os
import pandas as pd

RAW_EXCEL = "data/raw/mapbiomas_brazil_col_coverage_biome_state_municipality.xlsx"
PARTIAL_OUT = "data/partial/uso_terra_serra_penitente_timeseries.csv"
SHEET_NAME = "COVERAGE_9"
# Alto Parnaíba, Balsas, Tasso Fragoso
SERRA_CODES = [2100501, 2101400, 2112001]


def load_coverage_excel(fp: str, sheet_name: str = SHEET_NAME) -> pd.DataFrame:
    """
    Carrega o Excel MapBiomas de cobertura multianual.
    Renomeia colunas para padronizar:
      - geocode   → codigo_ibge
      - municipality → municipio
      - class     → uso
    """
    df = pd.read_excel(fp, sheet_name=sheet_name)
    df = df.rename(columns={
        'geocode': 'codigo_ibge',
        'municipality': 'municipio',
        'class': 'uso'
    })
    return df


def transform_long(df: pd.DataFrame) -> pd.DataFrame:
    """
    Transforma de “largura” para “longo”:
    Cada linha = um município + uso + ano + área (ha e km2)
    """
    # detecta colunas-numéricas (anos)
    year_cols = [c for c in df.columns if isinstance(c, (int, float))]
    id_vars = ['codigo_ibge', 'municipio', 'uso']
    df_long = df.melt(
        id_vars=id_vars,
        value_vars=year_cols,
        var_name='year',
        value_name='area_ha'
    )
    df_long['year'] = df_long['year'].astype(int)
    df_long['area_ha'] = df_long['area_ha'].astype(float)
    # 1 hectare = 0.01 km²
    df_long['area_km2'] = df_long['area_ha'] * 0.01
    return df_long


def filter_municipalities(df: pd.DataFrame, codes: list[int]) -> pd.DataFrame:
    """Filtra apenas os municípios de Serra do Penitente."""
    return df[df['codigo_ibge'].isin(codes)].reset_index(drop=True)


def summarize_by_use_year(df: pd.DataFrame) -> pd.DataFrame:
    """
    Agrega por município, uso e ano, somando áreas.
    Retorna DataFrame com colunas:
      codigo_ibge, municipio, year, uso, area_ha, area_km2
    """
    summary = (
        df
        .groupby(
            ['codigo_ibge', 'municipio', 'year', 'uso'],
            as_index=False
        )[['area_ha', 'area_km2']]
        .sum()
    )
    return summary


def save_partial(df: pd.DataFrame, out_fp: str):
    """Salva o CSV parcial em data/partial."""
    os.makedirs(os.path.dirname(out_fp), exist_ok=True)
    df.to_csv(out_fp, index=False, encoding='utf-8-sig')
    print(f"✅ CSV parcial gerado em: {out_fp}")


def main():
    # 1) Carrega o Excel bruto
    df_raw = load_coverage_excel(RAW_EXCEL)

    # 2) Transforma em formato longo
    df_long = transform_long(df_raw)
    print("Amostra (longo):")
    print(df_long.head())

    # 3) Filtra apenas Serra do Penitente
    df_serra = filter_municipalities(df_long, SERRA_CODES)
    print("\nAmostra pós-filtro:")
    print(df_serra.head())

    # 4) Agrega por município, uso e ano
    df_summary = summarize_by_use_year(df_serra)
    print("\nAmostra agregada (município × uso × ano):")
    print(df_summary.head())

    # 5) Salva parcial
    save_partial(df_summary, PARTIAL_OUT)


if __name__ == "__main__":
    main()
