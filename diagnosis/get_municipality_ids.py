# get_municipality_ids.py

import os
import json
from unidecode import unidecode
from map_biomas_api import MapBiomasAlertApi

def get_token():
    creds = {
        "email":    os.getenv("MAPBIOMAS_EMAIL"),
        "password": os.getenv("MAPBIOMAS_PASSWORD")
    }
    return MapBiomasAlertApi.token(creds)

def fetch_territory_options(token):
    q = """
    query {
      territoryOptions {
        categoryName
        territories {
          code
          name
        }
      }
    }
    """
    return MapBiomasAlertApi.query(token, q, {})["data"]["territoryOptions"]

def normalize(s: str) -> str:
    """Remove acentos e coloca em caixa alta."""
    return unidecode(s).strip().upper()

def extract_target_ids(options, targets):
    # 1) Filtra pela categoria "Município", normalizada
    munis_opts = [
        opt for opt in options
        if normalize(opt["categoryName"]) == "MUNICIPIO"
    ]
    # 2) Achata todas as listas de TerritoryOption
    all_munis = [t for opt in munis_opts for t in opt["territories"]]
    # 3) Mapeia NOME_NORMALIZADO → code
    mapping = { normalize(t["name"]): t["code"] for t in all_munis }
    # 4) Para cada alvo, tenta correspondência exata na versão normalizada
    result = {}
    for tgt in targets:
        key = normalize(tgt)
        result[tgt] = mapping.get(key)
    return result

if __name__ == "__main__":
    # 1) Autentica
    token = get_token()

    # 2) Busca opções de território
    opts = fetch_territory_options(token)

    # 3) Seus municípios de interesse
    alvos = ["Balsas", "Tasso Fragoso", "Alto Parnaíba"]

    # 4) Extrai os códigos
    ids = extract_target_ids(opts, alvos)

    # 5) Exibe o resultado
    print(json.dumps(ids, indent=2, ensure_ascii=False))
