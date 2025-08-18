#!/usr/bin/env python3
"""Script para verificar os resultados dos modelos."""

import pandas as pd


def check_model_results():
    """Verifica os resultados dos modelos."""
    print("=== RESULTADOS DOS MODELOS ===")

    # Carregar resultados
    df = pd.read_csv("results/metricas_modelos_com_idhm.csv")

    print("\nResultados completos:")
    print(df.round(4))

    print("\nMelhores modelos por CV R²:")
    df_sorted = df.sort_values("cv_r2_mean", ascending=False)
    print(df_sorted[["modelo", "cv_r2_mean", "cv_r2_std", "test_r2"]].round(4))

    print("\nModelos com overfitting (CV R² > 0.99):")
    overfitting = df[df["cv_r2_mean"] > 0.99]
    if overfitting.empty:
        print("✅ Nenhum modelo com overfitting detectado!")
    else:
        print(overfitting[["modelo", "cv_r2_mean", "test_r2"]])

    print("\nModelos com performance razoável (CV R² > 0.5):")
    good_models = df[df["cv_r2_mean"] > 0.5]
    if good_models.empty:
        print("❌ Nenhum modelo com performance razoável")
    else:
        print(good_models[["modelo", "cv_r2_mean", "test_r2"]].round(4))

    print("\n=== ANÁLISE CONCLUÍDA ===")


if __name__ == "__main__":
    check_model_results()
