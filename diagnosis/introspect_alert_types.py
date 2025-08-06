# diagnosis/introspect_alert_types.py
# -*- coding: utf-8 -*-
"""Script de diagnóstico para introspecção dos tipos de alertas da API MapBiomas.

Este script utiliza queries GraphQL para fazer introspecção profunda
dos tipos de dados disponíveis na API MapBiomas Alert, incluindo
AlertDataCollection, AlertData e CollectionMetadata, auxiliando
no desenvolvimento e compreensão da estrutura da API.

Dados de entrada:
- Credenciais da API MapBiomas (via variáveis de ambiente)

Arquivos de saída:
- Saída no console com estrutura detalhada dos tipos de dados

Dependências:
- map_biomas_api
- Variáveis de ambiente: MAPBIOMAS_EMAIL, MAPBIOMAS_PASSWORD
"""

import json
import os

from map_biomas_api import MapBiomasAlertApi

# 1) Autenticação
credentials = {"email": os.getenv("MAPBIOMAS_EMAIL"), "password": os.getenv("MAPBIOMAS_PASSWORD")}
token = MapBiomasAlertApi.token(credentials)

# 2) Introspecção profunda de AlertDataCollection, AlertData e CollectionMetadata
introspection = """
query {
  alertCollectionType: __type(name: "AlertDataCollection") {
    name
    fields {
      name
      type {
        kind
        name
        ofType {
          kind
          name
          ofType {
            kind
            name
            ofType {
              kind
              name
            }
          }
        }
      }
    }
  }
  alertType: __type(name: "AlertData") {
    name
    fields { name }
  }
  metaType: __type(name: "CollectionMetadata") {
    name
    fields { name }
  }
}
"""

resp = MapBiomasAlertApi.query(token, introspection, {})
print(json.dumps(resp["data"], indent=2, ensure_ascii=False))
