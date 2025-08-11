# tests/test_get_municipality_ids.py
# -*- coding: utf-8 -*-
"""
Testes para obtenção de IDs de municípios da API MapBiomas.

Este módulo contém testes para:
    - Busca de IDs de municípios na API
    - Validação de correspondência de nomes
    - Depuração de problemas de identificação
"""

import os

import pytest
import requests
from unidecode import unidecode

# Testes para obtenção de IDs de municípios MapBiomas via servidor local
# Baseado na implementação do arquivo 03_extrair_alertas_desmatamento.py

BASE_URL = "http://localhost:8000"


def get_token(base_url: str = BASE_URL) -> str:
    """Obtém token da API local via /token."""
    email = os.getenv("MAPBIOMAS_EMAIL")
    pwd = os.getenv("MAPBIOMAS_PASSWORD")

    if not email or not pwd:
        raise ValueError(
            "Credenciais não configuradas: defina MAPBIOMAS_EMAIL e MAPBIOMAS_PASSWORD"
        )

    resp = requests.post(
        f"{base_url}/token",
        json={"email": email, "password": pwd},
        timeout=30
    )
    resp.raise_for_status()

    token_data = resp.json()
    if "token" not in token_data:
        raise ValueError("Resposta da API não contém token válido")

    return token_data["token"]


def fetch_territory_options(base_url: str, token: str) -> list:
    """Busca opções de território da API local."""
    headers = {"Authorization": f"Bearer {token}"}

    resp = requests.get(
        f"{base_url}/territories/options",
        headers=headers,
        timeout=30
    )
    resp.raise_for_status()

    return resp.json()


def normalize(s: str) -> str:
    """Remove acentos e coloca em caixa alta."""
    return unidecode(s).strip().upper()


def extract_target_ids(options: list, targets: list) -> dict:
    """Extrai IDs dos municípios alvo."""
    # Filtra pela categoria "Município", normalizada
    munis_opts = [opt for opt in options if normalize(opt.get("categoryName", "")) == "MUNICIPIO"]

    # Achata todas as listas de territórios
    all_munis = []
    for opt in munis_opts:
        all_munis.extend(opt.get("territories", []))

    # Mapeia NOME_NORMALIZADO → code
    mapping = {normalize(t["name"]): t["code"] for t in all_munis}

    # Para cada alvo, tenta correspondência exata na versão normalizada
    result = {}
    for tgt in targets:
        key = normalize(tgt)
        result[tgt] = mapping.get(key)

    return result


def test_requests_available():
    """Test if requests module is available."""
    assert requests is not None, "Requests module should be available"


def test_unidecode_available():
    """Test if unidecode module is available."""
    assert unidecode is not None, "Unidecode module should be available"

    # Test normalize function
    test_string = "São Paulo"
    normalized = normalize(test_string)
    assert normalized == "SAO PAULO", f"Expected 'SAO PAULO', got '{normalized}'"


def test_environment_variables():
    """Test if required environment variables are set."""
    email = os.getenv("MAPBIOMAS_EMAIL")
    password = os.getenv("MAPBIOMAS_PASSWORD")

    if not email or not password:
        pytest.skip("MapBiomas credentials not configured - skipping test")

    assert email is not None, "MAPBIOMAS_EMAIL should be set"
    assert password is not None, "MAPBIOMAS_PASSWORD should be set"


@pytest.mark.skip(reason="Requires local MapBiomas server running")
def test_get_token_from_local_server():
    """Test getting token from local MapBiomas server."""
    try:
        token = get_token()
        assert token is not None, "Token should not be None"
        assert isinstance(token, str), "Token should be a string"
        assert len(token) > 0, "Token should not be empty"
    except requests.exceptions.ConnectionError:
        pytest.skip("Local MapBiomas server not running")
    except ValueError as e:
        if "Credenciais não configuradas" in str(e):
            pytest.skip("MapBiomas credentials not configured")
        raise


@pytest.mark.skip(reason="Requires local MapBiomas server running")
def test_fetch_territory_options_from_local_server():
    """Test fetching territory options from local MapBiomas server."""
    try:
        token = get_token()
        options = fetch_territory_options(BASE_URL, token)

        assert isinstance(options, list), "Territory options should be a list"

        # Se houver opções, verificar estrutura
        if options:
            for option in options[:3]:  # Verificar apenas as primeiras 3
                assert isinstance(option, dict), "Each option should be a dict"
                assert "categoryName" in option, "Option should have categoryName"
                assert "territories" in option, "Option should have territories"

    except requests.exceptions.ConnectionError:
        pytest.skip("Local MapBiomas server not running")
    except ValueError as e:
        if "Credenciais não configuradas" in str(e):
            pytest.skip("MapBiomas credentials not configured")
        raise


def test_extract_target_ids_with_mock_data():
    """Test extracting target IDs with mock data."""
    mock_options = [
        {
            "categoryName": "Município",
            "territories": [
                {"code": "2101251", "name": "Balsas"},
                {"code": "2112001", "name": "Tasso Fragoso"},
                {"code": "2100400", "name": "Alto Parnaíba"}
            ]
        },
        {
            "categoryName": "Estado",
            "territories": [
                {"code": "21", "name": "Maranhão"}
            ]
        }
    ]

    targets = ["Balsas", "Tasso Fragoso", "Alto Parnaíba"]
    result = extract_target_ids(mock_options, targets)

    assert isinstance(result, dict), "Result should be a dict"
    assert len(result) == 3, "Should have 3 results"
    assert result["Balsas"] == "2101251", "Balsas ID should match"
    assert result["Tasso Fragoso"] == "2112001", "Tasso Fragoso ID should match"
    assert result["Alto Parnaíba"] == "2100400", "Alto Parnaíba ID should match"


def test_normalize_function():
    """Test the normalize function with various inputs."""
    test_cases = [
        ("São Paulo", "SAO PAULO"),
        ("Brasília", "BRASILIA"),
        ("  Rio de Janeiro  ", "RIO DE JANEIRO"),
        ("Belo Horizonte", "BELO HORIZONTE"),
        ("Açailândia", "ACAILANDIA")
    ]

    for input_str, expected in test_cases:
        result = normalize(input_str)
        assert result == expected, f"normalize('{input_str}') expected '{expected}', got '{result}'"
