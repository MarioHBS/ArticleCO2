# 03_alertas_desmatamento.py

import requests
import argparse
import sys
import os
from map_biomas_api import MapBiomasAlertApi
import pandas as pd

# 1) Autenticação
credentials = {
    "email":    "marioh90@gmail.com",
    "password": "xZyn$3*6Hh"
}


def get_token(base_url: str) -> str:
    """Obtem token da API local via /token."""
    email = os.getenv("MAPBIOMAS_EMAIL")
    pwd = os.getenv("MAPBIOMAS_PASSWORD")
    if not email or not pwd:
        print("Erro: defina MAPBIOMAS_EMAIL e MAPBIOMAS_PASSWORD", file=sys.stderr)
        sys.exit(1)
    resp = requests.post(
        f"{base_url}/token",
        json={"email": email, "password": pwd},
        timeout=30
    )
    resp.raise_for_status()
    return resp.json()["token"]


def fetch_all_alerts(base_url: str, token: str, start_date: str, end_date: str, territory_ids: list[int]) -> list[dict]:
    """Chama /alerts/all e retorna a lista de alertas."""
    headers = {"Authorization": f"Bearer {token}"}
    params = {
        "startDate": start_date,
        "endDate": end_date,
        "territoryIds": ",".join(str(i) for i in territory_ids)
    }
    resp = requests.get(f"{base_url}/alerts/all",
                        headers=headers, params=params, timeout=300)
    resp.raise_for_status()
    data = resp.json()
    return data.get("collection", [])


def main():
    parser = argparse.ArgumentParser(
        description="Extrai todos os alertas de desmatamento via API MapBiomas")
    parser.add_argument("--start", "-s", required=True,
                        help="Data inicial (YYYY-MM-DD)")
    parser.add_argument("--end",   "-e", required=True,
                        help="Data final (YYYY-MM-DD)")
    parser.add_argument("--territories", "-t", required=True,
                        help="IDs de territórios separados por vírgula (ex: 19606,17294,17994)")
    parser.add_argument("--output", "-o", default="data/partial/alertas_serra_penitente.csv",
                        help="Caminho do arquivo CSV de saída")
    parser.add_argument("--server", "-u", default="http://localhost:8000",
                        help="URL base do servidor API (padrão: http://localhost:8000)")
    args = parser.parse_args()

    territory_ids = [int(x) for x in args.territories.split(",")]

    token = get_token(args.server)
    alerts = fetch_all_alerts(
        args.server, token, args.start, args.end, territory_ids)

    if not alerts:
        print("Nenhum alerta retornado para esses parâmetros.")
        sys.exit(0)

    # Converte para DataFrame e salva CSV
    df = pd.DataFrame(alerts)
    df.to_csv(args.output, index=False, encoding="utf-8-sig")

    print(f"✅ {len(alerts)} alertas salvos em: {args.output}")


if __name__ == "__main__":
    main()
