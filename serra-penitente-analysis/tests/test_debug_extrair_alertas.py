# tests/debug_extrair_alertas.py
# -*- coding: utf-8 -*-
"""
Script de teste para extração de alertas de desmatamento.

Este módulo contém testes para:
- Extração de alertas via API MapBiomas
- Validação de dados retornados
- Depuração de problemas na extração
"""

import os

import pytest
import requests

# Testes para extração de alertas MapBiomas via servidor local
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


def fetch_all_alerts(
    base_url: str,
    token: str,
    start_date: str,
    end_date: str,
    territory_ids: list
) -> list:
    """Chama /alerts/all e retorna a lista de alertas."""
    headers = {"Authorization": f"Bearer {token}"}
    params = {
        "startDate": start_date,
        "endDate": end_date,
        "territoryIds": ",".join(str(i) for i in territory_ids)
    }

    resp = requests.get(
        f"{base_url}/alerts/all",
        headers=headers,
        params=params,
        timeout=300
    )
    resp.raise_for_status()

    data = resp.json()
    return data.get("collection", [])


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
def test_fetch_alerts_from_local_server():
    """Test fetching alerts from local MapBiomas server."""
    try:
        token = get_token()
        territory_ids = [19606, 17294, 17994]  # IDs dos municípios da Serra do Penitente
        start_date = "2019-01-01"
        end_date = "2020-01-01"

        alerts = fetch_all_alerts(BASE_URL, token, start_date, end_date, territory_ids)
        assert isinstance(alerts, list), "Alerts should be a list"

        # Se houver alertas, verificar estrutura
        if alerts:
            for alert in alerts[:3]:  # Verificar apenas os primeiros 3
                assert isinstance(alert, dict), "Each alert should be a dict"

    except requests.exceptions.ConnectionError:
        pytest.skip("Local MapBiomas server not running")
    except ValueError as e:
        if "Credenciais não configuradas" in str(e):
            pytest.skip("MapBiomas credentials not configured")
        raise


def test_mock_alerts_response():
    """Test processing mock alerts response."""
    mock_alerts = [
        {
            "id": 1,
            "area": 10.5,
            "date": "2019-06-15",
            "territory": "Balsas",
            "category": "Desmatamento"
        },
        {
            "id": 2,
            "area": 25.3,
            "date": "2019-07-20",
            "territory": "Tasso Fragoso",
            "category": "Degradação"
        }
    ]

    # Test that we can process the expected data structure
    assert isinstance(mock_alerts, list)
    assert len(mock_alerts) == 2

    for alert in mock_alerts:
        assert "id" in alert
        assert "area" in alert
        assert "date" in alert
        assert "territory" in alert
        assert "category" in alert
        assert isinstance(alert["area"], (int, float))
        assert isinstance(alert["date"], str)
        assert isinstance(alert["territory"], str)
        assert isinstance(alert["category"], str)
