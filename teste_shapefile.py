# Carregar TODO o shapefile (sem bbox)
import geopandas as gpd

shapefile_path = 'data/coberturausogcs_grd_MA_final_2020.shp'
gdf = gpd.read_file(shapefile_path)

# Mostrar todas as colunas
print("Colunas disponíveis:", gdf.columns.tolist())

# Mostrar as 5 primeiras linhas
print(gdf.head())

# Verificar valores únicos nas colunas de uso da terra
uso_cols = [col for col in gdf.columns if "USO" in col]
print("Colunas de uso da terra:", uso_cols)
for col in uso_cols:
    print(f"Valores únicos em {col}: {gdf[col].unique()}")
