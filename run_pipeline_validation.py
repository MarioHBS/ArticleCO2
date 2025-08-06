#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Pipeline de Processamento de Dados de Carbono

Este script executa sequencialmente todos os scripts numerados do pipeline
de processamento de dados e geração de resultados.

Baseado em: run_pipeline_validation.ipynb
"""

import subprocess
import sys
import os
import glob
from src.variaveis import GENERATED_PATHS, RESULT_PATHS, SCRIPTS, FIGURE_PATHS


def safe_print(s: str):
    """Função para impressão segura com encoding."""
    try:
        print(s)
    except UnicodeEncodeError:
        clean = s.encode(sys.stdout.encoding, errors="replace").decode(sys.stdout.encoding)
        print(clean)


def check_files(files):
    """Verifica a existência de arquivos de saída."""
    status = True
    print(f"Verificando {len(files)} arquivo(s):")
    for f in files:
        if not os.path.exists(f):
            print(f"[MISSING] {f}")
            status = False
        else:
            print(f"[OK]      {f}")
    print(f"Resultado da verificação: {'SUCESSO' if status else 'FALHOU'}")
    return status


def run_script(script_name, expected_outputs=None, check_patterns=None):
    """Executa um script e verifica suas saídas."""
    print(f"\n=== Executando {script_name} ===")

    result = subprocess.run([sys.executable, script_name], capture_output=True, text=True)

    if result.stdout:
        safe_print(result.stdout)

    if result.returncode != 0:
        safe_print(f"[ERROR] {script_name} falhou (código de saída {result.returncode})")
        if result.stderr:
            safe_print(f"Erro: {result.stderr}")
        return False

    print(f"[OK] {script_name} executado com sucesso (código de saída {result.returncode})")

    # Verificar arquivos de saída
    if expected_outputs:
        print(f"Verificando saídas para {script_name}:")
        if not check_files(expected_outputs):
            return False

    # Verificar padrões de arquivos (para figuras)
    if check_patterns:
        print(f"Verificando padrões de arquivos para {script_name}:")
        for pattern in check_patterns:
            matches = glob.glob(pattern)
            if matches:
                print(f"[OK]      Padrão {pattern} -> {len(matches)} arquivo(s)")
            else:
                print(f"[MISSING] Padrão {pattern}")
                return False

    return True


def main():
    """Função principal do pipeline."""
    print("Iniciando Pipeline de Processamento de Dados de Carbono")
    print("=" * 60)

    all_ok = True
    step_results = []

    # Etapa 1: Extrair PIB municipal
    result1 = run_script(SCRIPTS.extrair_pib_municipal, [GENERATED_PATHS.pib_ibge_csv])
    step_results.append(("Etapa 1", result1))
    if not result1:
        all_ok = False

    # Etapa 2: Extrair cobertura municipal
    result2 = run_script(SCRIPTS.extrair_cobertura_municipal, [GENERATED_PATHS.mapbiomas_long_csv])
    step_results.append(("Etapa 2", result2))
    if not result2:
        all_ok = False

    # Etapa 3: Extrair alertas de desmatamento
    result3 = run_script(SCRIPTS.extrair_alertas_desmatamento, [GENERATED_PATHS.alertas_csv])
    step_results.append(("Etapa 3", result3))
    if not result3:
        all_ok = False

    # Etapa 4: Extrair séries temporais de uso da terra
    result4 = run_script(SCRIPTS.extrair_uso_terra_timeseries, [GENERATED_PATHS.uso_timeseries_csv])
    step_results.append(("Etapa 4", result4))
    if not result4:
        all_ok = False

    # Etapa 5: Consolidar dados de carbono
    result5 = run_script(
        SCRIPTS.consolidar_dados_carbono,
        [GENERATED_PATHS.carbono_consolidado_csv, RESULT_PATHS.model_results_csv],
    )
    step_results.append(("Etapa 5", result5))
    if not result5:
        all_ok = False

    # Etapa 6: Consolidar dados de carbono com IDHM
    result6 = run_script(
        SCRIPTS.consolidar_dados_carbono_com_idhm,
        [
            GENERATED_PATHS.carbono_consolidado_com_idhm_csv,
            RESULT_PATHS.metricas_modelos_com_idhm_csv,
        ],
    )
    step_results.append(("Etapa 6", result6))
    if not result6:
        all_ok = False

    # Etapa 7: Gerar figuras de carbono
    fig_dir = "results/figures"
    figure_patterns = []

    # Figuras específicas geradas pelo script 07_gerar_figuras_carbono.py
    figure_patterns.extend(
        [
            os.path.join(fig_dir, "Figura01_Evolucao_PIB.png"),
            os.path.join(fig_dir, "Figura03_Evolucao_GEE.png"),
            os.path.join(fig_dir, "Figura04_Evolucao_Desmatamento.png"),
            os.path.join(fig_dir, "Figura05_EQM_Modelos.png"),
            os.path.join(fig_dir, "Figura06_Causalidade_Granger.png"),
        ]
    )

    # Figuras 07_1 a 07_9 (scatters)
    for i in range(1, 10):
        figure_patterns.append(os.path.join(fig_dir, f"Figura07_{i}_*.png"))

    # Figuras específicas
    figure_patterns.extend(
        [
            os.path.join(fig_dir, "Figura08_Importancia_Variaveis.png"),
            os.path.join(fig_dir, "Figura09_Evolucao_Preco_Carbono.png"),
        ]
    )

    result7 = run_script(SCRIPTS.gerar_figuras_carbono, check_patterns=figure_patterns)
    step_results.append(("Etapa 7", result7))
    if not result7:
        all_ok = False

    # Etapa 8: Comparar modelos com e sem IDHM
    result8 = run_script(
        SCRIPTS.comparar_modelos_com_sem_idhm,
        [
            FIGURE_PATHS.comparacao_modelos_com_sem_idhm_png,
            FIGURE_PATHS.melhorias_percentuais_idhm_png,
        ],
    )
    step_results.append(("Etapa 8", result8))
    if not result8:
        all_ok = False

    # Etapa 9: Gerar visualizações IDHM vs Desmatamento
    result9 = run_script(
        SCRIPTS.gerar_visualizacoes_idhm_desmatamento,
        [
            FIGURE_PATHS.figura10_correlacao_idhm_desmatamento_png,
            FIGURE_PATHS.figura11_evolucao_temporal_idhm_desmatamento_png,
            FIGURE_PATHS.figura12_heatmap_correlacao_idhm_png,
        ],
    )
    step_results.append(("Etapa 9", result9))
    if not result9:
        all_ok = False

    # Etapa 10: Gerar figuras consolidadas
    consolidated_patterns = [
        "results/figuras_consolidadas/Figura01_Paineis_GEE_PIB.pdf",
        "results/figuras_consolidadas/Figura02_Comparacao_MSE.pdf",
        "results/figuras_consolidadas/Figura03_Importancia_RF.pdf",
        "results/figuras_consolidadas/Figura04_Matriz_Causalidade_Granger.pdf",
    ]

    result10 = run_script(
        SCRIPTS.gerar_figuras_consolidadas, expected_outputs=consolidated_patterns
    )
    step_results.append(("Etapa 10", result10))
    if not result10:
        all_ok = False

    # Etapa 11: Analisar políticas por estratos de desenvolvimento
    result11 = run_script(
        SCRIPTS.analisar_politicas_por_estratos_idhm,
        [
            FIGURE_PATHS.figura13_analise_estratos_desenvolvimento_png,
            FIGURE_PATHS.figura14_heatmap_metricas_estratos_png,
            "results/relatorio_analise_estratos_desenvolvimento.txt",
        ],
    )
    step_results.append(("Etapa 11", result11))
    if not result11:
        all_ok = False

    # Resultado final
    print("\n" + "=" * 60)
    print("RESUMO DO PIPELINE:")
    for step_name, step_ok in step_results:
        status = "[OK]" if step_ok else "[FALHOU]"
        print(f"  {step_name}: {status}")

    print("\n" + "=" * 60)
    if all_ok:
        print("[OK] PIPELINE EXECUTADO COM SUCESSO!")
        print("Todos os scripts foram executados e todas as saídas foram geradas.")
        return 0
    else:
        print("[ERROR] PIPELINE FALHOU!")
        print("Um ou mais scripts falharam ou arquivos de saída estão ausentes.")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
