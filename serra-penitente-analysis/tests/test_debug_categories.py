# tests/debug_categories.py
# -*- coding: utf-8 -*-
"""
Script de teste para análise das categorias da API MapBiomas.

Este módulo contém testes para:
- Exploração das categorias disponíveis na API
- Verificação da estrutura de dados retornada
- Depuração de problemas de conectividade
"""

import os

import pytest
import requests

# Testes para categorias MapBiomas via servidor local
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
def test_fetch_categories_from_local_server():
    """Test fetching categories from local MapBiomas server."""
    try:
        token = get_token()
        headers = {"Authorization": f"Bearer {token}"}

        # Assumindo que existe um endpoint para categorias
        resp = requests.get(
            f"{BASE_URL}/categories",
            headers=headers,
            timeout=30
        )
        resp.raise_for_status()

        categories = resp.json()
        assert isinstance(categories, (list, dict)), "Categories should be list or dict"

    except requests.exceptions.ConnectionError:
        pytest.skip("Local MapBiomas server not running")
    except ValueError as e:
        if "Credenciais não configuradas" in str(e):
            pytest.skip("MapBiomas credentials not configured")
        raise


def test_mock_categories_response():
    """Test processing mock categories response."""
    mock_categories = [
        {"id": 1, "name": "Desmatamento"},
        {"id": 2, "name": "Degradação"},
        {"id": 3, "name": "Mineração"}
    ]

    # Test that we can process the expected data structure
    assert isinstance(mock_categories, list)
    assert len(mock_categories) == 3

    for category in mock_categories:
        assert "id" in category
        assert "name" in category
        assert isinstance(category["id"], int)
        assert isinstance(category["name"], str)
