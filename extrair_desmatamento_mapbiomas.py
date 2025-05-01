# path: src/extrair_desmatamento_mapbiomas.py

import requests
import pandas as pd
import os

# --- Configurações
EMAIL = "marioh90@gmail.com"
PASSWORD = "xZyn$3*6Hh"

# Endpoints
api_login_url = "https://plataforma.alerta.mapbiomas.org/api/v2/graphql"
api_query_url = "https://plataforma.alerta.mapbiomas.org/api/v2/graphql"

# --- Etapa 1: Fazer login para obter o Token


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

# --- Etapa 2: Buscar URL do CSV


def buscar_url_csv(token):
    query = {
        "query": """
        query relatoryAlert($format: RelatoryTypenameTypes!, $typename: RelatoryFormatTypes!) {
          relatoryAlert(format: $format, typename: $typename) {
            fileUrl
          }
        }
        """,
        "variables": {
            "format": "Csv",
            "typename": "Alerts"
        }
    }
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    response = requests.post(api_query_url, json=query, headers=headers)

    if response.status_code == 200:
        data = response.json()
        file_url = data['data']['relatoryAlert']['fileUrl']
        return file_url
    else:
        print(f"Erro ao buscar URL: {response.status_code}")
        return None

# --- Etapa 3: Baixar e corrigir CSV


def baixar_csv(file_url, destino):
    response = requests.get(file_url)
    if response.status_code == 200:
        with open(destino, "wb") as f:
            f.write(response.content)
        print(f"✅ CSV salvo em {destino}")

        try:
            df = pd.read_csv(destino, sep=",", engine="python")
        except pd.errors.ParserError:
            df = pd.read_csv(destino, sep=";", engine="python")

        df.to_csv(destino, index=False)
        print("✅ CSV reformatado com sucesso!")
    else:
        print(f"Erro ao baixar CSV: {response.status_code}")

# --- Execução principal


def main():
    os.makedirs("data/downloads", exist_ok=True)
    token = obter_token(EMAIL, PASSWORD)
    if not token:
        return

    file_url = buscar_url_csv(token)
    if not file_url:
        return

    output_path = "data/downloads/alertas_mapbiomas.csv"
    baixar_csv(file_url, output_path)


if __name__ == "__main__":
    main()
