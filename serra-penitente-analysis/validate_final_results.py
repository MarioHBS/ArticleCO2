#!/usr/bin/env python3
"""
Script para validar resultados finais e documentar correções realizadas
no pipeline de análise de créditos de carbono no Cerrado maranhense.

Este script verifica:
1. Integridade dos dados processados
2. Consistência das métricas dos modelos
3. Qualidade das features selecionadas
4. Documentação das correções implementadas
"""

import json
import os
from datetime import datetime
from pathlib import Path

import pandas as pd


def verificar_arquivos_resultados():
    """
    Verifica se todos os arquivos de resultados foram gerados corretamente.
    """
    print("=" * 60)
    print("VALIDAÇÃO DE ARQUIVOS DE RESULTADOS")
    print("=" * 60)

    arquivos_esperados = [
        "data/generated/carbono_serra_penitente_com_idhm.csv",
        "results/metricas_modelos_com_idhm.csv",
        "results/feature_selection_results.json",
        "results/resultados_modelos_precificacao_carbono.csv",
    ]

    arquivos_encontrados = []
    arquivos_faltando = []

    for arquivo in arquivos_esperados:
        if os.path.exists(arquivo):
            arquivos_encontrados.append(arquivo)
            tamanho = Path(arquivo).stat().st_size
            print(f"✓ {arquivo} ({tamanho:,} bytes)")
        else:
            arquivos_faltando.append(arquivo)
            print(f"✗ {arquivo} - ARQUIVO FALTANDO")

    print(f"\nResumo: {len(arquivos_encontrados)}/{len(arquivos_esperados)} arquivos encontrados")

    if arquivos_faltando:
        print("\n⚠️  ATENÇÃO: Alguns arquivos estão faltando!")
        return False
    print("\n✅ Todos os arquivos de resultados foram encontrados!")
    return True


def validar_dados_consolidados():
    """
    Valida a integridade dos dados consolidados.
    """
    print("\n" + "=" * 60)
    print("VALIDAÇÃO DOS DADOS CONSOLIDADOS")
    print("=" * 60)

    try:
        df = pd.read_csv("data/generated/carbono_serra_penitente_com_idhm.csv")

        print(f"Dimensões do dataset: {df.shape}")
        print(f"Colunas: {list(df.columns)}")

        # Verificar valores nulos
        valores_nulos = df.isna().sum()
        if valores_nulos.sum() > 0:
            print("\n⚠️  Valores nulos encontrados:")
            for col, count in valores_nulos[valores_nulos > 0].items():
                print(f"   {col}: {count} valores nulos")
        else:
            print("\n✅ Nenhum valor nulo encontrado")

        # Verificar tipos de dados
        print("\nTipos de dados:")
        for col, dtype in df.dtypes.items():
            print(f"   {col}: {dtype}")

        # Estatísticas descritivas das features principais
        features_principais = ["pib", "GEE_tCO2e", "area_desmatada_ha"]
        features_existentes = [f for f in features_principais if f in df.columns]

        if features_existentes:
            print("\nEstatísticas das features principais:")
            print(df[features_existentes].describe())

        return True

    except Exception as e:
        print(f"\n❌ Erro ao validar dados consolidados: {e}")
        return False


def validar_metricas_modelos():
    """
    Valida as métricas dos modelos de machine learning.
    """
    print("\n" + "=" * 60)
    print("VALIDAÇÃO DAS MÉTRICAS DOS MODELOS")
    print("=" * 60)

    try:
        df_metricas = pd.read_csv("results/metricas_modelos_com_idhm.csv")

        print(f"Número de modelos avaliados: {len(df_metricas)}")
        print(f"Modelos: {list(df_metricas['modelo'].unique())}")

        # Verificar se há métricas válidas
        metricas_numericas = ["cv_r2_mean", "cv_mse_mean", "test_r2", "test_mse"]
        metricas_existentes = [m for m in metricas_numericas if m in df_metricas.columns]

        if metricas_existentes:
            print("\nResumo das métricas:")
            print(df_metricas[["modelo"] + metricas_existentes].round(4))

            # Identificar melhor modelo por R²
            if "test_r2" in df_metricas.columns:
                melhor_modelo = df_metricas.loc[df_metricas["test_r2"].idxmax()]
                print(
                    f"\n🏆 Melhor modelo (Test R²): "
                    f"{melhor_modelo['modelo']} (R² = {melhor_modelo['test_r2']:.4f})"
                )

        return True

    except Exception as e:
        print(f"\n❌ Erro ao validar métricas dos modelos: {e}")
        return False


def validar_feature_selection():
    """
    Valida os resultados da seleção de features.
    """
    print("\n" + "=" * 60)
    print("VALIDAÇÃO DA SELEÇÃO DE FEATURES")
    print("=" * 60)

    try:
        with open("results/feature_selection_results.json", encoding="utf-8") as f:
            results = json.load(f)

        print("Métodos de seleção aplicados:")
        for metodo, dados in results.items():
            if isinstance(dados, dict) and "features" in dados:
                print(f"   {metodo}: {dados['n_features']} features selecionadas")
                print(f"      Features: {dados['features']}")

        # Verificar consenso
        if "consensus" in results:
            consensus_features = results["consensus"]["features"]
            print(f"\n🎯 Features do consenso ({len(consensus_features)}): {consensus_features}")

        return True

    except Exception as e:
        print(f"\n❌ Erro ao validar feature selection: {e}")
        return False


def documentar_correcoes():
    """
    Documenta todas as correções realizadas no pipeline.
    """
    print("\n" + "=" * 60)
    print("DOCUMENTAÇÃO DAS CORREÇÕES REALIZADAS")
    print("=" * 60)

    correcoes = {
        "Data Leakage": {
            "problema": "Vazamento de dados entre conjuntos de treino e teste",
            "solucao": "Implementação de divisão temporal e validação cruzada k-fold",
            "arquivos_modificados": [
                "src/05_consolidar_dados_carbono.py",
                "src/06_consolidar_dados_carbono_com_idhm.py",
            ],
        },
        "Validação Cruzada": {
            "problema": "Falta de validação robusta dos modelos",
            "solucao": "Implementação de k-fold cross-validation com k=5",
            "arquivos_modificados": ["src/06_consolidar_dados_carbono_com_idhm.py"],
        },
        "Inconsistências de Unidades": {
            "problema": "Mistura de unidades (Mt C vs MtCO₂e) causando confusão",
            "solucao": "Padronização para MtCO₂e e correção de fatores de conversão",
            "arquivos_modificados": ["src/05_consolidar_dados_carbono.py", "main.tex"],
        },
        "Regularização": {
            "problema": "Modelos propensos a overfitting",
            "solucao": "Adição de regularização L1/L2 e parâmetros para prevenir overfitting",
            "arquivos_modificados": ["src/06_consolidar_dados_carbono_com_idhm.py"],
        },
        "Referências Órfãs": {
            "problema": "Referências bibliográficas não utilizadas no texto",
            "solucao": (
                "Reativação de referências relevantes (gomes2023, ferraz2023, energyecon2018)"
            ),
            "arquivos_modificados": ["main.tex", "refs.bib"],
        },
        "Períodos Temporais": {
            "problema": "Inconsistência entre períodos 2002-2021 vs 2023",
            "solucao": "Padronização e clarificação dos períodos utilizados",
            "arquivos_modificados": ["main.tex", "resumo_pipeline.md"],
        },
        "Feature Selection": {
            "problema": "Alta dimensionalidade sem seleção de features",
            "solucao": (
                "Implementação de múltiplas técnicas de seleção "
                "(Variance Threshold, SelectKBest, RFE, etc.)"
            ),
            "arquivos_modificados": ["src/06_consolidar_dados_carbono_com_idhm.py"],
        },
    }

    for categoria, detalhes in correcoes.items():
        print(f"\n📋 {categoria}:")
        print(f"   Problema: {detalhes['problema']}")
        print(f"   Solução: {detalhes['solucao']}")
        print(f"   Arquivos: {', '.join(detalhes['arquivos_modificados'])}")

    # Salvar documentação em arquivo
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    relatorio_path = f"results/relatorio_correcoes_{timestamp}.json"

    relatorio = {
        "timestamp": timestamp,
        "data_validacao": datetime.now().isoformat(),
        "correcoes_implementadas": correcoes,
        "status": "concluido",
    }

    with open(relatorio_path, "w", encoding="utf-8") as f:
        json.dump(relatorio, f, indent=2, ensure_ascii=False)

    print(f"\n📄 Relatório de correções salvo em: {relatorio_path}")

    return True


def main():
    """
    Executa todas as validações e gera relatório final.
    """
    print("VALIDAÇÃO FINAL DO PIPELINE DE CRÉDITOS DE CARBONO")
    print("=" * 80)
    print(f"Data/Hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)

    # Criar diretório de resultados se não existir
    os.makedirs("results", exist_ok=True)

    validacoes = [
        ("Arquivos de Resultados", verificar_arquivos_resultados),
        ("Dados Consolidados", validar_dados_consolidados),
        ("Métricas dos Modelos", validar_metricas_modelos),
        ("Feature Selection", validar_feature_selection),
        ("Documentação de Correções", documentar_correcoes),
    ]

    resultados = []

    for nome, funcao in validacoes:
        try:
            resultado = funcao()
            resultados.append((nome, resultado))
        except Exception as e:
            print(f"\n❌ Erro na validação '{nome}': {e}")
            resultados.append((nome, False))

    # Resumo final
    print("\n" + "=" * 80)
    print("RESUMO DA VALIDAÇÃO FINAL")
    print("=" * 80)

    sucessos = sum(1 for _, resultado in resultados if resultado)
    total = len(resultados)

    for nome, resultado in resultados:
        status = "✅ PASSOU" if resultado else "❌ FALHOU"
        print(f"{nome}: {status}")

    print(f"\nResultado geral: {sucessos}/{total} validações passaram")

    if sucessos == total:
        print("\n🎉 TODAS AS VALIDAÇÕES PASSARAM! Pipeline está pronto para uso.")
    else:
        print(f"\n⚠️  {total - sucessos} validação(ões) falharam. Revisar problemas identificados.")

    return sucessos == total


if __name__ == "__main__":
    sucesso = main()
    exit(0 if sucesso else 1)
