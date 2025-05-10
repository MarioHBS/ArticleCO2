# 02_extrair_alertas_desmatamento.py
# Extrai todos os alertas de desmatamento via API MapBiomas

import os
import sys
import requests
import argparse
import pandas as pd

from variaveis import OUTPUT_PATHS


def get_token(base_url: str) -> str:
    """Obtém token da API local via /token."""
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


def fetch_all_alerts(base_url: str,
                     token: str,
                     start_date: str,
                     end_date: str,
                     territory_ids: list[int]) -> list[dict]:
    """Chama /alerts/all e retorna a lista de alertas."""
    headers = {"Authorization": f"Bearer {token}"}
    params = {
        "startDate":     start_date,
        "endDate":       end_date,
        "territoryIds":  ",".join(str(i) for i in territory_ids)
    }
    resp = requests.get(
        f"{base_url}/alerts/all",
        headers=headers,
        params=params,
        timeout=300
    )
    resp.raise_for_status()
    return resp.json().get("collection", [])


# -----------------------------------------------------------------------
# 2) Main

def main():
    parser = argparse.ArgumentParser(
        description="Extrai todos os alertas de desmatamento via API MapBiomas"
    )
    parser.add_argument(
        "--start", "-s",
        default="2019-01-01",
        help="Data inicial (YYYY-MM-DD). Padrão: %(default)s"
    )
    parser.add_argument(
        "--end", "-e",
        default="2025-03-31",
        help="Data final (YYYY-MM-DD). Padrão: %(default)s"
    )
    parser.add_argument(
        "--territories", "-t",
        default="19606,17294,17994",
        help="IDs de territórios separados por vírgula. Padrão: %(default)s"
    )
    parser.add_argument(
        "--server", "-u",
        default="http://localhost:8000",
        help="URL base do servidor API. Padrão: %(default)s"
    )
    args = parser.parse_args()

    territory_ids = [int(x) for x in args.territories.split(",")]

    # 2.1) Autenticar e buscar alerts
    token = get_token(args.server)
    alerts = fetch_all_alerts(
        args.server, token, args.start, args.end, territory_ids
    )

    if not alerts:
        print("Nenhum alerta retornado para esses parâmetros.")
        sys.exit(0)

    # 2.2) Salvar CSV
    df = pd.DataFrame(alerts)
    output_path = OUTPUT_PATHS.alertas_csv
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df.to_csv(output_path, index=False, encoding="utf-8-sig")

    print(f"✅ {len(alerts)} alertas salvos em: {output_path}")


if __name__ == "__main__":
    main()
