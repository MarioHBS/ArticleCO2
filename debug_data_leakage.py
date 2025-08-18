#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Script para auditar data leakage nos dados consolidados."""

import pandas as pd
import os

def audit_data_leakage():
    """Audita possível data leakage nos dados consolidados."""
    print("=== AUDITORIA DE DATA LEAKAGE ===")
    
    # Verificar dados consolidados
    carbono_file = 'data/generated/carbono_serra_penitente.csv'
    if os.path.exists(carbono_file):
        print(f"\n1. Analisando {carbono_file}")
        df = pd.read_csv(carbono_file)
        print(f"Shape: {df.shape}")
        print(f"Columns: {df.columns.tolist()}")
        print(f"Sample data:")
        print(df.head())
        
        if 'ano' in df.columns:
            print(f"\nUnique years: {sorted(df['ano'].unique())}")
        
        if 'carbon_price_usd' in df.columns:
            print(f"\nCarbon price stats:")
            print(df['carbon_price_usd'].describe())
            
            # Verificar se há variação nos preços
            unique_prices = df['carbon_price_usd'].nunique()
            print(f"\nUnique carbon prices: {unique_prices}")
            if unique_prices <= 5:
                print("ALERTA: Poucos preços únicos - possível data leakage!")
                print(f"Preços únicos: {sorted(df['carbon_price_usd'].unique())}")
    else:
        print(f"Arquivo {carbono_file} não encontrado")
    
    # Verificar dados com IDHM
    idhm_file = 'data/generated/carbono_serra_penitente_com_idhm.csv'
    if os.path.exists(idhm_file):
        print(f"\n2. Analisando {idhm_file}")
        df_idhm = pd.read_csv(idhm_file)
        print(f"Shape: {df_idhm.shape}")
        print(f"Columns: {df_idhm.columns.tolist()}")
        
        if 'preco_carbono' in df_idhm.columns:
            print(f"\nCarbon price stats (IDHM):")
            print(df_idhm['preco_carbono'].describe())
            
            unique_prices_idhm = df_idhm['preco_carbono'].nunique()
            print(f"\nUnique carbon prices (IDHM): {unique_prices_idhm}")
            if unique_prices_idhm <= 5:
                print("ALERTA: Poucos preços únicos - possível data leakage!")
                print(f"Preços únicos: {sorted(df_idhm['preco_carbono'].unique())}")
    else:
        print(f"Arquivo {idhm_file} não encontrado")
    
    # Verificar resultados de modelos
    results_file = 'results/resultados_modelos_precificacao_carbono.csv'
    if os.path.exists(results_file):
        print(f"\n3. Analisando {results_file}")
        df_results = pd.read_csv(results_file)
        print(f"Shape: {df_results.shape}")
        print(f"Columns: {df_results.columns.tolist()}")
        print(f"\nResultados dos modelos:")
        print(df_results)
        
        # Verificar R² suspeitos
        if 'R2' in df_results.columns:
            suspicious_r2 = df_results[df_results['R2'] >= 0.99]
            if not suspicious_r2.empty:
                print(f"\nALERTA: Modelos com R² >= 0.99 (overfitting suspeito):")
                print(suspicious_r2[['model', 'R2', 'MSE']])
    else:
        print(f"Arquivo {results_file} não encontrado")
    
    print("\n=== FIM DA AUDITORIA ===")

if __name__ == '__main__':
    audit_data_leakage()