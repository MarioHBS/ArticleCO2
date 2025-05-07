import os
import ee
import geopandas as gpd
import pandas as pd

# Autentica e inicializa o Earth Engine
ee.Authenticate()
ee.Initialize(project="trabalho-credito-carbono")

# Define os municípios alvo
municipios_alvo = ["Balsas", "Tasso Fragoso", "Alto Parnaíba"]

# 1) Lê o shapefile dos municípios
gdf = gpd.read_file("data/raw/municipalities/municipalities.shp")


def salva_municipios(gdf):
    # 2) Salva todos os nomes únicos dos municípios em um .txt
    os.makedirs("data/generated", exist_ok=True)
    mun_names = sorted(gdf["name"].unique())
    with open("data/generated/municipios.txt", "w", encoding="utf-8") as f:
        for m in mun_names:
            f.write(f"{m}\n")
    print(f"✅ {len(mun_names)} municípios salvos em data/generated/municipios.txt")
# salva_municipios(gdf)


# 3) Filtra apenas Balsas, Tasso Fragoso e Alto Parnaíba

for m in municipios_alvo:
    if m not in gdf["name"].values:
        print(f"⚠️ Município não encontrado: {m}")
gdf = gdf[gdf["name"].isin(municipios_alvo)]
print("Municípios filtrados:", gdf["name"].tolist())

# 4) Garante projeção WGS84
gdf = gdf.to_crs(epsg=4326)

# 5) Converte para FeatureCollection do Earth Engine


def geodataframe_to_ee(fc):
    features = []
    for _, row in fc.iterrows():
        geom_json = row.geometry.__geo_interface__
        props = row.drop("geometry").to_dict()
        features.append(ee.Feature(ee.Geometry(geom_json), props))
    return ee.FeatureCollection(features)


ee_munis = geodataframe_to_ee(gdf)

# 6) Carrega coleção e calcula média por município
collection = (
    ee.ImageCollection("projects/mapbiomas-workspace/CO2_anomaly")
      .filterDate("2019-01-01", "2025-04-30")
)


def calc_mean(img):
    return img.reduceRegions(
        collection=ee_munis,
        reducer=ee.Reducer.mean(),
        scale=30
    ).map(lambda f: f.set("date", img.date().format("YYYY-MM-dd")))


result_fc = collection.map(calc_mean).flatten()

# 7) Exporta o resultado para CSV local
features = result_fc.getInfo()["features"]
rows = [f["properties"] for f in features]
df = pd.DataFrame(rows)

df.to_csv("data/generated/gee_serra_penitente.csv", index=False)
print("✅ gee_serra_penitente.csv gerado em data/generated/")
