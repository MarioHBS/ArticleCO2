# tests/test_list_territories.py
# -*- coding: utf-8 -*-
"""
Testes para listagem de territórios da API MapBiomas.

Este módulo contém testes para:
- Listagem de territórios disponíveis
- Validação de conectividade com API local
- Depuração de problemas de autenticação
"""

import os

import pytest
import requests

# Testes para listagem de territórios MapBiomas via servidor local
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


def list_territories(base_url: str, token: str) -> list:
    """Lista territórios disponíveis da API local."""
    headers = {"Authorization": f"Bearer {token}"}

    # Assumindo que existe um endpoint para listar territórios
    resp = requests.get(
        f"{base_url}/territories",
        headers=headers,
        timeout=30
    )
    resp.raise_for_status()

    return resp.json()


def test_requests_available():
    """Test if requests module is available."""
    assert requests is not None, "Requests module should be available"


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
def test_list_territories_from_local_server():
    """Test listing territories from local MapBiomas server."""
    try:
        token = get_token()
        territories = list_territories(BASE_URL, token)

        assert isinstance(territories, list), "Territories should be a list"

        if territories:  # Se há territórios na resposta
            # Verificar estrutura do primeiro território
            first_territory = territories[0]
            assert isinstance(first_territory, dict), "Territory should be a dict"

            # Campos esperados em um território
            expected_fields = ["id", "name", "type"]
            for field in expected_fields:
                if field in first_territory:
                    assert isinstance(first_territory[field], (str, int)), \
                        f"Field '{field}' should be string or int"

    except requests.exceptions.ConnectionError:
        pytest.skip("Local MapBiomas server not running")
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 404:
            pytest.skip("Territories endpoint not available on local server")
        raise
    except ValueError as e:
        if "Credenciais não configuradas" in str(e):
            pytest.skip("MapBiomas credentials not configured")
        raise


def test_mock_territories_list():
    """Test processing mock territories list."""
    mock_territories = [
        {
            "id": 1,
            "name": "Balsas",
            "type": "municipality",
            "state": "MA",
            "region": "Nordeste"
        },
        {
            "id": 2,
            "name": "São Félix do Xingu",
            "type": "municipality",
            "state": "PA",
            "region": "Norte"
        },
        {
            "id": 3,
            "name": "Maranhão",
            "type": "state",
            "region": "Nordeste"
        }
    ]

    # Test that we can process the expected territories structure
    assert isinstance(mock_territories, list)
    assert len(mock_territories) > 0

    for territory in mock_territories:
        assert isinstance(territory, dict)
        assert "id" in territory
        assert "name" in territory
        assert "type" in territory

        # Verificar tipos de dados
        assert isinstance(territory["id"], int), "Territory ID should be integer"
        assert isinstance(territory["name"], str), "Territory name should be string"
        assert isinstance(territory["type"], str), "Territory type should be string"

        # Verificar valores não vazios
        assert territory["id"] > 0, "Territory ID should be positive"
        assert len(territory["name"]) > 0, "Territory name should not be empty"
        assert len(territory["type"]) > 0, "Territory type should not be empty"


def test_territory_filtering():
    """Test filtering territories by type."""
    mock_territories = [
        {"id": 1, "name": "Balsas", "type": "municipality"},
        {"id": 2, "name": "São Félix do Xingu", "type": "municipality"},
        {"id": 3, "name": "Maranhão", "type": "state"},
        {"id": 4, "name": "Pará", "type": "state"}
    ]

    # Filtrar apenas municípios
    municipalities = [t for t in mock_territories if t["type"] == "municipality"]
    assert len(municipalities) == 2
    assert all(t["type"] == "municipality" for t in municipalities)

    # Filtrar apenas estados
    states = [t for t in mock_territories if t["type"] == "state"]
    assert len(states) == 2
    assert all(t["type"] == "state" for t in states)


def test_territory_search():
    """Test searching territories by name."""
    mock_territories = [
        {"id": 1, "name": "Balsas", "type": "municipality"},
        {"id": 2, "name": "São Félix do Xingu", "type": "municipality"},
        {"id": 3, "name": "Maranhão", "type": "state"}
    ]

    # Buscar por nome exato
    balsas = [t for t in mock_territories if t["name"] == "Balsas"]
    assert len(balsas) == 1
    assert balsas[0]["id"] == 1

    # Buscar por nome parcial (case insensitive)
    felix_results = [t for t in mock_territories if "félix" in t["name"].lower()]
    assert len(felix_results) == 1
    assert felix_results[0]["name"] == "São Félix do Xingu"
