# diagnosis/debug_categories.py
# -*- coding: utf-8 -*-
"""Script de diagnóstico para análise das categorias da API MapBiomas.

Este script conecta-se à API do MapBiomas Alert para explorar e
listar todas as categorias disponíveis de alertas de desmatamento,
ajudando no desenvolvimento e depuração dos scripts principais.

Dados de entrada:
- Credenciais da API MapBiomas (via variáveis de ambiente)

Arquivos de saída:
- Saída no console com informações das categorias

Dependências:
- map_biomas_api
- Variáveis de ambiente: MAPBIOMAS_EMAIL, MAPBIOMAS_PASSWORD
"""

import os

from map_biomas_api import MapBiomasAlertApi

token = MapBiomasAlertApi.token(
    {"email": os.getenv("MAPBIOMAS_EMAIL"), "password": os.getenv("MAPBIOMAS_PASSWORD")}
)

# 1) pega todas as opções
opts = MapBiomasAlertApi.query(
    token,
    """
  query {
    territoryOptions {
      categoryName
      territories { code name }
    }
  }
""",
    {},
)["data"]["territoryOptions"]

# 2) imprime categoria + qtd. de territórios
for opt in opts:
    print(f"{opt['categoryName']}: {len(opt['territories'])} itens")

# 3) mostra os primeiros nomes da categoria que tiver >0 itens
print("\nExemplos de nomes em cada categoria:")
for opt in opts:
    if opt["territories"]:
        sample = [t["name"] for t in opt["territories"][:5]]
        print(f"  {opt['categoryName']}: {sample}")
