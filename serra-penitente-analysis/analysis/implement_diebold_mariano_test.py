#!/usr/bin/env python3
"""
Implementação do Teste Diebold-Mariano para Comparação de Modelos

Este script implementa o teste Diebold-Mariano para comparar estatisticamente
a performance preditiva de diferentes modelos de machine learning.

O teste Diebold-Mariano é usado para:
- Testar se dois modelos têm performance estatisticamente diferente
- Validar se melhorias observadas são significativas
- Fornecer evidência estatística robusta para seleção de modelos

Autor: Sistema de IA
Data: 2025-01-15
"""

import os
import warnings

import numpy as np
import pandas as pd
from scipy import stats
from sklearn.dummy import DummyRegressor
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import Lasso, LinearRegression
from sklearn.model_selection import TimeSeriesSplit
from sklearn.neighbors import KNeighborsRegressor
from sklearn.neural_network import MLPRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVR
from sklearn.tree import DecisionTreeRegressor

warnings.filterwarnings("ignore")


def diebold_mariano_test(errors1, errors2, h=1):
    """
    Implementa o teste Diebold-Mariano para comparar dois modelos.

    Parâmetros:
    -----------
    errors1 : array-like
        Erros de predição do modelo 1
    errors2 : array-like
        Erros de predição do modelo 2
    h : int
        Horizonte de predição (default=1)

    Retorna:
    --------
    dict : Resultados do teste incluindo estatística DM e p-valor
    """
    # Calcular diferenças de loss
    d = errors1**2 - errors2**2

    # Média das diferenças
    d_mean = np.mean(d)

    # Variância das diferenças (com correção para autocorrelação)
    n = len(d)

    # Autocovariância
    def autocovariance(x, lag):
        n = len(x)
        if lag >= n:
            return 0
        x_centered = x - np.mean(x)
        if lag == 0:
            return np.sum(x_centered * x_centered) / n
        return np.sum(x_centered[:-lag] * x_centered[lag:]) / n

    # Variância de longo prazo (Newey-West)
    gamma_0 = autocovariance(d, 0)
    gamma_sum = 0

    # Usar lag máximo baseado no tamanho da amostra
    max_lag = min(int(4 * (n / 100) ** (2 / 9)), n - 1)

    for lag in range(1, max_lag + 1):
        gamma_lag = autocovariance(d, lag)
        weight = 1 - lag / (max_lag + 1)  # Kernel de Bartlett
        gamma_sum += 2 * weight * gamma_lag

    long_run_variance = gamma_0 + gamma_sum

    # Estatística DM
    if long_run_variance <= 0:
        # Fallback para variância simples se a estimativa for inválida
        long_run_variance = np.var(d, ddof=1)

    dm_stat = d_mean / np.sqrt(long_run_variance / n)

    # P-valor (teste bilateral)
    p_value = 2 * (1 - stats.norm.cdf(abs(dm_stat)))

    return {
        "dm_statistic": dm_stat,
        "p_value": p_value,
        "mean_difference": d_mean,
        "long_run_variance": long_run_variance,
        "significant_5pct": p_value < 0.05,
        "significant_1pct": p_value < 0.01,
    }


def perform_cross_validation_with_errors(X, y, models, cv_splits=5):
    """
    Realiza validação cruzada e coleta erros para teste Diebold-Mariano.

    Parâmetros:
    -----------
    X : DataFrame
        Features
    y : Series
        Target
    models : dict
        Dicionário com modelos
    cv_splits : int
        Número de splits para validação cruzada

    Retorna:
    --------
    dict : Erros de predição para cada modelo
    """
    # Configurar validação cruzada temporal
    tscv = TimeSeriesSplit(n_splits=cv_splits)

    # Armazenar erros
    model_errors = {name: [] for name in models}
    model_predictions = {name: [] for name in models}
    true_values = []

    print(f"Realizando validação cruzada com {cv_splits} folds...")

    for fold, (train_idx, test_idx) in enumerate(tscv.split(X)):
        print(f"  Processando fold {fold + 1}/{cv_splits}...")

        # Split dos dados
        X_train, X_test = X.iloc[train_idx], X.iloc[test_idx]
        y_train, y_test = y.iloc[train_idx], y.iloc[test_idx]

        # Normalização
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)

        # Treinar e avaliar cada modelo
        for name, model in models.items():
            try:
                # Treinar modelo
                model_copy = type(model)(**model.get_params())
                model_copy.fit(X_train_scaled, y_train)

                # Predições
                y_pred = model_copy.predict(X_test_scaled)

                # Calcular erros (residuos)
                errors = y_test.values - y_pred
                model_errors[name].extend(errors)
                model_predictions[name].extend(y_pred)

            except Exception as e:
                print(f"    Erro no modelo {name}: {e}")
                # Preencher com NaN em caso de erro
                model_errors[name].extend([np.nan] * len(y_test))
                model_predictions[name].extend([np.nan] * len(y_test))

        # Armazenar valores verdadeiros
        true_values.extend(y_test.values)

    # Converter para arrays numpy
    for name in model_errors:
        model_errors[name] = np.array(model_errors[name])
        model_predictions[name] = np.array(model_predictions[name])

    true_values = np.array(true_values)

    return model_errors, model_predictions, true_values


def run_diebold_mariano_analysis(data_path):
    """
    Executa análise completa com teste Diebold-Mariano.

    Parâmetros:
    -----------
    data_path : str
        Caminho para o arquivo de dados
    """
    print("=" * 60)
    print("ANÁLISE DIEBOLD-MARIANO PARA COMPARAÇÃO DE MODELOS")
    print("=" * 60)

    # Carregar dados
    try:
        df = pd.read_csv(data_path)
        print(f"Dados carregados: {len(df)} registros")
    except FileNotFoundError:
        print(f"Erro: Arquivo {data_path} não encontrado.")
        return None

    # Preparar dados
    feature_cols = [
        "pib",
        "area_desmatada_ha",
        "idhm_",
        "idhm_renda",
        "idhm_educação",
        "idhm_longevidade",
    ]
    target_col = "GEE_tCO2e"

    # Filtrar colunas disponíveis
    available_cols = [col for col in feature_cols if col in df.columns]
    print(f"Features disponíveis: {available_cols}")

    # Preparar dados para modelagem
    Xy = df.dropna(subset=available_cols + [target_col])
    Xy = Xy.sort_values("ano").reset_index(drop=True)

    X = Xy[available_cols]
    y = Xy[target_col]

    print(f"Dados para modelagem: {len(Xy)} registros")
    print(f"Período: {Xy['ano'].min()} - {Xy['ano'].max()}")

    # Definir modelos
    models = {
        "Linear Regression": LinearRegression(),
        "Random Forest": RandomForestRegressor(
            n_estimators=100, max_depth=10, min_samples_split=5, min_samples_leaf=2, random_state=42
        ),
        "KNN": KNeighborsRegressor(n_neighbors=5),
        "Decision Tree": DecisionTreeRegressor(
            max_depth=8, min_samples_split=10, min_samples_leaf=5, random_state=42
        ),
        "MLP": MLPRegressor(hidden_layer_sizes=(50,), max_iter=1000, alpha=0.01, random_state=42),
        "Lasso": Lasso(alpha=1.0, random_state=42),
        "SVR": SVR(kernel="rbf", C=1.0, gamma="scale"),
        "Dummy": DummyRegressor(strategy="mean"),
    }

    # Realizar validação cruzada
    model_errors, model_predictions, true_values = perform_cross_validation_with_errors(
        X, y, models, cv_splits=5
    )

    print("\n" + "=" * 60)
    print("RESULTADOS DO TESTE DIEBOLD-MARIANO")
    print("=" * 60)

    # Calcular MSE para cada modelo
    model_mse = {}
    for name in models:
        valid_mask = ~np.isnan(model_errors[name])
        if np.sum(valid_mask) > 0:
            model_mse[name] = np.mean(model_errors[name][valid_mask] ** 2)
        else:
            model_mse[name] = np.inf

    # Ordenar modelos por MSE
    sorted_models = sorted(model_mse.items(), key=lambda x: x[1])

    print("\n📊 PERFORMANCE DOS MODELOS (MSE):")
    for i, (name, mse) in enumerate(sorted_models):
        print(f"  {i + 1:2d}. {name:<15} - MSE: {mse:,.2f}")

    # Realizar testes Diebold-Mariano entre todos os pares
    print("\n🔬 TESTES DIEBOLD-MARIANO (comparações par a par):")
    print("   H0: Modelos têm performance igual")
    print("   H1: Modelos têm performance diferente")
    print()

    dm_results = []
    model_names = list(models.keys())

    for i, model1 in enumerate(model_names):
        for j, model2 in enumerate(model_names):
            if i < j:  # Evitar comparações duplicadas
                # Filtrar valores válidos
                valid_mask = ~(np.isnan(model_errors[model1]) | np.isnan(model_errors[model2]))

                if np.sum(valid_mask) > 10:  # Mínimo de observações
                    errors1 = model_errors[model1][valid_mask]
                    errors2 = model_errors[model2][valid_mask]

                    dm_result = diebold_mariano_test(errors1, errors2)

                    # Determinar qual modelo é melhor
                    mse1 = np.mean(errors1**2)
                    mse2 = np.mean(errors2**2)
                    better_model = model1 if mse1 < mse2 else model2

                    dm_results.append(
                        {
                            "model1": model1,
                            "model2": model2,
                            "better_model": better_model,
                            "dm_statistic": dm_result["dm_statistic"],
                            "p_value": dm_result["p_value"],
                            "significant_5pct": dm_result["significant_5pct"],
                            "significant_1pct": dm_result["significant_1pct"],
                            "mse1": mse1,
                            "mse2": mse2,
                        }
                    )

                    # Exibir resultado
                    significance = ""
                    if dm_result["significant_1pct"]:
                        significance = "***"
                    elif dm_result["significant_5pct"]:
                        significance = "**"
                    else:
                        significance = ""

                    print(f"  {model1} vs {model2}:")
                    print(
                        f"    DM = {dm_result['dm_statistic']:6.3f}, "
                        f"p = {dm_result['p_value']:.4f} {significance}"
                    )
                    print(f"    Melhor: {better_model} (MSE: {min(mse1, mse2):,.0f})")
                    print()

    # Resumo das comparações significativas
    significant_comparisons = [r for r in dm_results if r["significant_5pct"]]

    print("\n" + "=" * 60)
    print("RESUMO DAS DIFERENÇAS SIGNIFICATIVAS (α = 0.05)")
    print("=" * 60)

    if significant_comparisons:
        print(f"\n🎯 {len(significant_comparisons)} comparações com diferenças significativas:")

        for result in sorted(significant_comparisons, key=lambda x: x["p_value"]):
            significance_level = "1%" if result["significant_1pct"] else "5%"
            worse_model = (
                result["model2"] if result["better_model"] == result["model1"] else result["model1"]
            )
            print(f"\n  • {result['better_model']} > {worse_model}")
            print(f"    p-valor: {result['p_value']:.4f} (significativo a {significance_level})")
            print(f"    Diferença MSE: {abs(result['mse1'] - result['mse2']):,.0f}")
    else:
        print("\n⚠️  Nenhuma diferença significativa encontrada entre os modelos.")
        print("   Isso pode indicar:")
        print("   - Modelos têm performance similar")
        print("   - Amostra insuficiente para detectar diferenças")
        print("   - Alta variabilidade nos dados")

    # Salvar resultados
    timestamp = pd.Timestamp.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"results/diebold_mariano_results_{timestamp}.csv"

    # Criar DataFrame com resultados
    df_results = pd.DataFrame(dm_results)

    # Criar diretório se não existir
    import os

    os.makedirs("results", exist_ok=True)

    # Salvar resultados
    df_results.to_csv(output_file, index=False)

    print(f"\n💾 Resultados salvos em: {output_file}")

    # Recomendações
    print("\n" + "=" * 60)
    print("RECOMENDAÇÕES PARA O ARTIGO")
    print("=" * 60)

    best_model = sorted_models[0][0]
    print("\n📋 Para reportar no artigo:")
    print(f"   • Melhor modelo: {best_model}")
    print(f"   • MSE: {sorted_models[0][1]:,.2f}")
    print(f"   • Comparações DM realizadas: {len(dm_results)}")
    print(f"   • Diferenças significativas: {len(significant_comparisons)}")

    if significant_comparisons:
        print("\n   📊 Evidência estatística:")
        sig_1pct = len([r for r in significant_comparisons if r["significant_1pct"]])
        sig_5pct = len(
            [
                r
                for r in significant_comparisons
                if r["significant_5pct"] and not r["significant_1pct"]
            ]
        )
        print(f"   • {sig_1pct} diferenças significativas a 1%")
        print(f"   • {sig_5pct} diferenças significativas a 5%")

    print("\n   ✅ Validação metodológica:")
    print("   • Teste Diebold-Mariano implementado")
    print("   • Correção para autocorrelação (Newey-West)")
    print("   • Validação cruzada temporal")

    return df_results


def main():
    """Função principal."""
    data_path = "data/generated/carbono_serra_penitente_com_idhm.csv"

    if not os.path.exists(data_path):
        print(f"Erro: Arquivo {data_path} não encontrado.")
        print("Execute primeiro o script 06_consolidar_dados_carbono_com_idhm.py")
        return

    # Executar análise
    run_diebold_mariano_analysis(data_path)

    print("\n" + "=" * 60)
    print("✅ ANÁLISE DIEBOLD-MARIANO CONCLUÍDA")
    print("=" * 60)


if __name__ == "__main__":
    main()
