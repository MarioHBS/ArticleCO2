<<<<<<< HEAD
# src/validacao.py
=======
>>>>>>> beb1535e6636cbb46b2a9dc8a71465b20f493e7b
# -*- coding: utf-8 -*-
"""
Módulo de Validação de Dados - Pipeline de Análise de Carbono

Este módulo contém funções para validação de schemas e verificação de integridade
dos dados utilizados no pipeline de análise de carbono da Serra do Penitente.

Funções principais:
- validate_pib_schema(): Validação de estrutura de dados PIB
- validate_carbono_schema(): Validação de dados consolidados de carbono
- check_data_integrity(): Verificação de integridade básica dos dados
"""

<<<<<<< HEAD
import logging
from typing import Any, Dict

import numpy as np
import pandas as pd
=======
import pandas as pd
import numpy as np
import logging
from typing import Dict, Any
>>>>>>> beb1535e6636cbb46b2a9dc8a71465b20f493e7b


def validate_pib_schema(df: pd.DataFrame) -> bool:
    """
    Valida schema de dados PIB.
<<<<<<< HEAD

    Args:
        df: DataFrame com dados PIB

    Returns:
        bool: True se schema é válido

=======
    
    Args:
        df: DataFrame com dados PIB
        
    Returns:
        bool: True se schema é válido
        
>>>>>>> beb1535e6636cbb46b2a9dc8a71465b20f493e7b
    Raises:
        ValueError: Se schema é inválido
    """
    required_columns = ['codigo_ibge', 'municipio', 'ano', 'pib']
<<<<<<< HEAD

=======
    
>>>>>>> beb1535e6636cbb46b2a9dc8a71465b20f493e7b
    # Verificar colunas obrigatórias
    missing_cols = [col for col in required_columns if col not in df.columns]
    if missing_cols:
        raise ValueError(f"Colunas obrigatórias ausentes: {missing_cols}")
<<<<<<< HEAD

    # Verificar se DataFrame não está vazio
    if df.empty:
        raise ValueError("DataFrame PIB está vazio")

    # Verificar tipos de dados
    if not pd.api.types.is_integer_dtype(df['codigo_ibge']):
        raise ValueError("Coluna 'codigo_ibge' deve ser do tipo inteiro")

    if not pd.api.types.is_numeric_dtype(df['pib']):
        raise ValueError("Coluna 'pib' deve ser numérica")

    if not pd.api.types.is_integer_dtype(df['ano']):
        raise ValueError("Coluna 'ano' deve ser do tipo inteiro")

    # Verificar valores válidos
    if (df['codigo_ibge'] <= 0).any():
        raise ValueError("Códigos IBGE devem ser positivos")

    # Permitir valores negativos de PIB (podem representar déficits ou ajustes contábeis)
    # if (df['pib'] < 0).any():
    #     raise ValueError("Valores de PIB não podem ser negativos")

    if (df['ano'] < 2000).any() or (df['ano'] > 2030).any():
        raise ValueError("Anos devem estar entre 2000 e 2030")

=======
    
    # Verificar se DataFrame não está vazio
    if df.empty:
        raise ValueError("DataFrame PIB está vazio")
    
    # Verificar tipos de dados
    if not pd.api.types.is_integer_dtype(df['codigo_ibge']):
        raise ValueError("Coluna 'codigo_ibge' deve ser do tipo inteiro")
    
    if not pd.api.types.is_numeric_dtype(df['pib']):
        raise ValueError("Coluna 'pib' deve ser numérica")
    
    if not pd.api.types.is_integer_dtype(df['ano']):
        raise ValueError("Coluna 'ano' deve ser do tipo inteiro")
    
    # Verificar valores válidos
    if (df['codigo_ibge'] <= 0).any():
        raise ValueError("Códigos IBGE devem ser positivos")
    
    if (df['pib'] < 0).any():
        raise ValueError("Valores de PIB não podem ser negativos")
    
    if (df['ano'] < 2000).any() or (df['ano'] > 2030).any():
        raise ValueError("Anos devem estar entre 2000 e 2030")
    
>>>>>>> beb1535e6636cbb46b2a9dc8a71465b20f493e7b
    return True


def validate_carbono_schema(df: pd.DataFrame) -> bool:
    """
    Valida schema de dados consolidados de carbono.
<<<<<<< HEAD

    Args:
        df: DataFrame com dados consolidados

    Returns:
        bool: True se schema é válido

=======
    
    Args:
        df: DataFrame com dados consolidados
        
    Returns:
        bool: True se schema é válido
        
>>>>>>> beb1535e6636cbb46b2a9dc8a71465b20f493e7b
    Raises:
        ValueError: Se schema é inválido
    """
    # Features padrão para modelagem
    FEATURE_COLS = ['pib', 'GEE_tCO2e', 'area_desmatada_ha']
<<<<<<< HEAD

=======
    
>>>>>>> beb1535e6636cbb46b2a9dc8a71465b20f493e7b
    # Verificar colunas de features padrão
    for col in FEATURE_COLS:
        if col not in df.columns:
            raise ValueError(f"Coluna obrigatória '{col}' não encontrada")
<<<<<<< HEAD

        if not pd.api.types.is_numeric_dtype(df[col]):
            raise ValueError(f"Coluna '{col}' deve ser numérica")

    # Verificar se DataFrame não está vazio
    if df.empty:
        raise ValueError("DataFrame de carbono está vazio")

=======
        
        if not pd.api.types.is_numeric_dtype(df[col]):
            raise ValueError(f"Coluna '{col}' deve ser numérica")
    
    # Verificar se DataFrame não está vazio
    if df.empty:
        raise ValueError("DataFrame de carbono está vazio")
    
>>>>>>> beb1535e6636cbb46b2a9dc8a71465b20f493e7b
    # Verificar valores não negativos
    for col in ['pib', 'GEE_tCO2e', 'area_desmatada_ha']:
        if col in df.columns and (df[col] < 0).any():
            raise ValueError(f"Valores em '{col}' não podem ser negativos")
<<<<<<< HEAD

=======
    
>>>>>>> beb1535e6636cbb46b2a9dc8a71465b20f493e7b
    return True


def validate_alertas_schema(df: pd.DataFrame) -> bool:
    """
    Valida schema básico de dados de alertas de desmatamento.
<<<<<<< HEAD

    Args:
        df: DataFrame com dados de alertas

    Returns:
        bool: True se schema é válido

=======
    
    Args:
        df: DataFrame com dados de alertas
        
    Returns:
        bool: True se schema é válido
        
>>>>>>> beb1535e6636cbb46b2a9dc8a71465b20f493e7b
    Raises:
        ValueError: Se schema é inválido
    """
    # Verificar se DataFrame não está vazio
    if df.empty:
        raise ValueError("DataFrame de alertas está vazio")
<<<<<<< HEAD

    # Verificar se tem pelo menos algumas colunas básicas
    if len(df.columns) == 0:
        raise ValueError("DataFrame de alertas não possui colunas")

    # Verificar se tem dados
    if len(df) == 0:
        raise ValueError("DataFrame de alertas não possui registros")

=======
    
    # Verificar se tem pelo menos algumas colunas básicas
    if len(df.columns) == 0:
        raise ValueError("DataFrame de alertas não possui colunas")
    
    # Verificar se tem dados
    if len(df) == 0:
        raise ValueError("DataFrame de alertas não possui registros")
    
>>>>>>> beb1535e6636cbb46b2a9dc8a71465b20f493e7b
    return True


def validate_idhm_schema(df: pd.DataFrame) -> bool:
    """
    Valida schema de dados IDHM.
<<<<<<< HEAD

    Args:
        df: DataFrame com dados IDHM

    Returns:
        bool: True se schema é válido

=======
    
    Args:
        df: DataFrame com dados IDHM
        
    Returns:
        bool: True se schema é válido
        
>>>>>>> beb1535e6636cbb46b2a9dc8a71465b20f493e7b
    Raises:
        ValueError: Se schema é inválido
    """
    required_columns = ['codigo_ibge', 'idhm_']
<<<<<<< HEAD

=======
    
>>>>>>> beb1535e6636cbb46b2a9dc8a71465b20f493e7b
    # Verificar colunas obrigatórias
    missing_cols = [col for col in required_columns if col not in df.columns]
    if missing_cols:
        raise ValueError(f"Colunas obrigatórias IDHM ausentes: {missing_cols}")
<<<<<<< HEAD

    # Verificar se DataFrame não está vazio
    if df.empty:
        raise ValueError("DataFrame IDHM está vazio")

    # Verificar tipos de dados
    if not pd.api.types.is_integer_dtype(df['codigo_ibge']):
        raise ValueError("Coluna 'codigo_ibge' deve ser do tipo inteiro")

    if not pd.api.types.is_numeric_dtype(df['idhm_']):
        raise ValueError("Coluna 'idhm_' deve ser numérica")

    # Verificar valores válidos para IDHM (entre 0 e 1)
    if (df['idhm_'] < 0).any() or (df['idhm_'] > 1).any():
        raise ValueError("Valores de IDHM devem estar entre 0 e 1")

=======
    
    # Verificar se DataFrame não está vazio
    if df.empty:
        raise ValueError("DataFrame IDHM está vazio")
    
    # Verificar tipos de dados
    if not pd.api.types.is_integer_dtype(df['codigo_ibge']):
        raise ValueError("Coluna 'codigo_ibge' deve ser do tipo inteiro")
    
    if not pd.api.types.is_numeric_dtype(df['idhm_']):
        raise ValueError("Coluna 'idhm_' deve ser numérica")
    
    # Verificar valores válidos para IDHM (entre 0 e 1)
    if (df['idhm_'] < 0).any() or (df['idhm_'] > 1).any():
        raise ValueError("Valores de IDHM devem estar entre 0 e 1")
    
>>>>>>> beb1535e6636cbb46b2a9dc8a71465b20f493e7b
    return True


def check_data_integrity(df: pd.DataFrame, name: str = "DataFrame") -> Dict[str, Any]:
    """
    Verifica integridade básica dos dados.
<<<<<<< HEAD

    Args:
        df: DataFrame para verificar
        name: Nome do dataset para logging

=======
    
    Args:
        df: DataFrame para verificar
        name: Nome do dataset para logging
        
>>>>>>> beb1535e6636cbb46b2a9dc8a71465b20f493e7b
    Returns:
        dict: Relatório de integridade com estatísticas
    """
    report = {
        'total_rows': len(df),
        'total_columns': len(df.columns),
        'missing_values': df.isna().sum().sum(),
        'duplicate_rows': df.duplicated().sum(),
        'columns_with_na': df.columns[df.isna().any()].tolist(),
        'numeric_columns': df.select_dtypes(include=[np.number]).columns.tolist(),
        'object_columns': df.select_dtypes(include=['object']).columns.tolist()
    }
<<<<<<< HEAD

=======
    
>>>>>>> beb1535e6636cbb46b2a9dc8a71465b20f493e7b
    # Log do relatório
    logging.info(f"Relatório de integridade para {name}:")
    logging.info(f"  - Total de linhas: {report['total_rows']}")
    logging.info(f"  - Total de colunas: {report['total_columns']}")
    logging.info(f"  - Valores ausentes: {report['missing_values']}")
    logging.info(f"  - Linhas duplicadas: {report['duplicate_rows']}")
<<<<<<< HEAD

    if report['missing_values'] > 0:
        logging.warning(f"  - Colunas com valores ausentes: {report['columns_with_na']}")

    if report['duplicate_rows'] > 0:
        logging.warning(f"  - Encontradas {report['duplicate_rows']} linhas duplicadas")

    return report


def validate_year_range(
    df: pd.DataFrame, year_col: str = 'ano',
        min_year: int = 2000,
        max_year: int = 2030) -> bool:
    """
    Valida se os anos estão dentro de um intervalo válido.

=======
    
    if report['missing_values'] > 0:
        logging.warning(f"  - Colunas com valores ausentes: {report['columns_with_na']}")
    
    if report['duplicate_rows'] > 0:
        logging.warning(f"  - Encontradas {report['duplicate_rows']} linhas duplicadas")
    
    return report


def validate_year_range(df: pd.DataFrame, year_col: str = 'ano', 
                       min_year: int = 2000, max_year: int = 2030) -> bool:
    """
    Valida se os anos estão dentro de um intervalo válido.
    
>>>>>>> beb1535e6636cbb46b2a9dc8a71465b20f493e7b
    Args:
        df: DataFrame com coluna de ano
        year_col: Nome da coluna de ano
        min_year: Ano mínimo válido
        max_year: Ano máximo válido
<<<<<<< HEAD

    Returns:
        bool: True se todos os anos são válidos

=======
        
    Returns:
        bool: True se todos os anos são válidos
        
>>>>>>> beb1535e6636cbb46b2a9dc8a71465b20f493e7b
    Raises:
        ValueError: Se anos inválidos são encontrados
    """
    if year_col not in df.columns:
        raise ValueError(f"Coluna '{year_col}' não encontrada")
<<<<<<< HEAD

    invalid_years = df[(df[year_col] < min_year) | (df[year_col] > max_year)]

    if len(invalid_years) > 0:
        unique_invalid = invalid_years[year_col].unique()
        raise ValueError(
            f"Anos inválidos encontrados: {unique_invalid}. "
            f"Esperado entre {min_year} e {max_year}"
        )

=======
    
    invalid_years = df[(df[year_col] < min_year) | (df[year_col] > max_year)]
    
    if len(invalid_years) > 0:
        unique_invalid = invalid_years[year_col].unique()
        raise ValueError(f"Anos inválidos encontrados: {unique_invalid}. "
                        f"Esperado entre {min_year} e {max_year}")
    
>>>>>>> beb1535e6636cbb46b2a9dc8a71465b20f493e7b
    return True


def validate_positive_values(df: pd.DataFrame, columns: list) -> bool:
    """
    Valida se todas as colunas especificadas contêm apenas valores positivos.
<<<<<<< HEAD

    Args:
        df: DataFrame para validar
        columns: Lista de colunas que devem ter valores positivos

    Returns:
        bool: True se todos os valores são positivos

=======
    
    Args:
        df: DataFrame para validar
        columns: Lista de colunas que devem ter valores positivos
        
    Returns:
        bool: True se todos os valores são positivos
        
>>>>>>> beb1535e6636cbb46b2a9dc8a71465b20f493e7b
    Raises:
        ValueError: Se valores negativos são encontrados
    """
    for col in columns:
        if col not in df.columns:
            raise ValueError(f"Coluna '{col}' não encontrada")
<<<<<<< HEAD

        if not pd.api.types.is_numeric_dtype(df[col]):
            raise ValueError(f"Coluna '{col}' deve ser numérica")

        negative_count = (df[col] < 0).sum()
        if negative_count > 0:
            raise ValueError(f"Coluna '{col}' contém {negative_count} valores negativos")

=======
        
        if not pd.api.types.is_numeric_dtype(df[col]):
            raise ValueError(f"Coluna '{col}' deve ser numérica")
        
        negative_count = (df[col] < 0).sum()
        if negative_count > 0:
            raise ValueError(f"Coluna '{col}' contém {negative_count} valores negativos")
    
>>>>>>> beb1535e6636cbb46b2a9dc8a71465b20f493e7b
    return True


def validate_required_columns(df: pd.DataFrame, required_columns: list) -> bool:
    """
    Valida se todas as colunas obrigatórias estão presentes.
<<<<<<< HEAD

    Args:
        df: DataFrame para validar
        required_columns: Lista de colunas obrigatórias

    Returns:
        bool: True se todas as colunas estão presentes

=======
    
    Args:
        df: DataFrame para validar
        required_columns: Lista de colunas obrigatórias
        
    Returns:
        bool: True se todas as colunas estão presentes
        
>>>>>>> beb1535e6636cbb46b2a9dc8a71465b20f493e7b
    Raises:
        ValueError: Se colunas obrigatórias estão ausentes
    """
    missing_cols = [col for col in required_columns if col not in df.columns]
<<<<<<< HEAD

    if missing_cols:
        raise ValueError(f"Colunas obrigatórias ausentes: {missing_cols}")

    return True
=======
    
    if missing_cols:
        raise ValueError(f"Colunas obrigatórias ausentes: {missing_cols}")
    
    return True
>>>>>>> beb1535e6636cbb46b2a9dc8a71465b20f493e7b
