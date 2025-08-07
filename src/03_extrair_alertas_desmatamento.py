# src/03_extrair_alertas_desmatamento.py
# -*- coding: utf-8 -*-
<<<<<<< HEAD
"""Script para extração de alertas de desmatamento via API MapBiomas.
=======
"""
Script para extração de alertas de desmatamento via API MapBiomas.
>>>>>>> beb1535e6636cbb46b2a9dc8a71465b20f493e7b

Este script utiliza a API do MapBiomas para extrair dados de alertas de
desmatamento nos municípios da região da Serra do Penitente, processando
informações sobre área desmatada, datas e categorias de alertas.
"""
<<<<<<< HEAD

import argparse
import logging
import os
import sys

import pandas as pd
import requests
from requests.exceptions import ConnectionError, RequestException, Timeout

from variaveis import GENERATED_PATHS

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
=======
import os
import sys
import requests
import argparse
import logging
import pandas as pd
from requests.exceptions import RequestException, Timeout, ConnectionError

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from variaveis import GENERATED_PATHS
>>>>>>> beb1535e6636cbb46b2a9dc8a71465b20f493e7b


def get_token(base_url: str) -> str:
    """Obtém token da API local via /token."""
    try:
        email = os.getenv("MAPBIOMAS_EMAIL")
        pwd = os.getenv("MAPBIOMAS_PASSWORD")
<<<<<<< HEAD

        if not email or not pwd:
            raise ValueError(
                "Credenciais não configuradas: defina MAPBIOMAS_EMAIL e MAPBIOMAS_PASSWORD"
            )

        logging.info(f"Autenticando na API: {base_url}")

=======
        
        if not email or not pwd:
            raise ValueError("Credenciais não configuradas: defina MAPBIOMAS_EMAIL e MAPBIOMAS_PASSWORD")
        
        logging.info(f"Autenticando na API: {base_url}")
        
>>>>>>> beb1535e6636cbb46b2a9dc8a71465b20f493e7b
        resp = requests.post(
            f"{base_url}/token",
            json={"email": email, "password": pwd},
            timeout=30
        )
        resp.raise_for_status()
<<<<<<< HEAD

        token_data = resp.json()
        if "token" not in token_data:
            raise ValueError("Resposta da API não contém token válido")

        logging.info("Autenticação realizada com sucesso")
        return token_data["token"]

=======
        
        token_data = resp.json()
        if "token" not in token_data:
            raise ValueError("Resposta da API não contém token válido")
            
        logging.info("Autenticação realizada com sucesso")
        return token_data["token"]
        
>>>>>>> beb1535e6636cbb46b2a9dc8a71465b20f493e7b
    except Timeout:
        logging.error(f"Timeout ao conectar com a API: {base_url}")
        raise
    except ConnectionError:
        logging.error(f"Erro de conexão com a API: {base_url}")
        raise
    except RequestException as e:
        logging.error(f"Erro na requisição de autenticação: {str(e)}")
        raise
    except Exception as e:
        logging.error(f"Erro inesperado durante autenticação: {str(e)}")
        raise


def fetch_all_alerts(base_url: str,
                     token: str,
                     start_date: str,
                     end_date: str,
                     territory_ids: list[int]) -> list[dict]:
    """Chama /alerts/all e retorna a lista de alertas."""
    try:
        logging.info(f"Buscando alertas para período {start_date} a {end_date}")
        logging.info(f"Territórios: {territory_ids}")
<<<<<<< HEAD

=======
        
>>>>>>> beb1535e6636cbb46b2a9dc8a71465b20f493e7b
        headers = {"Authorization": f"Bearer {token}"}
        params = {
            "startDate":     start_date,
            "endDate":       end_date,
            "territoryIds":  ",".join(str(i) for i in territory_ids)
        }
<<<<<<< HEAD

=======
        
>>>>>>> beb1535e6636cbb46b2a9dc8a71465b20f493e7b
        resp = requests.get(
            f"{base_url}/alerts/all",
            headers=headers,
            params=params,
            timeout=300
        )
        resp.raise_for_status()
<<<<<<< HEAD

        data = resp.json()
        alerts = data.get("collection", [])

        logging.info(f"Recebidos {len(alerts)} alertas da API")

        if not alerts:
            logging.warning("Nenhum alerta encontrado para os parâmetros especificados")

        return alerts

=======
        
        data = resp.json()
        alerts = data.get("collection", [])
        
        logging.info(f"Recebidos {len(alerts)} alertas da API")
        
        if not alerts:
            logging.warning("Nenhum alerta encontrado para os parâmetros especificados")
        
        return alerts
        
>>>>>>> beb1535e6636cbb46b2a9dc8a71465b20f493e7b
    except Timeout:
        logging.error("Timeout ao buscar alertas da API")
        raise
    except ConnectionError:
        logging.error("Erro de conexão ao buscar alertas")
        raise
    except RequestException as e:
        logging.error(f"Erro na requisição de alertas: {str(e)}")
        raise
    except Exception as e:
        logging.error(f"Erro inesperado ao buscar alertas: {str(e)}")
        raise


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
<<<<<<< HEAD

=======
    
>>>>>>> beb1535e6636cbb46b2a9dc8a71465b20f493e7b
    # Configurar logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s"
    )
<<<<<<< HEAD

=======
    
>>>>>>> beb1535e6636cbb46b2a9dc8a71465b20f493e7b
    try:
        territory_ids = [int(x) for x in args.territories.split(",")]
        logging.info(f"Iniciando extração de alertas para territórios: {territory_ids}")

        # Autenticar e buscar alerts
        token = get_token(args.server)
        alerts = fetch_all_alerts(
            args.server, token, args.start, args.end, territory_ids
        )

        if not alerts:
            logging.warning("Nenhum alerta retornado para esses parâmetros")
            # Criar arquivo vazio para manter consistência do pipeline
            df = pd.DataFrame()
        else:
            df = pd.DataFrame(alerts)
            logging.info(f"Processando {len(alerts)} alertas")

        # Salvar CSV
        output_path = GENERATED_PATHS.alertas_csv
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        df.to_csv(output_path, index=False, encoding="utf-8-sig")

        logging.info(f"Alertas salvos com sucesso em: {output_path} ({len(df)} registros)")
<<<<<<< HEAD

=======
        
>>>>>>> beb1535e6636cbb46b2a9dc8a71465b20f493e7b
    except ValueError as e:
        logging.error(f"Erro de validação: {str(e)}")
        sys.exit(1)
    except Exception as e:
        logging.error(f"Erro durante extração de alertas: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
