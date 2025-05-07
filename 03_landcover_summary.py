import os
import geopandas as gpd
import pandas as pd


def load_municipalities(fp: str) -> gpd.GeoDataFrame:
    """Carrega o shapefile de municípios e prepara o código IBGE (descarta valores ausentes)."""
    mun = gpd.read_file(fp)
    mun = mun.rename(columns={"source_id_": "codigo_ibge"})
    mun["codigo_ibge"] = pd.to_numeric(mun["codigo_ibge"], errors="coerce")
    mun = mun.dropna(subset=["codigo_ibge"]).copy()
    mun["codigo_ibge"] = mun["codigo_ibge"].astype(int)
    return mun


def filter_serra_penitente(mun: gpd.GeoDataFrame, codes: list[int]) -> gpd.GeoDataFrame:
    """Filtra apenas os municípios da Serra do Penitente."""
    return mun[mun["codigo_ibge"].isin(codes)].reset_index(drop=True)


def load_landcover(fp: str, target_crs: int = None) -> gpd.GeoDataFrame:
    """Carrega o shapefile de uso do solo e, opcionalmente, reprojeta."""
    lc = gpd.read_file(fp)
    print(f"CRS original do landcover: {lc.crs}")
    if target_crs:
        lc = lc.to_crs(epsg=target_crs)
        print(f"Reprojected landcover to EPSG:{target_crs}")
    return lc


def intersect_landcover_municipalities(
    lc: gpd.GeoDataFrame,
    mun: gpd.GeoDataFrame
) -> gpd.GeoDataFrame:
    """Faz a interseção espacial entre landcover e municípios alvo, garantindo CRS compatível."""
    # Garante que ambos os GeoDataFrames estejam no mesmo CRS
    if mun.crs != lc.crs:
        mun = mun.to_crs(lc.crs)
    return gpd.overlay(lc, mun, how="intersection")


def summarize_landcover(lc_roi: gpd.GeoDataFrame) -> pd.DataFrame:
    """Agrupa pelos usos de solo (USO2020) e soma áreas em m²."""
    lc_roi = lc_roi.copy()
    lc_roi["area_m2"] = lc_roi.geometry.area
    summary = (
        lc_roi
        .groupby(["codigo_ibge", "USO2020"], as_index=False)
        .agg({"area_m2": "sum"})
    )
    return summary


def merge_municipality_names(
    summary: pd.DataFrame,
    mun: gpd.GeoDataFrame
) -> pd.DataFrame:
    """Adiciona o nome do município ao resumo."""
    merged = summary.merge(
        mun[["codigo_ibge", "name"]],
        on="codigo_ibge",
        how="left"
    ).rename(columns={"name": "municipio", "USO2020": "uso2020"})
    return merged[["municipio", "codigo_ibge", "uso2020", "area_m2"]]


def save_summary(df: pd.DataFrame, out_fp: str):
    """Salva o DataFrame final em CSV."""
    os.makedirs(os.path.dirname(out_fp), exist_ok=True)
    df.to_csv(out_fp, index=False, encoding="utf-8-sig")
    print(f"✅ CSV salvo em: {out_fp}")


def main():
    # Paths corrigidos
    mun_fp = "data/raw/municipalities/municipalities.shp"
    lc_fp = "data/raw/landcover/landcover_ma_2020.shp"
    out_fp = "data/generated/landcover_summary_serra_penitente.csv"
    target_crs = 5880  # Exemplo de CRS equal-area
    serra_codes = [2100501, 2101400, 2112001]

    # 1) Municípios
    mun = load_municipalities(mun_fp)
    roi = filter_serra_penitente(mun, serra_codes)
    print("Municípios selecionados:\n", roi[["codigo_ibge", "name"]])

    # 2) Landcover
    lc = load_landcover(lc_fp, target_crs=target_crs)

    # 3) Interseção espacial
    # Ao intersectar, o CRS de muni e lc serão alinhados dentro da função
    lc_roi = intersect_landcover_municipalities(lc, roi)
    print(f"Feições após interseção: {len(lc_roi)}")

    # 4) Resumo das áreas
    summary = summarize_landcover(lc_roi)
    resumo = merge_municipality_names(summary, roi)
    print("Visão geral do resumo:\n", resumo.head())

    # 5) Salvamento
    save_summary(resumo, out_fp)


if __name__ == "__main__":
    main()
