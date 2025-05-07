# path: src/02_landcover_inspection.py

import geopandas as gpd

# 1) Defina o caminho para o shapefile (todos os arquivos .shp/.shx/.dbf/.prj no mesmo dir)
landcover_fp = "data/raw/landcover/landcover_ma_2020.shp"

# 2) Carrega o shapefile
landcover = gpd.read_file(landcover_fp)

# 3) Inspeção rápida
print("CRS:", landcover.crs)
print("\nColunas disponíveis:", landcover.columns.tolist())
print("\nPrimeiros registros:\n", landcover.head())

# 4) Contagem por classe de uso em 2020
print("\nContagem de códigos USO2020:")
print(landcover["USO2020"].value_counts())

# 5) (Opcional) se você tiver um dicionário que mapeie código → nome, pode combiná-lo assim:
# legend = {10: "Floresta", 20: "Savanna", …}
# print(landcover["USO2020"].map(legend).value_counts())
