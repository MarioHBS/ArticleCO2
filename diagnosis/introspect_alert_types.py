# introspect_alert_types.py

import json
import os

from map_biomas_api import MapBiomasAlertApi

# 1) Autenticação
credentials = {
    "email":    os.getenv("MAPBIOMAS_EMAIL"),
    "password": os.getenv("MAPBIOMAS_PASSWORD")
}
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
