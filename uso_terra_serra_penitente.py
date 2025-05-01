# path: src/uso_terra_serra_penitente.py

import geopandas as gpd
import pandas as pd
import os
import matplotlib.pyplot as plt
import seaborn as sns

# Diretórios
os.makedirs('data/generated', exist_ok=True)

# Caminho do shapefile
shapefile_path = 'data/coberturausogcs_grd_MA_final_2020.shp'

# Municípios alvo
municipios_alvo = ['Balsas', 'Tasso Fragoso', 'Alto Parnaíba']

# Bounding Box aproximada da Serra do Penitente
# Coordenadas aproximadas (latitude, longitude)
# Atenção: ajustar conforme necessário!
bbox = {
    'minx': -46.3,
    'maxx': -44.7,
    'miny': -9.0,
    'maxy': -7.5
}

# Carregar shapefile filtrando a área de interesse
gdf = gpd.read_file(shapefile_path, bbox=(
    bbox['minx'], bbox['miny'], bbox['maxx'], bbox['maxy']))

# Mostrar as colunas disponíveis no GeoDataFrame
# print("Colunas disponíveis no GeoDataFrame:", gdf.columns)
print("Colunas disponíveis:", gdf.columns.tolist())

# Verificar se a coluna 'USO2020' existe antes de acessá-la
if 'USO2020' in gdf.columns:
    print("Valores únicos de USO2020:", gdf['USO2020'].unique())

    # Criar classificação simples (exemplo)

    def classificar_uso(codigo):
        if codigo in [1, 2, 3]:  # Exemplo: classes de vegetação nativa
            return 'Vegetação Nativa'
        elif codigo in [4, 5, 6]:  # Exemplo: classes agrícolas
            return 'Agricultura'
        else:
            return 'Outros'

    # Aplicar classificação
    gdf['classe_uso'] = gdf['USO2020'].apply(classificar_uso)

    # Agrupar área total por classe
    uso_agrupado = gdf.groupby('classe_uso')['Shape_Area'].sum().reset_index()
    uso_agrupado['Shape_Area_km2'] = uso_agrupado['Shape_Area'] / \
        1e6  # converter para km²

    # Salvar o dataset
    uso_agrupado.to_csv(
        'data/generated/uso_terra_serra_penitente.csv', index=False)

    # Exibir resultado
    print(uso_agrupado)

    # Gráfico para visualização
    plt.figure(figsize=(8, 6))
    sns.barplot(data=uso_agrupado, x='classe_uso', y='Shape_Area_km2')
    plt.title('Área por Classe de Uso da Terra - Serra do Penitente (2020)')
    plt.ylabel('Área (km²)')
    plt.xlabel('Classe de Uso')
    plt.tight_layout()
    plt.savefig('results/figures/uso_terra_serra_penitente.png')
    plt.close()
else:
    print("A coluna 'USO2020' não foi encontrada no GeoDataFrame. Verifique o shapefile.")
