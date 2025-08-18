#!/usr/bin/env python3
"""Script para consolidar dados de PIB, GEE, alertas de desmatamento e IDHM
para predição do preço de carbono na região da Serra do Penitente.

Este script expande o pipeline original incluindo indicadores do IDHM
como features adicionais para melhorar a predição do preço de carbono.
"""

import os
import sys
import warnings

import numpy as np
import pandas as pd
from sklearn.dummy import DummyRegressor
from sklearn.ensemble import RandomForestRegressor
from sklearn.feature_selection import RFE, SelectKBest, VarianceThreshold, f_regression
from sklearn.linear_model import Lasso, LinearRegression
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.model_selection import KFold, cross_val_score, train_test_split
from sklearn.neighbors import KNeighborsRegressor
from sklearn.neural_network import MLPRegressor
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVR
from sklearn.tree import DecisionTreeRegressor
from variaveis import (
    FEATURE_COLS_EXPANDIDO,
    GENERATED_PATHS,
    INPUT_PATHS,
    MUNICIPIOS_ALVO,
    RESULT_PATHS,
)
from xgboost import XGBRegressor

warnings.filterwarnings("ignore")

# Criar pasta results se não existir
os.makedirs("results", exist_ok=True)

# Importar configurações

sys.path.append(os.path.dirname(os.path.abspath(__file__)))


def carregar_dados_idhm():
    """
    Carrega e processa os dados do IDHM.

    Returns:
        pd.DataFrame: DataFrame com dados do IDHM processados
    """
    print("Carregando dados do IDHM...")

    # Carregar arquivo IDHM
    df_idhm = pd.read_excel(INPUT_PATHS.idhm)

    print(f"Shape original do IDHM: {df_idhm.shape}")
    print(f"Colunas disponíveis: {len(df_idhm.columns)}")

    # Identificar coluna de territorialidades (municípios)
    col_municipio = "Territorialidades"

    # Filtrar apenas os municípios de interesse
    # Usar nomes completos com estado como no arquivo
    municipios_completos = ["Alto Parnaíba (MA)", "Balsas (MA)", "Tasso Fragoso (MA)"]
    df_idhm_filtrado = df_idhm[df_idhm[col_municipio].isin(municipios_completos)].copy()

    print(f"Municípios encontrados no IDHM: {df_idhm_filtrado[col_municipio].unique()}")

    # Selecionar indicadores IDHM principais para os anos disponíveis
    # Focar nos indicadores mais relevantes: IDHM geral, Renda, Educação, Longevidade
    indicadores_principais = [
        "IDHM 2010",
        "IDHM Renda 2010",
        "IDHM Educação 2010",
        "IDHM Longevidade 2010",
        "IDHM 2000",
        "IDHM Renda 2000",
        "IDHM Educação 2000",
        "IDHM Longevidade 2000",
    ]

    # Verificar quais indicadores estão disponíveis
    indicadores_disponiveis = [col for col in indicadores_principais if col in df_idhm.columns]
    print(f"Indicadores IDHM disponíveis: {indicadores_disponiveis}")

    # Selecionar colunas relevantes
    colunas_selecionadas = [col_municipio] + indicadores_disponiveis
    df_idhm_selecionado = df_idhm_filtrado[colunas_selecionadas].copy()

    # Converter para formato longo para facilitar merge com outros dados
    dados_processados = []

    for _, row in df_idhm_selecionado.iterrows():
        municipio_nome = row[col_municipio].replace(" (MA)", "")

        # Dados para 2000 - só adicionar se não for NaN
        if not pd.isna(row.get("IDHM 2000")):
            dados_processados.append(
                {
                    "municipio": municipio_nome,
                    "ano": 2000,
                    "idhm_": row.get("IDHM 2000"),
                    "idhm_renda": row.get("IDHM Renda 2000"),
                    "idhm_educação": row.get("IDHM Educação 2000"),
                    "idhm_longevidade": row.get("IDHM Longevidade 2000"),
                }
            )

        # Dados para 2010 - só adicionar se não for NaN
        if not pd.isna(row.get("IDHM 2010")):
            dados_processados.append(
                {
                    "municipio": municipio_nome,
                    "ano": 2010,
                    "idhm_": row.get("IDHM 2010"),
                    "idhm_renda": row.get("IDHM Renda 2010"),
                    "idhm_educação": row.get("IDHM Educação 2010"),
                    "idhm_longevidade": row.get("IDHM Longevidade 2010"),
                }
            )

    df_idhm_processado = pd.DataFrame(dados_processados)

    print(f"Dados IDHM processados: {len(dados_processados)} registros")
    if len(dados_processados) == 0:
        print("ERRO: Nenhum dado IDHM foi processado!")
        return pd.DataFrame()

    # Interpolar valores para anos intermediários (2001-2009)
    df_idhm_expandido = []

    for municipio in df_idhm_processado["municipio"].unique():
        dados_municipio = df_idhm_processado[df_idhm_processado["municipio"] == municipio].copy()
        dados_municipio = dados_municipio.sort_values("ano")

        # Criar série temporal completa de 2000 a 2010
        anos_completos = list(range(2000, 2011))
        dados_municipio_completo = dados_municipio.set_index("ano").reindex(anos_completos)
        dados_municipio_completo["municipio"] = municipio

        # Interpolar valores
        colunas_idhm = ["idhm_", "idhm_renda", "idhm_educação", "idhm_longevidade"]
        for col in colunas_idhm:
            if col in dados_municipio_completo.columns:
                dados_municipio_completo[col] = (
                    dados_municipio_completo[col].interpolate(method="linear").bfill().ffill()
                )

        # Resetar índice e adicionar coluna ano
        dados_municipio_completo = dados_municipio_completo.reset_index()
        dados_municipio_completo = dados_municipio_completo.rename(columns={"index": "ano"})

        df_idhm_expandido.append(dados_municipio_completo)

    # Concatenar todos os dados
    df_idhm_final = pd.concat(df_idhm_expandido, ignore_index=True)

    # Remover registros com todos os valores NaN (exceto municipio e ano)
    colunas_indicadores = [col for col in df_idhm_final.columns if col not in ["municipio", "ano"]]
    df_idhm_final = df_idhm_final.dropna(subset=colunas_indicadores, how="all")

    print(f"Shape final do IDHM processado: {df_idhm_final.shape}")
    print(f"Colunas do IDHM processado: {df_idhm_final.columns.tolist()}")
    print(f"Anos IDHM: {df_idhm_final['ano'].min()} - {df_idhm_final['ano'].max()}")

    return df_idhm_final


def consolidar_dados_com_idhm():
    """
    Consolida dados de PIB, GEE, alertas e IDHM.

    Returns:
        pd.DataFrame: DataFrame consolidado com todas as features
    """
    print("Iniciando consolidação de dados com IDHM...")

    # 1. Carregar dados existentes (PIB, GEE, alertas)
    print("Carregando dados de PIB...")
    try:
        df_pib = pd.read_csv(GENERATED_PATHS.pib_ibge_csv, encoding="utf-8", sep=",")
        print(f"PIB carregado: {df_pib.shape}")
    except Exception as e:
        print(f"Erro ao carregar PIB com utf-8: {e}")
        try:
            df_pib = pd.read_csv(GENERATED_PATHS.pib_ibge_csv, encoding="latin-1", sep=",")
            print(f"PIB carregado com latin-1: {df_pib.shape}")
        except Exception as e2:
            print(f"Erro ao carregar PIB com latin-1: {e2}")
            raise

    # Usar dados consolidados de carbono em vez de mapbiomas
    print("Carregando dados consolidados de carbono...")
    df_carbono = pd.read_csv(GENERATED_PATHS.carbono_consolidado_csv)
    print(f"Dados de carbono carregados: {df_carbono.shape}")

    # Extrair GEE dos dados consolidados
    df_gee = df_carbono[["municipio", "ano", "GEE_tCO2e"]].copy()
    print(f"GEE extraído dos dados consolidados: {df_gee.shape}")

    # Extrair alertas dos dados consolidados
    df_alertas = df_carbono[["municipio", "ano", "area_desmatada_ha"]].copy()
    print(f"Alertas extraídos dos dados consolidados: {df_alertas.shape}")

    # 2. Carregar dados do IDHM
    df_idhm = carregar_dados_idhm()

    # 3. Processar dados existentes
    print("Processando dados do PIB...")
    # O arquivo PIB já tem as colunas corretas
    df_pib = df_pib[df_pib["municipio"].isin([m.nome for m in MUNICIPIOS_ALVO])]
    df_pib = df_pib[["municipio", "ano", "pib"]].copy()

    # Processar GEE
    df_gee = df_gee.rename(columns={"municipality": "municipio", "year": "ano", "sum": "GEE_tCO2e"})
    df_gee = df_gee[["municipio", "ano", "GEE_tCO2e"]]

    # Processar alertas
    df_alertas = df_alertas.rename(
        columns={
            "municipality": "municipio",
            "year": "ano",
            "area_ha": "area_desmatada_ha",
        }
    )
    df_alertas = df_alertas.groupby(["municipio", "ano"])["area_desmatada_ha"].sum().reset_index()

    # 4. Merge dos dados existentes
    print("Fazendo merge dos dados existentes...")
    df_consolidado = df_pib.merge(df_gee, on=["municipio", "ano"], how="outer")
    df_consolidado = df_consolidado.merge(df_alertas, on=["municipio", "ano"], how="outer")

    # 5. Integrar dados do IDHM
    print("Integrando dados do IDHM...")
    if not df_idhm.empty and "municipio" in df_idhm.columns:
        df_consolidado = df_consolidado.merge(df_idhm, on=["municipio", "ano"], how="left")
        print(f"Dados do IDHM integrados. Shape final: {df_consolidado.shape}")
    else:
        print("[AVISO] Dados do IDHM estão vazios ou sem coluna 'municipio'.")
        print("Continuando sem IDHM...")
        # Adicionar colunas IDHM vazias para manter compatibilidade
        for col in FEATURE_COLS_EXPANDIDO:
            if col not in df_consolidado.columns and "idhm" in col:
                df_consolidado[col] = None

    # 6. Filtrar apenas municípios de interesse
    municipios_interesse = [mun.nome for mun in MUNICIPIOS_ALVO]
    df_consolidado = df_consolidado[df_consolidado["municipio"].isin(municipios_interesse)]

    # 7. Preencher valores NaN
    df_consolidado = df_consolidado.fillna(0)

    print(f"Shape final dos dados consolidados: {df_consolidado.shape}")
    print(f"Colunas disponíveis: {df_consolidado.columns.tolist()}")
    print(f"Período coberto: {df_consolidado['ano'].min()} - {df_consolidado['ano'].max()}")

    return df_consolidado


def aplicar_feature_selection(X, y, feature_names, n_features=10):
    """
    Aplica diferentes técnicas de feature selection

    Args:
        X (array): Features
        y (array): Target
        feature_names (list): Nomes das features
        n_features (int): Número de features a selecionar

    Returns:
        dict: Resultados das diferentes técnicas
    """

    print("[FEATURE SELECTION] Aplicando seleção de features...")
    print(f"   - Features originais: {X.shape[1]}")
    print(f"   - Features a selecionar: {n_features}")

    results = {}

    # 1. Variance Threshold - remover features com baixa variância
    print("   1. Variance Threshold:")
    variance_selector = VarianceThreshold(threshold=0.01)
    variance_selector.fit_transform(X)
    variance_features = np.array(feature_names)[variance_selector.get_support()]
    print(f"      Features após variance threshold: {len(variance_features)}")
    results["variance_threshold"] = {
        "features": variance_features.tolist(),
        "n_features": len(variance_features),
    }

    # 2. SelectKBest - seleção univariada
    print("   2. SelectKBest (f_regression):")
    k_best = SelectKBest(score_func=f_regression, k=min(n_features, X.shape[1]))
    k_best.fit_transform(X, y)
    kbest_features = np.array(feature_names)[k_best.get_support()]
    kbest_scores = k_best.scores_[k_best.get_support()]
    print(f"      Features selecionadas: {len(kbest_features)}")
    results["selectkbest"] = {
        "features": kbest_features.tolist(),
        "scores": kbest_scores.tolist(),
        "n_features": len(kbest_features),
    }

    # 3. RFE com Random Forest
    print("   3. Recursive Feature Elimination (RFE):")
    rf_estimator = RandomForestRegressor(n_estimators=50, random_state=42)
    rfe = RFE(estimator=rf_estimator, n_features_to_select=min(n_features, X.shape[1]))
    rfe.fit_transform(X, y)
    rfe_features = np.array(feature_names)[rfe.get_support()]
    rfe_ranking = rfe.ranking_[rfe.get_support()]
    print(f"      Features selecionadas: {len(rfe_features)}")
    results["rfe"] = {
        "features": rfe_features.tolist(),
        "ranking": rfe_ranking.tolist(),
        "n_features": len(rfe_features),
    }

    # 4. Feature Importance com Random Forest
    print("   4. Feature Importance (Random Forest):")
    rf_importance = RandomForestRegressor(n_estimators=100, random_state=42)
    rf_importance.fit(X, y)
    feature_importance = rf_importance.feature_importances_

    # Selecionar top N features por importância
    importance_indices = np.argsort(feature_importance)[::-1][:n_features]
    importance_features = np.array(feature_names)[importance_indices]
    importance_scores = feature_importance[importance_indices]

    print(f"      Features selecionadas: {len(importance_features)}")
    results["feature_importance"] = {
        "features": importance_features.tolist(),
        "scores": importance_scores.tolist(),
        "n_features": len(importance_features),
    }

    # 5. Análise de correlação
    print("   5. Análise de Correlação:")
    df_features = pd.DataFrame(X, columns=feature_names)
    correlation_matrix = df_features.corr().abs()

    # Encontrar features altamente correlacionadas
    high_corr_pairs = []
    for i in range(len(correlation_matrix.columns)):
        for j in range(i + 1, len(correlation_matrix.columns)):
            if correlation_matrix.iloc[i, j] > 0.8:
                high_corr_pairs.append(
                    (
                        correlation_matrix.columns[i],
                        correlation_matrix.columns[j],
                        correlation_matrix.iloc[i, j],
                    )
                )

    print(f"      Pares altamente correlacionados (>0.8): {len(high_corr_pairs)}")
    results["correlation"] = {
        "high_corr_pairs": high_corr_pairs,
        "n_pairs": len(high_corr_pairs),
    }

    # 6. Consenso entre métodos
    print("   6. Consenso entre Métodos:")
    all_selected = set()
    for method in ["selectkbest", "rfe", "feature_importance"]:
        all_selected.update(results[method]["features"])

    # Contar quantas vezes cada feature foi selecionada
    feature_votes = {}
    for feature in all_selected:
        votes = 0
        for method in ["selectkbest", "rfe", "feature_importance"]:
            if feature in results[method]["features"]:
                votes += 1
        feature_votes[feature] = votes

    # Features com pelo menos 2 votos
    consensus_features = [f for f, v in feature_votes.items() if v >= 2]
    print(f"      Features com consenso (≥2 métodos): {len(consensus_features)}")

    results["consensus"] = {
        "features": consensus_features,
        "votes": feature_votes,
        "n_features": len(consensus_features),
    }

    print("[FEATURE SELECTION] Análise concluída!")
    return results


def treinar_modelos_expandidos(df_consolidado):
    """
    Treina modelos de predição com features expandidas incluindo IDHM.

    Args:
        df_consolidado (pd.DataFrame): DataFrame com todas as features

    Returns:
        dict: Resultados dos modelos
    """
    print("Iniciando treinamento de modelos com features expandidas...")

    # Carregar preços de carbono
    print("[INFO] Carregando preços de carbono...")
    price_raw = pd.read_excel(
        INPUT_PATHS.precos_carbono,
        sheet_name=0,
        header=1,
        engine="openpyxl",
    )
    instrument_col = "Instrument name"
    # identifica anos nas colunas
    year_cols = [c for c in price_raw.columns if isinstance(c, int)]

    df_precos = price_raw.melt(
        id_vars=[instrument_col],
        value_vars=year_cols,
        var_name="ano",
        value_name="preco_carbono",
    ).query(f"`{instrument_col}` == 'EU ETS'")
    df_precos["ano"] = df_precos["ano"].astype(int)
    df_precos["preco_carbono"] = pd.to_numeric(df_precos["preco_carbono"], errors="coerce")
    df_precos = df_precos[["ano", "preco_carbono"]].dropna().drop_duplicates()

    # Merge com preços de carbono
    df_final = df_consolidado.merge(df_precos, on="ano", how="inner")

    print(f"Dados finais para modelagem: {df_final.shape}")

    # Definir features expandidas
    feature_cols_base = ["pib", "GEE_tCO2e", "area_desmatada_ha"]
    feature_cols_idhm = [col for col in df_final.columns if col.startswith("idhm_")]
    feature_cols_expandidas = feature_cols_base + feature_cols_idhm

    print(f"Features base: {feature_cols_base}")
    print(f"Features IDHM: {feature_cols_idhm}")
    print(f"Features expandidas: {feature_cols_expandidas}")

    # Aplicar feature selection
    X_temp = df_final[feature_cols_expandidas].fillna(0)
    y_temp = df_final["preco_carbono"].fillna(0)

    # Remover linhas com NaN
    mask_temp = ~(X_temp.isna().any(axis=1) | y_temp.isna())
    X_temp = X_temp[mask_temp]
    y_temp = y_temp[mask_temp]

    if X_temp.shape[0] > 0:
        # Aplicar feature selection
        n_features_to_select = min(8, len(feature_cols_expandidas))  # Selecionar até 8 features
        feature_selection_results = aplicar_feature_selection(
            X_temp.values,
            y_temp.values,
            feature_cols_expandidas,
            n_features_to_select,
        )

        # Usar features do consenso, ou SelectKBest se consenso for muito pequeno
        if len(feature_selection_results["consensus"]["features"]) >= 3:
            selected_features = feature_selection_results["consensus"]["features"]
            print(f"[FEATURE SELECTION] Usando features do consenso: {selected_features}")
        else:
            selected_features = feature_selection_results["selectkbest"]["features"]
            print(f"[FEATURE SELECTION] Usando features do SelectKBest: {selected_features}")

        # Atualizar features para usar apenas as selecionadas
        feature_cols_expandidas = selected_features

        # Salvar resultados da feature selection
        import json

        os.makedirs("results", exist_ok=True)
        with open("results/feature_selection_results.json", "w", encoding="utf-8") as f:
            json.dump(feature_selection_results, f, indent=2, ensure_ascii=False)
        print("[FEATURE SELECTION] Resultados salvos em results/feature_selection_results.json")
    else:
        print(
            "[FEATURE SELECTION] Dados insuficientes para feature selection, "
            "usando todas as features"
        )

    # Preparar dados para modelagem
    X = df_final[feature_cols_expandidas]
    y = df_final["preco_carbono"]

    # Remover linhas com NaN
    mask = ~(X.isna().any(axis=1) | y.isna())
    X = X[mask]
    y = y[mask]

    print(f"Dados para treinamento: {X.shape[0]} amostras, {X.shape[1]} features")

    if X.shape[0] == 0:
        print("Erro: Nenhuma amostra válida para treinamento!")
        return {}

    # Split dos dados
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Normalização
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    # Definir modelos com regularização para prevenir overfitting
    modelos = {
        "Linear Regression": LinearRegression(),
        "Random Forest": RandomForestRegressor(
            n_estimators=100,
            max_depth=10,  # Limitar profundidade
            min_samples_split=5,  # Mínimo de amostras para split
            min_samples_leaf=2,  # Mínimo de amostras por folha
            random_state=42,
        ),
        "KNN": KNeighborsRegressor(n_neighbors=5),  # Aumentar K
        "Decision Tree": DecisionTreeRegressor(
            max_depth=8,  # Limitar profundidade
            min_samples_split=10,  # Mínimo de amostras para split
            min_samples_leaf=5,  # Mínimo de amostras por folha
            random_state=42,
        ),
        "MLP Regressor": MLPRegressor(
            hidden_layer_sizes=(50,),  # Reduzir complexidade
            max_iter=1000,
            alpha=0.01,  # Regularização L2
            random_state=42,
        ),
        "Lasso": Lasso(alpha=1.0, random_state=42),  # Aumentar regularização
        "SVR": SVR(kernel="rbf", C=1.0, gamma="scale"),  # Regularização
        "Dummy": DummyRegressor(strategy="mean"),
        "XGBoost": XGBRegressor(
            n_estimators=100,
            max_depth=6,  # Limitar profundidade
            learning_rate=0.1,  # Taxa de aprendizado moderada
            subsample=0.8,  # Subsample para regularização
            colsample_bytree=0.8,  # Feature sampling
            reg_alpha=0.1,  # Regularização L1
            reg_lambda=1.0,  # Regularização L2
            random_state=42,
            verbosity=0,
        ),
    }

    # Configurar validação cruzada temporal adequada
    # Para 20 anos de dados, k=5 resulta em ~4 anos por fold
    kfold = KFold(n_splits=5, shuffle=True, random_state=42)

    # Treinar e avaliar modelos com validação cruzada
    resultados = []

    for nome, modelo in modelos.items():
        print(f"Treinando {nome} com validação cruzada...")

        try:
            # Criar pipeline com ou sem normalização
            if nome in ["Linear Regression", "MLP Regressor", "Lasso", "SVR"]:
                pipeline = Pipeline(
                    [
                        ("scaler", StandardScaler()),
                        ("model", modelo),
                    ]
                )
                X_for_cv = X
            else:
                pipeline = modelo
                X_for_cv = X

            # Validação cruzada para R²
            cv_r2_scores = cross_val_score(pipeline, X_for_cv, y, cv=kfold, scoring="r2")
            cv_mse_scores = cross_val_score(
                pipeline, X_for_cv, y, cv=kfold, scoring="neg_mean_squared_error"
            )

            # Converter MSE negativo para positivo
            cv_mse_scores = -cv_mse_scores

            # Treinar modelo final para test set
            if nome in ["Linear Regression", "MLP Regressor", "Lasso", "SVR"]:
                modelo.fit(X_train_scaled, y_train)
                y_pred = modelo.predict(X_test_scaled)
            else:
                modelo.fit(X_train, y_train)
                y_pred = modelo.predict(X_test)

            # Calcular métricas no test set
            test_r2 = r2_score(y_test, y_pred)
            test_mse = mean_squared_error(y_test, y_pred)

            resultados.append(
                {
                    "modelo": nome,
                    "cv_r2_mean": cv_r2_scores.mean(),
                    "cv_r2_std": cv_r2_scores.std(),
                    "cv_mse_mean": cv_mse_scores.mean(),
                    "cv_mse_std": cv_mse_scores.std(),
                    "test_r2": test_r2,
                    "test_mse": test_mse,
                    "features_utilizadas": len(feature_cols_expandidas),
                    "features_idhm": len(feature_cols_idhm),
                }
            )

            print(f"{nome}:")
            print(f"  CV R² = {cv_r2_scores.mean():.4f} ± {cv_r2_scores.std():.4f}")
            print(f"  CV MSE = {cv_mse_scores.mean():.4f} ± {cv_mse_scores.std():.4f}")
            print(f"  Test R² = {test_r2:.4f}, Test MSE = {test_mse:.4f}")

            # Salvar importância das features para modelos tree-based
            if hasattr(modelo, "feature_importances_"):
                importancias = pd.DataFrame(
                    {
                        "feature": feature_cols_expandidas,
                        "importancia": modelo.feature_importances_,
                    }
                ).sort_values("importancia", ascending=False)

                print(f"\nTop 5 features mais importantes ({nome}):")
                print(importancias.head())

                # Salvar importâncias
                nome_arquivo = nome.lower().replace(" ", "_")
                if nome_arquivo == "random_forest":
                    caminho_arquivo = RESULT_PATHS.feature_importance_rf_csv
                elif nome_arquivo == "decision_tree":
                    caminho_arquivo = RESULT_PATHS.feature_importance_dt_csv
                elif nome_arquivo == "xgboost":
                    caminho_arquivo = RESULT_PATHS.feature_importance_xgb_csv
                else:
                    caminho_arquivo = f"results/feature_importance_{nome_arquivo}_com_idhm.csv"
                importancias.to_csv(caminho_arquivo, index=False)

        except Exception as e:
            print(f"Erro ao treinar {nome}: {e}")
            resultados.append(
                {
                    "modelo": nome,
                    "cv_r2_mean": np.nan,
                    "cv_r2_std": np.nan,
                    "cv_mse_mean": np.nan,
                    "cv_mse_std": np.nan,
                    "test_r2": np.nan,
                    "test_mse": np.nan,
                    "features_utilizadas": len(feature_cols_expandidas),
                    "features_idhm": len(feature_cols_idhm),
                }
            )

    return resultados


def main():
    """
    Função principal do script.
    """
    print("=" * 60)
    print("CONSOLIDAÇÃO DE DADOS COM IDHM PARA PREDIÇÃO DE PREÇO DE CARBONO")
    print("=" * 60)

    try:
        # 1. Consolidar dados
        df_consolidado = consolidar_dados_com_idhm()

        # 2. Salvar dados consolidados
        output_path = GENERATED_PATHS.carbono_consolidado_com_idhm_csv
        df_consolidado.to_csv(output_path, index=False)
        print(f"\nDados consolidados salvos em: {output_path}")

        # 3. Treinar modelos
        resultados = treinar_modelos_expandidos(df_consolidado)

        # 4. Salvar resultados
        if resultados:
            df_resultados = pd.DataFrame(resultados)
            df_resultados.to_csv(RESULT_PATHS.metricas_modelos_com_idhm_csv, index=False)
            print(f"\nMétricas dos modelos salvas em: {RESULT_PATHS.metricas_modelos_com_idhm_csv}")

            # Exibir resumo dos resultados
            print("\n" + "=" * 50)
            print("RESUMO DOS RESULTADOS")
            print("=" * 50)
            print(df_resultados.sort_values("cv_r2_mean", ascending=False))

        print("\n[OK] Pipeline executado com sucesso!")

    except Exception as e:
        print(f"[ERROR] Erro na execução: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
