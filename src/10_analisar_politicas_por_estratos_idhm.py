# src/10_analisar_politicas_por_estratos_idhm.py
# -*- coding: utf-8 -*-
"""Script para analisar a efetividade de políticas ambientais por estratos de desenvolvimento.

Este script implementa o Passo 4 da análise, segmentando os municípios por níveis de IDHM
e avaliando como diferentes políticas ambientais impactam cada estrato de desenvolvimento.
"""

import os
import sys
import warnings

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score

# Configurar path para imports locais
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from variaveis import (  # noqa: E402
    FIGURE_PATHS,
    RESULT_PATHS,
)

warnings.filterwarnings("ignore")

# Configuração de estilo
plt.style.use("seaborn-v0_8")
sns.set_palette("husl")
plt.rcParams["figure.figsize"] = (12, 8)
plt.rcParams["font.size"] = 10


def carregar_dados_consolidados():
    """
    Carrega os dados consolidados com IDHM.

    Returns:
        pd.DataFrame: Dataset consolidado
    """
    print("Carregando dados consolidados com IDHM...")

    try:
        df = pd.read_csv(RESULT_PATHS.carbono_consolidado_com_idhm_csv)
        print(f"Dados carregados: {df.shape}")
        print(f"Colunas disponíveis: {df.columns.tolist()}")

        # Verificar se há dados de IDHM válidos
        colunas_idhm = [col for col in df.columns if "idhm" in col.lower()]
        print(f"Colunas IDHM encontradas: {colunas_idhm}")

        return df
    except Exception as e:
        print(f"Erro ao carregar dados: {e}")
        raise


def definir_estratos_desenvolvimento(df):
    """
    Define estratos de desenvolvimento baseados no IDHM.

    Args:
        df (pd.DataFrame): Dataset com dados de IDHM

    Returns:
        pd.DataFrame: Dataset com estratos definidos
    """
    print("Definindo estratos de desenvolvimento...")

    # Criar uma cópia do dataframe
    df_estratos = df.copy()

    # Verificar se há dados de IDHM válidos
    if "idhm_" in df.columns and df["idhm_"].sum() > 0:
        print("Usando dados de IDHM para classificação...")

        def classificar_estrato_idhm(idhm):
            if pd.isna(idhm) or idhm == 0:
                return "Não classificado"
            elif idhm < 0.550:
                return "Muito baixo desenvolvimento"
            elif idhm < 0.700:
                return "Baixo desenvolvimento"
            elif idhm < 0.800:
                return "Médio desenvolvimento"
            else:
                return "Alto desenvolvimento"

        df_estratos["estrato_desenvolvimento"] = df_estratos["idhm_"].apply(
            classificar_estrato_idhm
        )
    else:
        # Criar IDHM sintético baseado em PIB e área desmatada para demonstração
        print(
            "[AVISO] Dados de IDHM não encontrados ou zerados. "
            "Criando estratos baseados em PIB per capita..."
        )

        # Calcular PIB per capita aproximado (usando população estimada)
        df_estratos["pib_per_capita"] = df_estratos["pib"] / 10000  # Estimativa simplificada

        # Definir estratos baseados em quartis de PIB per capita
        quartis = df_estratos["pib_per_capita"].quantile([0.25, 0.5, 0.75])

        def classificar_estrato_pib(pib_pc):
            if pd.isna(pib_pc) or pib_pc == 0:
                return "Não classificado"
            elif pib_pc <= quartis[0.25]:
                return "Baixo desenvolvimento"
            elif pib_pc <= quartis[0.5]:
                return "Médio-baixo desenvolvimento"
            elif pib_pc <= quartis[0.75]:
                return "Médio-alto desenvolvimento"
            else:
                return "Alto desenvolvimento"

        df_estratos["estrato_desenvolvimento"] = df_estratos["pib_per_capita"].apply(
            classificar_estrato_pib
        )

    # Estatísticas dos estratos
    print("\nDistribuição dos estratos de desenvolvimento:")
    print(df_estratos["estrato_desenvolvimento"].value_counts())

    return df_estratos


def analisar_efetividade_por_estrato(df_estratos):
    """
    Analisa a efetividade de políticas ambientais por estrato de desenvolvimento.

    Args:
        df_estratos (pd.DataFrame): Dataset com estratos definidos

    Returns:
        dict: Resultados da análise por estrato
    """
    print("Analisando efetividade de políticas por estrato...")

    resultados = {}

    # Filtrar dados válidos
    df_valido = df_estratos[
        (df_estratos["estrato_desenvolvimento"] != "Não classificado")
        & (df_estratos["area_desmatada_ha"].notna())
        & (df_estratos["GEE_tCO2e"].notna())
        & (df_estratos["pib"].notna())
    ].copy()

    print(f"Dados válidos para análise: {len(df_valido)} registros")

    # Análise por estrato
    for estrato in df_valido["estrato_desenvolvimento"].unique():
        if estrato == "Não classificado":
            continue

        df_estrato = df_valido[df_valido["estrato_desenvolvimento"] == estrato]

        if len(df_estrato) < 5:  # Mínimo de observações
            continue

        print(f"\nAnalisando estrato: {estrato} ({len(df_estrato)} observações)")

        # Métricas ambientais
        metricas = {
            "n_observacoes": len(df_estrato),
            "desmatamento_medio": df_estrato["area_desmatada_ha"].mean(),
            "desmatamento_std": df_estrato["area_desmatada_ha"].std(),
            "emissoes_medias": df_estrato["GEE_tCO2e"].mean(),
            "emissoes_std": df_estrato["GEE_tCO2e"].std(),
            "pib_medio": df_estrato["pib"].mean(),
            "pib_std": df_estrato["pib"].std(),
        }

        # Análise de tendências temporais
        if len(df_estrato["ano"].unique()) > 3:
            # Regressão linear para tendência de desmatamento
            X = df_estrato["ano"].values.reshape(-1, 1)
            y_desmat = df_estrato["area_desmatada_ha"].values
            y_emissoes = df_estrato["GEE_tCO2e"].values

            # Tendência de desmatamento
            reg_desmat = LinearRegression().fit(X, y_desmat)
            metricas["tendencia_desmatamento"] = reg_desmat.coef_[0]
            metricas["r2_desmatamento"] = r2_score(y_desmat, reg_desmat.predict(X))

            # Tendência de emissões
            reg_emissoes = LinearRegression().fit(X, y_emissoes)
            metricas["tendencia_emissoes"] = reg_emissoes.coef_[0]
            metricas["r2_emissoes"] = r2_score(y_emissoes, reg_emissoes.predict(X))

        # Eficiência ambiental (emissões por unidade de PIB)
        df_estrato_pib = df_estrato[df_estrato["pib"] > 0]
        if len(df_estrato_pib) > 0:
            metricas["intensidade_carbono"] = (
                df_estrato_pib["GEE_tCO2e"] / df_estrato_pib["pib"]
            ).mean()
            metricas["intensidade_carbono_std"] = (
                df_estrato_pib["GEE_tCO2e"] / df_estrato_pib["pib"]
            ).std()

        resultados[estrato] = metricas

    return resultados


def gerar_visualizacoes_estratos(df_estratos, resultados):
    """
    Gera visualizações da análise por estratos.

    Args:
        df_estratos (pd.DataFrame): Dataset com estratos
        resultados (dict): Resultados da análise
    """
    print("Gerando visualizações da análise por estratos...")

    # Criar diretório de resultados
    os.makedirs("results/figures", exist_ok=True)

    # Filtrar dados válidos
    df_plot = df_estratos[
        (df_estratos["estrato_desenvolvimento"] != "Não classificado")
        & (df_estratos["area_desmatada_ha"].notna())
        & (df_estratos["GEE_tCO2e"].notna())
    ].copy()

    # 1. Boxplot de desmatamento por estrato
    plt.figure(figsize=(14, 8))

    plt.subplot(2, 2, 1)
    sns.boxplot(data=df_plot, x="estrato_desenvolvimento", y="area_desmatada_ha")
    plt.title("Distribuição do Desmatamento por Estrato de Desenvolvimento")
    plt.xlabel("Estrato de Desenvolvimento")
    plt.ylabel("Área Desmatada (ha)")
    plt.xticks(rotation=45)

    # 2. Boxplot de emissões por estrato
    plt.subplot(2, 2, 2)
    sns.boxplot(data=df_plot, x="estrato_desenvolvimento", y="GEE_tCO2e")
    plt.title("Distribuição das Emissões de GEE por Estrato")
    plt.xlabel("Estrato de Desenvolvimento")
    plt.ylabel("Emissões GEE (tCO2e)")
    plt.xticks(rotation=45)

    # 3. Evolução temporal por estrato
    plt.subplot(2, 2, 3)
    for estrato in df_plot["estrato_desenvolvimento"].unique():
        df_estrato = df_plot[df_plot["estrato_desenvolvimento"] == estrato]
        evolucao = df_estrato.groupby("ano")["area_desmatada_ha"].mean()
        plt.plot(evolucao.index, evolucao.values, marker="o", label=estrato, linewidth=2)

    plt.title("Evolução Temporal do Desmatamento por Estrato")
    plt.xlabel("Ano")
    plt.ylabel("Desmatamento Médio (ha)")
    plt.legend(bbox_to_anchor=(1.05, 1), loc="upper left")
    plt.grid(True, alpha=0.3)

    # 4. Intensidade de carbono por estrato
    plt.subplot(2, 2, 4)
    df_intensidade = df_plot[df_plot["pib"] > 0].copy()
    df_intensidade["intensidade_carbono"] = df_intensidade["GEE_tCO2e"] / df_intensidade["pib"]

    sns.boxplot(data=df_intensidade, x="estrato_desenvolvimento", y="intensidade_carbono")
    plt.title("Intensidade de Carbono por Estrato\n(tCO2e por unidade de PIB)")
    plt.xlabel("Estrato de Desenvolvimento")
    plt.ylabel("Intensidade de Carbono")
    plt.xticks(rotation=45)

    plt.tight_layout()
    plt.savefig(
        FIGURE_PATHS.figura13_analise_estratos_desenvolvimento_png, dpi=300, bbox_inches="tight"
    )
    plt.close()

    # 5. Heatmap de métricas por estrato
    plt.figure(figsize=(12, 8))

    # Preparar dados para heatmap
    metricas_heatmap = []
    estratos_ordem = []

    for estrato, metricas in resultados.items():
        if estrato != "Não classificado":
            estratos_ordem.append(estrato)
            metricas_heatmap.append(
                [
                    metricas.get("desmatamento_medio", 0),
                    metricas.get("emissoes_medias", 0),
                    metricas.get("intensidade_carbono", 0),
                    metricas.get("tendencia_desmatamento", 0),
                    metricas.get("tendencia_emissoes", 0),
                ]
            )

    if metricas_heatmap:
        df_heatmap = pd.DataFrame(
            metricas_heatmap,
            index=estratos_ordem,
            columns=[
                "Desmatamento\nMédio (ha)",
                "Emissões\nMédias (tCO2e)",
                "Intensidade\nCarbono",
                "Tendência\nDesmatamento",
                "Tendência\nEmissões",
            ],
        )

        # Normalizar dados para melhor visualização
        df_heatmap_norm = df_heatmap.div(df_heatmap.abs().max(), axis=1)

        sns.heatmap(
            df_heatmap_norm,
            annot=True,
            cmap="RdYlBu_r",
            center=0,
            fmt=".2f",
            cbar_kws={"label": "Valores Normalizados"},
        )
        plt.title("Índice de Causalidade: Métricas Ambientais por Estrato de Desenvolvimento")
        plt.ylabel("Estrato de Desenvolvimento")
        plt.xlabel("Métricas Ambientais")

        plt.tight_layout()
        plt.savefig(
            FIGURE_PATHS.figura14_heatmap_metricas_estratos_png, dpi=300, bbox_inches="tight"
        )
        plt.close()


def gerar_relatorio_estratos(resultados):
    """
    Gera relatório detalhado da análise por estratos.

    Args:
        resultados (dict): Resultados da análise
    """
    print("Gerando relatório da análise por estratos...")

    relatorio = []
    relatorio.append("RELATÓRIO DE ANÁLISE DE POLÍTICAS POR ESTRATOS DE DESENVOLVIMENTO")
    relatorio.append("=" * 80)
    relatorio.append("")
    relatorio.append(f"Data da análise: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}")
    relatorio.append(f"Número de estratos analisados: {len(resultados)}")
    relatorio.append("")

    # Análise por estrato
    for estrato, metricas in resultados.items():
        relatorio.append(f"ESTRATO: {estrato.upper()}")
        relatorio.append("-" * 50)
        relatorio.append(f"Número de observações: {metricas.get('n_observacoes', 'N/A')}")
        relatorio.append(
            f"Desmatamento médio: {metricas.get('desmatamento_medio', 0):.2f} ± "
            f"{metricas.get('desmatamento_std', 0):.2f} ha"
        )
        relatorio.append(
            f"Emissões médias: {metricas.get('emissoes_medias', 0):.2f} ± "
            f"{metricas.get('emissoes_std', 0):.2f} tCO2e"
        )
        relatorio.append(
            f"PIB médio: R$ {metricas.get('pib_medio', 0):,.2f} ± "
            f"{metricas.get('pib_std', 0):,.2f}"
        )

        if "intensidade_carbono" in metricas:
            relatorio.append(
                f"Intensidade de carbono: {metricas['intensidade_carbono']:.6f} ± "
                f"{metricas.get('intensidade_carbono_std', 0):.6f} tCO2e/R$"
            )

        if "tendencia_desmatamento" in metricas:
            relatorio.append(
                f"Tendência de desmatamento: {metricas['tendencia_desmatamento']:.2f} ha/ano "
                f"(R² = {metricas.get('r2_desmatamento', 0):.3f})"
            )
            relatorio.append(
                f"Tendência de emissões: {metricas['tendencia_emissoes']:.2f} tCO2e/ano "
                f"(R² = {metricas.get('r2_emissoes', 0):.3f})"
            )

        relatorio.append("")

    # Análise comparativa
    relatorio.append("ANÁLISE COMPARATIVA ENTRE ESTRATOS")
    relatorio.append("=" * 50)

    # Ranking por desmatamento
    estratos_desmat = [
        (estrato, metricas.get("desmatamento_medio", 0)) for estrato, metricas in resultados.items()
    ]
    estratos_desmat.sort(key=lambda x: x[1], reverse=True)

    relatorio.append("Ranking de desmatamento (maior para menor):")
    for i, (estrato, valor) in enumerate(estratos_desmat, 1):
        relatorio.append(f"{i}. {estrato}: {valor:.2f} ha")
    relatorio.append("")

    # Ranking por intensidade de carbono
    estratos_intensidade = [
        (estrato, metricas.get("intensidade_carbono", 0))
        for estrato, metricas in resultados.items()
        if "intensidade_carbono" in metricas
    ]
    estratos_intensidade.sort(key=lambda x: x[1], reverse=True)

    if estratos_intensidade:
        relatorio.append("Ranking de intensidade de carbono (maior para menor):")
        for i, (estrato, valor) in enumerate(estratos_intensidade, 1):
            relatorio.append(f"{i}. {estrato}: {valor:.6f} tCO2e/R$")
        relatorio.append("")

    # Recomendações de políticas
    relatorio.append("RECOMENDAÇÕES DE POLÍTICAS POR ESTRATO")
    relatorio.append("=" * 50)

    for estrato, metricas in resultados.items():
        relatorio.append(f"\n{estrato.upper()}:")

        desmat_medio = metricas.get("desmatamento_medio", 0)
        tendencia_desmat = metricas.get("tendencia_desmatamento", 0)
        intensidade = metricas.get("intensidade_carbono", 0)

        if desmat_medio > 1000:  # Alto desmatamento
            relatorio.append("- Prioridade ALTA para políticas de controle do desmatamento")
            relatorio.append("- Implementar monitoramento intensivo e fiscalização rigorosa")
            relatorio.append("- Programas de incentivos para conservação")
        elif desmat_medio > 100:
            relatorio.append("- Prioridade MÉDIA para políticas preventivas")
            relatorio.append("- Fortalecer capacidades locais de monitoramento")
        else:
            relatorio.append("- Manter políticas de conservação atuais")
            relatorio.append("- Foco em sustentabilidade e desenvolvimento verde")

        if tendencia_desmat > 0:
            relatorio.append("- ATENÇÃO: Tendência crescente de desmatamento")
            relatorio.append("- Revisar efetividade das políticas atuais")

        if intensidade > 0.001:  # Alta intensidade de carbono
            relatorio.append("- Promover eficiência energética e tecnologias limpas")
            relatorio.append("- Incentivar diversificação econômica sustentável")

    # Salvar relatório
    with open(
        RESULT_PATHS.relatorio_analise_estratos_desenvolvimento_txt, "w", encoding="utf-8"
    ) as f:
        f.write("\n".join(relatorio))

    print(f"Relatório salvo em: {RESULT_PATHS.relatorio_analise_estratos_desenvolvimento_txt}")


def main():
    """
    Função principal do script.
    """
    print("=" * 80)
    print("ANÁLISE DE EFETIVIDADE DE POLÍTICAS POR ESTRATOS DE DESENVOLVIMENTO")
    print("=" * 80)

    try:
        # 1. Carregar dados
        df = carregar_dados_consolidados()

        # 2. Definir estratos de desenvolvimento
        df_estratos = definir_estratos_desenvolvimento(df)

        # 3. Analisar efetividade por estrato
        resultados = analisar_efetividade_por_estrato(df_estratos)

        # 4. Gerar visualizações
        gerar_visualizacoes_estratos(df_estratos, resultados)

        # 5. Gerar relatório
        gerar_relatorio_estratos(resultados)

        print("\n" + "=" * 80)
        print("ANÁLISE CONCLUÍDA COM SUCESSO!")
        print("=" * 80)
        print("\nArquivos gerados:")
        print(f"- {FIGURE_PATHS.figura13_analise_estratos_desenvolvimento_png}")
        print(f"- {FIGURE_PATHS.figura14_heatmap_metricas_estratos_png}")
        print(f"- {RESULT_PATHS.relatorio_analise_estratos_desenvolvimento_txt}")

    except Exception as e:
        print(f"\n[ERROR] Erro durante a execução: {e}")
        import traceback

        traceback.print_exc()
        return False

    return True


if __name__ == "__main__":
    main()
