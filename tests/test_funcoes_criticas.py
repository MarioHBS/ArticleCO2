# tests/test_funcoes_criticas.py
# -*- coding: utf-8 -*-
"""
Testes unitários para funções críticas do pipeline de análise de carbono.

Este módulo contém testes para:
- Validação de schemas de entrada
- Funções de parsing de municípios
- Funções de carregamento de dados
- Validação de integridade dos dados
"""

import os
import sys
import tempfile
import unittest

import numpy as np
import pandas as pd

from src.validacao import validate_carbono_schema, validate_pib_schema
from variaveis import MUNICIPIOS_ALVO, Municipio, granger_causality_matrix

# Adicionar src ao path
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "src"))


class TestMunicipio(unittest.TestCase):
    """Testes para a classe Municipio e funções relacionadas."""

    def test_municipio_creation(self):
        """Testa criação de instância Municipio."""
        municipio = Municipio(2100501, "Alto Parnaíba", "MA")
        self.assertEqual(municipio.id, 2100501)
        self.assertEqual(municipio.nome, "Alto Parnaíba")
        self.assertEqual(municipio.uf, "MA")

    def test_municipios_alvo_validos(self):
        """Testa se MUNICIPIOS_ALVO contém dados válidos."""
        self.assertGreater(len(MUNICIPIOS_ALVO), 0, "Lista de municípios não pode estar vazia")

        for municipio in MUNICIPIOS_ALVO:
            self.assertIsInstance(municipio, Municipio)
            self.assertIsInstance(municipio.id, int)
            self.assertGreater(municipio.id, 0, "ID do município deve ser positivo")
            self.assertIsInstance(municipio.nome, str)
            self.assertGreater(len(municipio.nome), 0, "Nome do município não pode estar vazio")
            self.assertIsInstance(municipio.uf, str)
            self.assertEqual(len(municipio.uf), 2, "UF deve ter 2 caracteres")

    def test_parse_municipio_ids(self):
        """Testa extração de IDs dos municípios."""
        ids = [m.id for m in MUNICIPIOS_ALVO]
        self.assertEqual(len(ids), len(set(ids)), "IDs de municípios devem ser únicos")
        self.assertTrue(all(isinstance(id_mun, int) for id_mun in ids))


class TestSchemaValidation(unittest.TestCase):
    """Testes para validação de schemas de entrada."""

    def test_pib_schema_validation(self):
        """Testa validação do schema de dados PIB."""
        # Schema válido
        valid_df = pd.DataFrame(
            {
                "codigo_ibge": [2100501, 2101400],
                "municipio": ["Alto Parnaíba", "Balsas"],
                "ano": [2020, 2020],
                "pib": [1000000, 2000000],
            }
        )

        # Teste com schema válido
        self.assertTrue(validate_pib_schema(valid_df))

        # Teste com schema inválido - coluna ausente
        invalid_df = valid_df.drop("pib", axis=1)
        with self.assertRaises(ValueError):
            validate_pib_schema(invalid_df)

        # Teste com DataFrame vazio
        empty_df = pd.DataFrame()
        with self.assertRaises(ValueError):
            validate_pib_schema(empty_df)

    def test_alertas_schema_validation(self):
        """Testa validação do schema de dados de alertas."""
        # Schema básico para alertas (pode variar conforme API)
        valid_df = pd.DataFrame(
            {
                "territory_id": [19606, 17294],
                "area_ha": [10.5, 25.3],
                "date": ["2023-01-15", "2023-02-20"],
            }
        )

        # Verificar se não está vazio
        self.assertGreater(len(valid_df), 0)

        # Verificar se tem colunas
        self.assertGreater(len(valid_df.columns), 0)

    def test_carbono_schema_validation(self):
        """Testa validação do schema de dados consolidados de carbono."""
        valid_df = pd.DataFrame(
            {
                "codigo_ibge": [2100501, 2101400],
                "ano": [2020, 2020],
                "pib": [1000000, 2000000],
                "GEE_tCO2e": [50000, 75000],
                "area_desmatada_ha": [100, 150],
            }
        )

        # Teste com schema válido
        self.assertTrue(validate_carbono_schema(valid_df))

        # Teste com schema inválido - coluna ausente
        invalid_df = valid_df.drop("pib", axis=1)
        with self.assertRaises(ValueError):
            validate_carbono_schema(invalid_df)

        # Teste com DataFrame vazio
        empty_df = pd.DataFrame()
        with self.assertRaises(ValueError):
            validate_carbono_schema(empty_df)


class TestDataIntegrity(unittest.TestCase):
    """Testes para validação de integridade dos dados."""

    def test_data_consistency(self):
        """Testa consistência básica dos dados."""
        # Criar dados de teste
        df = pd.DataFrame(
            {
                "codigo_ibge": [2100501, 2101400, 2112001],
                "ano": [2020, 2020, 2020],
                "pib": [1000000, 2000000, 1500000],
                "GEE_tCO2e": [50000, 75000, 60000],
                "area_desmatada_ha": [100, 150, 120],
            }
        )

        # Verificar valores não negativos para variáveis que devem ser positivas
        self.assertTrue((df["pib"] >= 0).all(), "PIB não pode ser negativo")
        self.assertTrue((df["GEE_tCO2e"] >= 0).all(), "Emissões GEE não podem ser negativas")
        self.assertTrue(
            (df["area_desmatada_ha"] >= 0).all(), "Área desmatada não pode ser negativa"
        )

        # Verificar anos válidos
        self.assertTrue((df["ano"] >= 2000).all(), "Anos devem ser >= 2000")
        self.assertTrue((df["ano"] <= 2030).all(), "Anos devem ser <= 2030")

    def test_missing_values_detection(self):
        """Testa detecção de valores ausentes."""
        # Dados com valores ausentes
        df_with_na = pd.DataFrame(
            {
                "codigo_ibge": [2100501, np.nan, 2112001],
                "ano": [2020, 2020, 2020],
                "pib": [1000000, 2000000, np.nan],
            }
        )

        # Verificar detecção de NAs
        self.assertTrue(df_with_na["codigo_ibge"].isna().any())
        self.assertTrue(df_with_na["pib"].isna().any())

        # Contar valores ausentes
        na_count = df_with_na.isna().sum().sum()
        self.assertEqual(na_count, 2)

    def test_duplicate_detection(self):
        """Testa detecção de duplicatas."""
        # Dados com duplicatas
        df_with_dups = pd.DataFrame(
            {
                "codigo_ibge": [2100501, 2100501, 2101400],
                "ano": [2020, 2020, 2020],
                "pib": [1000000, 1000000, 2000000],
            }
        )

        # Verificar detecção de duplicatas
        duplicates = df_with_dups.duplicated(subset=["codigo_ibge", "ano"])
        self.assertTrue(duplicates.any(), "Duplicatas devem ser detectadas")

        # Contar duplicatas
        dup_count = duplicates.sum()
        self.assertEqual(dup_count, 1)


class TestGrangerCausality(unittest.TestCase):
    """Testes para função de causalidade de Granger."""

    def test_granger_causality_basic(self):
        """Testa funcionamento básico da função de causalidade."""
        # Criar dados de teste com tendência
        np.random.seed(42)
        n = 100

        # Série temporal com relação causal simulada
        x = np.cumsum(np.random.randn(n))
        y = 0.5 * np.roll(x, 1) + np.random.randn(n) * 0.1  # y depende de x com lag

        df = pd.DataFrame({"x": x, "y": y})

        # Testar função
        result = granger_causality_matrix(df, ["x", "y"], maxlag=2, verbose=False)

        # Verificar formato do resultado
        self.assertIsInstance(result, pd.DataFrame)
        self.assertEqual(result.shape, (2, 2))
        self.assertTrue(all(col in result.columns for col in ["x", "y"]))
        self.assertTrue(all(idx in result.index for idx in ["x", "y"]))

    def test_granger_causality_edge_cases(self):
        """Testa casos extremos da função de causalidade."""
        # Dados insuficientes
        small_df = pd.DataFrame({"x": [1, 2], "y": [3, 4]})

        result = granger_causality_matrix(small_df, ["x", "y"], maxlag=4, verbose=False)
        self.assertIsInstance(result, pd.DataFrame)

        # Dados constantes
        const_df = pd.DataFrame({"x": [1, 1, 1, 1, 1], "y": [2, 2, 2, 2, 2]})

        result = granger_causality_matrix(const_df, ["x", "y"], maxlag=2, verbose=False)
        self.assertIsInstance(result, pd.DataFrame)


class TestFileOperations(unittest.TestCase):
    """Testes para operações de arquivo."""

    def test_csv_write_read_consistency(self):
        """Testa consistência de escrita e leitura de CSV."""
        # Criar dados de teste
        original_df = pd.DataFrame(
            {
                "codigo_ibge": [2100501, 2101400],
                "municipio": ["Alto Parnaíba", "Balsas"],
                "ano": [2020, 2021],
                "pib": [1000000.5, 2000000.7],
            }
        )

        # Usar arquivo temporário
        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as tmp:
            tmp_path = tmp.name

        try:
            # Escrever CSV
            original_df.to_csv(tmp_path, index=False, encoding="utf-8-sig")

            # Ler CSV
            read_df = pd.read_csv(tmp_path, encoding="utf-8-sig")

            # Verificar consistência
            pd.testing.assert_frame_equal(original_df, read_df)

        finally:
            # Limpar arquivo temporário
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)


if __name__ == "__main__":
    # Configurar logging para testes
    import logging

    logging.basicConfig(level=logging.WARNING)  # Reduzir verbosidade durante testes

    # Executar testes
    unittest.main(verbosity=2)
