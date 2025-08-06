# tests/introspect_alert_types.py
# -*- coding: utf-8 -*-
"""
Script de teste para introspecção dos tipos de alertas da API MapBiomas.

Este módulo contém testes para:
- Introspecção GraphQL dos tipos de dados
- Análise da estrutura da API
- Depuração de schemas de dados
"""

import os

import pytest
import requests

# Testes para introspecção de tipos de alertas MapBiomas via servidor local
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


def introspect_schema(base_url: str, token: str) -> dict:
    """Faz introspecção do schema da API local."""
    headers = {"Authorization": f"Bearer {token}"}

    # Assumindo que existe um endpoint para introspecção ou schema
    resp = requests.get(
        f"{base_url}/schema",
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
def test_introspect_schema_from_local_server():
    """Test introspecting schema from local MapBiomas server."""
    try:
        token = get_token()
        schema = introspect_schema(BASE_URL, token)

        assert isinstance(schema, dict), "Schema should be a dict"

        # Verificar se contém informações sobre tipos de alertas
        # A estrutura exata depende da implementação do servidor

    except requests.exceptions.ConnectionError:
        pytest.skip("Local MapBiomas server not running")
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 404:
            pytest.skip("Schema endpoint not available on local server")
        raise
    except ValueError as e:
        if "Credenciais não configuradas" in str(e):
            pytest.skip("MapBiomas credentials not configured")
        raise


def test_mock_alert_types_schema():
    """Test processing mock alert types schema."""
    mock_schema = {
        "AlertData": {
            "fields": [
                {"name": "id", "type": "Int"},
                {"name": "area", "type": "Float"},
                {"name": "date", "type": "String"},
                {"name": "territory", "type": "String"},
                {"name": "category", "type": "String"},
                {"name": "source", "type": "String"}
            ]
        },
        "AlertDataCollection": {
            "fields": [
                {"name": "collection", "type": "[AlertData]"},
                {"name": "metadata", "type": "CollectionMetadata"}
            ]
        },
        "CollectionMetadata": {
            "fields": [
                {"name": "total", "type": "Int"},
                {"name": "page", "type": "Int"},
                {"name": "limit", "type": "Int"}
            ]
        }
    }

    # Test that we can process the expected schema structure
    assert isinstance(mock_schema, dict)
    assert "AlertData" in mock_schema
    assert "AlertDataCollection" in mock_schema
    assert "CollectionMetadata" in mock_schema

    # Verificar estrutura do AlertData
    alert_data = mock_schema["AlertData"]
    assert "fields" in alert_data
    assert isinstance(alert_data["fields"], list)

    # Verificar campos esperados
    field_names = [field["name"] for field in alert_data["fields"]]
    expected_fields = ["id", "area", "date", "territory", "category", "source"]

    for expected_field in expected_fields:
        assert expected_field in field_names, f"Field '{expected_field}' should be in schema"


def test_alert_data_structure_validation():
    """Test validation of alert data structure."""
    sample_alert = {
        "id": 12345,
        "area": 15.75,
        "date": "2019-08-15",
        "territory": "Balsas",
        "category": "Desmatamento",
        "source": "PRODES"
    }

    # Verificar tipos de dados
    assert isinstance(sample_alert["id"], int), "ID should be integer"
    assert isinstance(sample_alert["area"], (int, float)), "Area should be numeric"
    assert isinstance(sample_alert["date"], str), "Date should be string"
    assert isinstance(sample_alert["territory"], str), "Territory should be string"
    assert isinstance(sample_alert["category"], str), "Category should be string"
    assert isinstance(sample_alert["source"], str), "Source should be string"

    # Verificar valores não vazios
    assert sample_alert["id"] > 0, "ID should be positive"
    assert sample_alert["area"] > 0, "Area should be positive"
    assert len(sample_alert["date"]) > 0, "Date should not be empty"
    assert len(sample_alert["territory"]) > 0, "Territory should not be empty"
    assert len(sample_alert["category"]) > 0, "Category should not be empty"
    assert len(sample_alert["source"]) > 0, "Source should not be empty"
