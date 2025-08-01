# debug_extrair_alertas.py

from map_biomas_api import MapBiomasAlertApi
import pandas as pd
import json, sys

# 1) Autenticação
credentials = {
    "email":    "marioh90@gmail.com",
    "password": "xZyn$3*6Hh"
}
token = MapBiomasAlertApi.token(credentials)

# 2) Parâmetros
startDate = "2019-01-01"
endDate   = "2025-04-30"
limit     = 1000
page      = 1
target_cities = {"BALSAS", "TASSO FRAGOSO", "ALTO PARNAIBA"}

all_alerts = []
query = MapBiomasAlertApi.PUBLISHED_ALERTS_QUERY

# 3) Loop de paginação
while True:
    variables = {
        "startDate": startDate,
        "endDate":   endDate,
        "page":      page,
        "limit":     limit,
    }
    resp = MapBiomasAlertApi.query(token, query, variables)

    # Extrai o campo 'alerts'
    alerts_field = resp.get("data", {}).get("alerts")

    # DEBUG: na 1ª página, mostra o tipo e as chaves
    if page == 1:
        print(">>> alerts_field type:", type(alerts_field))
        if isinstance(alerts_field, dict):
            print(">>> alerts_field keys:", list(alerts_field.keys()))
        elif isinstance(alerts_field, list) and alerts_field:
            print(">>> First record keys:", list(alerts_field[0].keys()))
        print()  # linha em branco

    # Descobre onde está a lista de registros
    if isinstance(alerts_field, list):
        batch = alerts_field
    elif isinstance(alerts_field, dict):
        if "records" in alerts_field:
            batch = alerts_field["records"]
        elif "data" in alerts_field:
            batch = alerts_field["data"]
        elif "items" in alerts_field:
            batch = alerts_field["items"]
        elif "nodes" in alerts_field:
            batch = alerts_field["nodes"]
        else:
            raise RuntimeError(f"Formato inesperado em alerts: {alerts_field.keys()}")
    else:
        raise RuntimeError(f"Tipo inesperado para alerts: {type(alerts_field)}")

    if not batch:
        break

    all_alerts.extend(batch)
    if len(batch) < limit:
        break

    page += 1

# 4) Converte em DataFrame e inspeciona colunas
df = pd.DataFrame(all_alerts)
print("Available columns:", df.columns.tolist())

# Detecta automaticamente a coluna de cidade
if "alertCities" in df.columns:
    filter_col = "alertCities"
elif "cities" in df.columns:
    filter_col = "cities"
elif "city" in df.columns:
    filter_col = "city"
else:
    raise RuntimeError("Não encontrei coluna de cidade; colunas disponíves: " +
                       ", ".join(df.columns))

# Função de filtragem (se for lista ou string)
def city_in_target(val):
    if isinstance(val, list):
        return any(c.strip().upper() in target_cities for c in val)
    return str(val).strip().upper() in target_cities

mask = df[filter_col].apply(city_in_target)
df_serra = df.loc[mask].reset_index(drop=True)

# 5) Salva CSV
output_path = "data/downloads/alertas_serra_penitente.csv"
df_serra.to_csv(output_path, index=False)
print(f"Linhas extraídas: {len(df_serra)}")
print(f"✅ CSV salvo em {output_path}")
