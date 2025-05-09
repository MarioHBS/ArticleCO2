import os
import pandas as pd


def load_coverage_excel(fp: str, sheet_name: str = "COVERAGE_9") -> pd.DataFrame:
    """Carrega o Excel com cobertura CLASSIFICADA para múltiplos anos (COVERAGE_9)."""
    df = pd.read_excel(fp, sheet_name=sheet_name)
    # Renomeia colunas para padronizar
    df = df.rename(columns={
        'geocode': 'codigo_ibge',
        'municipality': 'municipio',
        'class': 'uso'
    })
    return df


def transform_long(df: pd.DataFrame) -> pd.DataFrame:
    """Transforma DataFrame em formato longo: one row per muni-uso-year com área em m²."""
    # Identifica colunas de ano (numéricas)
    year_cols = [c for c in df.columns if isinstance(c, (int, float))]
    id_vars = ['codigo_ibge', 'municipio', 'uso']
    df_long = df.melt(
        id_vars=id_vars,
        value_vars=year_cols,
        var_name='year',
        value_name='area_ha'
    )
    # Conversões de tipo
    df_long['year'] = df_long['year'].astype(int)
    df_long['area_m2'] = df_long['area_ha'].astype(float) * 10000
    return df_long


def filter_municipalities(df: pd.DataFrame, codes: list[int]) -> pd.DataFrame:
    """Filtra o DataFrame apenas para os códigos IBGE de Serra do Penitente."""
    return df[df['codigo_ibge'].isin(codes)].reset_index(drop=True)


def save_summary(df: pd.DataFrame, out_fp: str):
    """Salva o DataFrame final em CSV, criando diretório se necessário."""
    os.makedirs(os.path.dirname(out_fp), exist_ok=True)
    df.to_csv(out_fp, index=False, encoding='utf-8-sig')
    print(f"✅ CSV salvo em: {out_fp}")


def main():
    # Arquivo de entrada: Excel MapBiomas cobertura multianual
    excel_fp = 'data/raw/mapbiomas_brazil_col_coverage_biome_state_municipality.xlsx'
    # Arquivo de saída: CSV filtrado para Serra do Penitente
    out_fp = 'data/partial/landcover_summary_serra_penitente.csv'
    serra_codes = [2100501, 2101400, 2112001]

    # 1) Carrega dados brutos
    df = load_coverage_excel(excel_fp)

    # 2) Transforma para formato longo e converte para m²
    df_long = transform_long(df)

    # 3) Filtra apenas os municípios de interesse
    df_serra = filter_municipalities(df_long, serra_codes)
    print('Resumo Serra do Penitente (amostra):')
    print(df_serra.head())

    # 4) Salva CSV final
    save_summary(df_serra, out_fp)


if __name__ == '__main__':
    main()
