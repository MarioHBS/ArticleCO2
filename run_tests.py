#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para executar testes unitários do pipeline de análise de carbono.

Este script executa todos os testes unitários e gera um relatório
de cobertura e resultados dos testes.
"""

import sys
import os
import unittest
import logging
from pathlib import Path

# Configurar logging para testes
logging.basicConfig(
    level=logging.WARNING,  # Reduzir verbosidade durante testes
    format="%(asctime)s [%(levelname)s] %(message)s"
)

def run_all_tests():
    """
    Executa todos os testes unitários do projeto.
    
    Returns:
        bool: True se todos os testes passaram, False caso contrário
    """
    print("=" * 60)
    print("EXECUTANDO TESTES UNITÁRIOS - PIPELINE CARBONO")
    print("=" * 60)
    
    # Descobrir e executar testes
    test_dir = Path(__file__).parent / "tests"
    
    if not test_dir.exists():
        print(f"Erro: Diretório de testes não encontrado: {test_dir}")
        return False
    
    # Descobrir testes automaticamente
    loader = unittest.TestLoader()
    start_dir = str(test_dir)
    suite = loader.discover(start_dir, pattern='test_*.py')
    
    # Executar testes
    runner = unittest.TextTestRunner(
        verbosity=2,
        stream=sys.stdout,
        buffer=True
    )
    
    result = runner.run(suite)
    
    # Relatório final
    print("\n" + "=" * 60)
    print("RELATÓRIO FINAL DOS TESTES")
    print("=" * 60)
    print(f"Testes executados: {result.testsRun}")
    print(f"Falhas: {len(result.failures)}")
    print(f"Erros: {len(result.errors)}")
    print(f"Ignorados: {len(result.skipped)}")
    
    if result.failures:
        print("\nFALHAS:")
        for test, traceback in result.failures:
            print(f"  - {test}: {traceback.split('AssertionError:')[-1].strip()}")
    
    if result.errors:
        print("\nERROS:")
        for test, traceback in result.errors:
            print(f"  - {test}: {traceback.split('Exception:')[-1].strip()}")
    
    success = len(result.failures) == 0 and len(result.errors) == 0
    
    if success:
        print("\n✅ TODOS OS TESTES PASSARAM!")
    else:
        print("\n❌ ALGUNS TESTES FALHARAM!")
    
    print("=" * 60)
    
    return success


def run_specific_test(test_name: str):
    """
    Executa um teste específico.
    
    Args:
        test_name: Nome do teste ou classe de teste
    """
    print(f"Executando teste específico: {test_name}")
    
    # Carregar teste específico
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromName(test_name)
    
    # Executar teste
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return len(result.failures) == 0 and len(result.errors) == 0


def main():
    """
    Função principal do script de testes.
    """
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Executa testes unitários do pipeline de carbono"
    )
    parser.add_argument(
        "--test", "-t",
        help="Nome de teste específico para executar"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Modo verboso (mais detalhes)"
    )
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.INFO)
    
    try:
        if args.test:
            success = run_specific_test(args.test)
        else:
            success = run_all_tests()
        
        sys.exit(0 if success else 1)
        
    except Exception as e:
        print(f"Erro durante execução dos testes: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()