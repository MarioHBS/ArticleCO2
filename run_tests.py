#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para executar testes unitários do pipeline de análise de carbono.

Este script executa todos os testes unitários e gera um relatório
de cobertura e resultados dos testes.
"""

import sys
<<<<<<< HEAD
=======
import os
>>>>>>> beb1535e6636cbb46b2a9dc8a71465b20f493e7b
import unittest
import logging
from pathlib import Path

# Configurar logging para testes
logging.basicConfig(
    level=logging.WARNING,  # Reduzir verbosidade durante testes
<<<<<<< HEAD
    format="%(asctime)s [%(levelname)s] %(message)s",
)


def run_all_tests():
    """
    Executa todos os testes unitários do projeto.

=======
    format="%(asctime)s [%(levelname)s] %(message)s"
)

def run_all_tests():
    """
    Executa todos os testes unitários do projeto.
    
>>>>>>> beb1535e6636cbb46b2a9dc8a71465b20f493e7b
    Returns:
        bool: True se todos os testes passaram, False caso contrário
    """
    print("=" * 60)
    print("EXECUTANDO TESTES UNITÁRIOS - PIPELINE CARBONO")
    print("=" * 60)
<<<<<<< HEAD

    # Descobrir e executar testes
    test_dir = Path(__file__).parent / "tests"

    if not test_dir.exists():
        print(f"Erro: Diretório de testes não encontrado: {test_dir}")
        return False

    # Descobrir testes automaticamente
    loader = unittest.TestLoader()
    start_dir = str(test_dir)
    suite = loader.discover(start_dir, pattern="test_*.py")

    # Executar testes
    runner = unittest.TextTestRunner(verbosity=2, stream=sys.stdout, buffer=True)

    result = runner.run(suite)

=======
    
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
    
>>>>>>> beb1535e6636cbb46b2a9dc8a71465b20f493e7b
    # Relatório final
    print("\n" + "=" * 60)
    print("RELATÓRIO FINAL DOS TESTES")
    print("=" * 60)
    print(f"Testes executados: {result.testsRun}")
    print(f"Falhas: {len(result.failures)}")
    print(f"Erros: {len(result.errors)}")
    print(f"Ignorados: {len(result.skipped)}")
<<<<<<< HEAD

=======
    
>>>>>>> beb1535e6636cbb46b2a9dc8a71465b20f493e7b
    if result.failures:
        print("\nFALHAS:")
        for test, traceback in result.failures:
            print(f"  - {test}: {traceback.split('AssertionError:')[-1].strip()}")
<<<<<<< HEAD

=======
    
>>>>>>> beb1535e6636cbb46b2a9dc8a71465b20f493e7b
    if result.errors:
        print("\nERROS:")
        for test, traceback in result.errors:
            print(f"  - {test}: {traceback.split('Exception:')[-1].strip()}")
<<<<<<< HEAD

    success = len(result.failures) == 0 and len(result.errors) == 0

=======
    
    success = len(result.failures) == 0 and len(result.errors) == 0
    
>>>>>>> beb1535e6636cbb46b2a9dc8a71465b20f493e7b
    if success:
        print("\n✅ TODOS OS TESTES PASSARAM!")
    else:
        print("\n❌ ALGUNS TESTES FALHARAM!")
<<<<<<< HEAD

    print("=" * 60)

=======
    
    print("=" * 60)
    
>>>>>>> beb1535e6636cbb46b2a9dc8a71465b20f493e7b
    return success


def run_specific_test(test_name: str):
    """
    Executa um teste específico.
<<<<<<< HEAD

=======
    
>>>>>>> beb1535e6636cbb46b2a9dc8a71465b20f493e7b
    Args:
        test_name: Nome do teste ou classe de teste
    """
    print(f"Executando teste específico: {test_name}")
<<<<<<< HEAD

    # Carregar teste específico
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromName(test_name)

    # Executar teste
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

=======
    
    # Carregar teste específico
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromName(test_name)
    
    # Executar teste
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
>>>>>>> beb1535e6636cbb46b2a9dc8a71465b20f493e7b
    return len(result.failures) == 0 and len(result.errors) == 0


def main():
    """
    Função principal do script de testes.
    """
    import argparse
<<<<<<< HEAD

    parser = argparse.ArgumentParser(description="Executa testes unitários do pipeline de carbono")
    parser.add_argument("--test", "-t", help="Nome de teste específico para executar")
    parser.add_argument("--verbose", "-v", action="store_true", help="Modo verboso (mais detalhes)")

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.INFO)

=======
    
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
    
>>>>>>> beb1535e6636cbb46b2a9dc8a71465b20f493e7b
    try:
        if args.test:
            success = run_specific_test(args.test)
        else:
            success = run_all_tests()
<<<<<<< HEAD

        sys.exit(0 if success else 1)

=======
        
        sys.exit(0 if success else 1)
        
>>>>>>> beb1535e6636cbb46b2a9dc8a71465b20f493e7b
    except Exception as e:
        print(f"Erro durante execução dos testes: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
<<<<<<< HEAD
    main()
=======
    main()
>>>>>>> beb1535e6636cbb46b2a9dc8a71465b20f493e7b
