#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de Teste Simples do Pipeline

Testa a execução do pipeline sem limpar dados anteriores.
"""

import subprocess
import sys
from pathlib import Path


def test_individual_scripts():
    """Testa scripts individuais."""
    print("=== TESTE DE SCRIPTS INDIVIDUAIS ===")

    scripts = [
        "src/01_extrair_pib_municipal.py",
        "src/02_extrair_cobertura_municipal.py",
        "src/07_gerar_figuras_carbono.py",
        "src/09_gerar_visualizacoes_idhm_desmatamento.py"
    ]

    results = {}
    serra_dir = Path("serra-penitente-analysis")

    for script in scripts:
        print(f"\n--- Testando {script} ---")
        try:
            result = subprocess.run(
                [sys.executable, script],
                cwd=serra_dir,  # Executar na pasta correta
                capture_output=True,
                text=True,
                timeout=300  # 5 minutos timeout
            )

            if result.returncode == 0:
                print(f"✅ {script} - SUCESSO")
                results[script] = True
            else:
                print(f"❌ {script} - FALHOU (código {result.returncode})")
                if result.stderr:
                    print(f"Erro: {result.stderr[:200]}...")
                results[script] = False

        except subprocess.TimeoutExpired:
            print(f"⏰ {script} - TIMEOUT")
            results[script] = False
        except Exception as e:
            print(f"💥 {script} - ERRO: {e}")
            results[script] = False

    return results


def test_server_status():
    """Testa se o servidor MapBiomas está funcionando."""
    print("=== TESTE DO SERVIDOR MAPBIOMAS ===")

    try:
        import requests
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code == 200:
            print("✅ Servidor MapBiomas - FUNCIONANDO")
            return True
        else:
            print(f"❌ Servidor MapBiomas - STATUS {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Servidor MapBiomas - ERRO: {e}")
        return False


def test_pipeline_validation():
    """Testa o pipeline de validação."""
    print("\n=== TESTE DO PIPELINE DE VALIDAÇÃO ===")

    try:
        result = subprocess.run(
            [sys.executable, "run_pipeline_validation.py"],
            cwd="serra-penitente-analysis",
            capture_output=True,
            text=True,
            timeout=600  # 10 minutos timeout
        )

        if result.returncode == 0:
            print("✅ Pipeline de validação - SUCESSO")
            return True
        else:
            print(f"❌ Pipeline de validação - FALHOU (código {result.returncode})")
            # Mostrar apenas as últimas linhas do erro
            if result.stdout:
                lines = result.stdout.split('\n')
                print("Últimas linhas da saída:")
                for line in lines[-10:]:
                    if line.strip():
                        print(f"  {line}")
            return False

    except subprocess.TimeoutExpired:
        print("⏰ Pipeline de validação - TIMEOUT")
        return False
    except Exception as e:
        print(f"💥 Pipeline de validação - ERRO: {e}")
        return False


def check_data_files():
    """Verifica se os arquivos de dados estão presentes."""
    print("=== VERIFICAÇÃO DE ARQUIVOS DE DADOS ===")

    data_files = [
        "serra-penitente-analysis/data/raw/pib_municipios_ibge_2002_2009.xls",
        "serra-penitente-analysis/data/raw/pib_municipios_ibge_2010_2021.xlsx",
        "serra-penitente-analysis/data/raw/cobertura_solo_mapbiomas_municipios_brasil.xlsx",
        "serra-penitente-analysis/data/raw/precos_carbono_eu_ets.xlsx",
        "serra-penitente-analysis/data/raw/idhm_municipios_serra_penitente.xlsx"
    ]

    all_present = True
    for file_path in data_files:
        if Path(file_path).exists():
            print(f"✅ {Path(file_path).name}")
        else:
            print(f"❌ {Path(file_path).name} - AUSENTE")
            all_present = False

    return all_present


def main():
    """Função principal."""
    print("TESTE SIMPLES DO PIPELINE SERRA PENITENTE")
    print("=" * 50)

    # Teste 0: Verificar arquivos de dados
    data_files_ok = check_data_files()

    # Teste 1: Verificar servidor
    server_ok = test_server_status()

    # Teste 2: Scripts individuais
    individual_results = test_individual_scripts()

    # Teste 3: Pipeline completo (apenas se os dados estiverem OK)
    if data_files_ok:
        pipeline_result = test_pipeline_validation()
    else:
        print("\n⚠️ Pulando teste do pipeline - arquivos de dados ausentes")
        pipeline_result = False

    # Resumo
    print("\n" + "=" * 50)
    print("RESUMO DOS TESTES")
    print("=" * 50)

    print(f"\n🗄️ Arquivos de Dados: {'✅ PRESENTES' if data_files_ok else '❌ AUSENTES'}")
    print(f"🌐 Servidor MapBiomas: {'✅ FUNCIONANDO' if server_ok else '❌ FALHOU'}")

    print("\n📊 Scripts Individuais:")
    for script, success in individual_results.items():
        status = "✅ SUCESSO" if success else "❌ FALHOU"
        script_name = Path(script).name
        print(f"  {script_name}: {status}")

    print(f"\n🔄 Pipeline Completo: {'✅ SUCESSO' if pipeline_result else '❌ FALHOU'}")

    # Resultado final
    individual_success = all(individual_results.values())
    overall_success = data_files_ok and server_ok and individual_success and pipeline_result

    print(f"\n🎯 RESULTADO GERAL: {'✅ TODOS OS TESTES PASSARAM' if overall_success else '❌ ALGUNS TESTES FALHARAM'}")

    if not overall_success:
        print("\n💡 SUGESTÕES:")
        if not data_files_ok:
            print("  - Verifique se todos os arquivos de dados estão na pasta data/raw/")
        if not server_ok:
            print("  - Inicie o servidor MapBiomas: python mapbiomas-alert-api/run_server.py")
        if not individual_success:
            print("  - Execute os scripts individuais para identificar problemas específicos")

    return 0 if overall_success else 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
