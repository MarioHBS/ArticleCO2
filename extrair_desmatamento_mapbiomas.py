# path: src/extrair_desmatamento_mapbiomas_v2.py

import requests
import os

# --- Configurações
EMAIL = "marioh90@gmail.com"
PASSWORD = "xZyn$3*6Hh"

# Endpoints
api_login_url = "https://plataforma.alerta.mapbiomas.org/api/v2/graphql"
api_query_url = "https://plataforma.alerta.mapbiomas.org/api/v2/graphql"

# --- Login para obter Token


def obter_token(email, password):
    query = {
        "query": """
        mutation signIn($email: String!, $password: String!) {
          signIn(email: $email, password: $password) {
            token
          }
        }
        """,
        "variables": {
            "email": email,
            "password": password
        }
    }
    headers = {"Content-Type": "application/json"}
    response = requests.post(api_login_url, json=query, headers=headers)

    if response.status_code == 200:
        data = response.json()
        return data['data']['signIn']['token']
    else:
        print(f"Erro no login: {response.status_code}")
        return None

# --- Buscar alertas reais paginados


def buscar_alertas(token, limite=1000):
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    alerta_lista = []
    offset = 0
    continuar = True

    while continuar:
        query = {
            "query": """
            query alerts($limit: Int!, $offset: Int!) {
              alerts(limit: $limit, offset: $offset) {
                id
                status
                detected_year
                area_ha
                biome
                state
                city
                source
              }
            }
            """,
            "variables": {
                "limit": limite,
                "offset": offset
            }
        }

        response = requests.post(api_query_url, json=query, headers=headers)

        if response.status_code == 200:
            data = response.json()
            if 'data' not in data or 'alerts' not in data['data']:
                print("❗ Erro na resposta da API!")
                print("Resposta recebida:", data)
                return []
            alertas = data['data']['alerts']

            if not alertas:
                continuar = False
            else:
                alerta_lista.extend(alertas)
                offset += limite
                print(f"Coletados {len(alerta_lista)} registros...")
        else:
            print(f"Erro ao buscar alertas: {response.status_code}")
            break

    return alerta_lista

# --- Execução principal


def main():
    os.makedirs("data/downloads", exist_ok=True)

    token = obter_token(EMAIL, PASSWORD)
    if not token:
        return

    alertas = buscar_alertas(token)
    if not alertas:
        print("Nenhum alerta coletado.")
        return

    df = pd.DataFrame(alertas)

    output_path = "data/downloads/alertas_mapbiomas_corrigido.csv"
    df.to_csv(output_path, index=False)

    print(f"\u2705 CSV de alertas reais salvo em: {output_path}")
    print(f"Total de registros salvos: {len(df)}")


if __name__ == "__main__":
    main()
