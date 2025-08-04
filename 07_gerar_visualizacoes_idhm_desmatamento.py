#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para gerar visualizações específicas correlacionando IDHM com desmatamento.

Este script cria gráficos que mostram a relação direta entre indicadores
socioeconômicos (IDHM) e área desmatada nos municípios da Serra do Penitente.
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from pathlib import Path
from variaveis import RESULT_PATHS, CARBONO_CONSOLIDADO_COM_IDHM
from scipy.stats import pearsonr, spearmanr

# Configurar estilo
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (10, 6)
plt.rcParams['font.size'] = 10

def carregar_dados_idhm_desmatamento():
    """
    Carrega dados consolidados com IDHM e desmatamento.
    """
    print("Carregando dados consolidados com IDHM...")
    
    if not Path(CARBONO_CONSOLIDADO_COM_IDHM).exists():
        print(f"Erro: Arquivo {CARBONO_CONSOLIDADO_COM_IDHM} não encontrado.")
        return None
    
    df = pd.read_csv(CARBONO_CONSOLIDADO_COM_IDHM, encoding='utf-8-sig')
    print(f"Dados carregados: {df.shape[0]} registros, {df.shape[1]} colunas")
    
    # Filtrar apenas registros com dados válidos
    colunas_idhm = [col for col in df.columns if col.startswith('idhm_')]
    df_valido = df.dropna(subset=['area_desmatada_ha'] + colunas_idhm)
    
    print(f"Registros válidos após filtro: {df_valido.shape[0]}")
    return df_valido

def gerar_scatter_idhm_desmatamento(df):
    """
    Gera scatter plots correlacionando cada indicador IDHM com desmatamento.
    """
    print("Gerando scatter plots IDHM vs Desmatamento...")
    
    # Criar diretório para figuras
    fig_dir = Path("results/figures")
    fig_dir.mkdir(parents=True, exist_ok=True)
    
    # Indicadores IDHM disponíveis
    indicadores_idhm = {
        'idhm_': 'IDHM Geral',
        'idhm_renda': 'IDHM Renda',
        'idhm_educação': 'IDHM Educação',
        'idhm_longevidade': 'IDHM Longevidade'
    }
    
    # Criar subplot para cada indicador
    fig, axes = plt.subplots(2, 2, figsize=(15, 12))
    axes = axes.flatten()
    
    for i, (col, nome) in enumerate(indicadores_idhm.items()):
        if col in df.columns:
            # Filtrar dados válidos para este indicador
            dados_validos = df.dropna(subset=[col, 'area_desmatada_ha'])
            
            if len(dados_validos) > 0:
                # Calcular correlações
                corr_pearson, p_pearson = pearsonr(dados_validos[col], dados_validos['area_desmatada_ha'])
                corr_spearman, p_spearman = spearmanr(dados_validos[col], dados_validos['area_desmatada_ha'])
                
                # Criar scatter plot
                sns.scatterplot(data=dados_validos, x=col, y='area_desmatada_ha', 
                              hue='municipio', s=60, alpha=0.7, ax=axes[i])
                
                # Adicionar linha de tendência (se possível)
                try:
                    if len(dados_validos) > 1 and dados_validos[col].var() > 0:
                        z = np.polyfit(dados_validos[col], dados_validos['area_desmatada_ha'], 1)
                        p = np.poly1d(z)
                        axes[i].plot(dados_validos[col], p(dados_validos[col]), "r--", alpha=0.8)
                except (np.linalg.LinAlgError, ValueError):
                    # Se não conseguir calcular a linha de tendência, continua sem ela
                    pass
                
                # Configurar título e labels
                axes[i].set_title(f'{nome} vs Área Desmatada\n'
                                f'Pearson: {corr_pearson:.3f} (p={p_pearson:.3f})\n'
                                f'Spearman: {corr_spearman:.3f} (p={p_spearman:.3f})')
                axes[i].set_xlabel(nome)
                axes[i].set_ylabel('Área Desmatada (ha)')
                axes[i].legend(title='Município', bbox_to_anchor=(1.05, 1), loc='upper left')
            else:
                axes[i].text(0.5, 0.5, f'Dados não disponíveis\npara {nome}', 
                           ha='center', va='center', transform=axes[i].transAxes)
                axes[i].set_title(nome)
        else:
            axes[i].text(0.5, 0.5, f'Coluna {col}\nnão encontrada', 
                       ha='center', va='center', transform=axes[i].transAxes)
            axes[i].set_title(nome)
    
    plt.tight_layout()
    caminho_scatter = fig_dir / "Figura10_Correlacao_IDHM_Desmatamento.png"
    plt.savefig(caminho_scatter, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Scatter plots salvos em: {caminho_scatter}")

def gerar_evolucao_temporal_idhm_desmatamento(df):
    """
    Gera gráfico de evolução temporal dos indicadores IDHM e desmatamento.
    """
    print("Gerando gráfico de evolução temporal...")
    
    fig_dir = Path("results/figures")
    
    # Agrupar por ano
    df_temporal = df.groupby('ano').agg({
        'area_desmatada_ha': 'sum',
        'idhm_': 'mean',
        'idhm_renda': 'mean',
        'idhm_educação': 'mean',
        'idhm_longevidade': 'mean'
    }).reset_index()
    
    # Criar gráfico com dois eixos Y
    fig, ax1 = plt.subplots(figsize=(12, 6))
    
    # Eixo principal - Desmatamento
    color = 'tab:red'
    ax1.set_xlabel('Ano')
    ax1.set_ylabel('Área Desmatada Total (ha)', color=color)
    line1 = ax1.plot(df_temporal['ano'], df_temporal['area_desmatada_ha'], 
                     color=color, marker='o', linewidth=2, label='Área Desmatada')
    ax1.tick_params(axis='y', labelcolor=color)
    ax1.grid(True, alpha=0.3)
    
    # Eixo secundário - IDHM
    ax2 = ax1.twinx()
    color = 'tab:blue'
    ax2.set_ylabel('IDHM Médio', color=color)
    
    # Plotar indicadores IDHM disponíveis
    cores_idhm = ['tab:blue', 'tab:green', 'tab:orange', 'tab:purple']
    indicadores = ['idhm_', 'idhm_renda', 'idhm_educação', 'idhm_longevidade']
    nomes = ['IDHM Geral', 'IDHM Renda', 'IDHM Educação', 'IDHM Longevidade']
    
    lines2 = []
    for i, (ind, nome, cor) in enumerate(zip(indicadores, nomes, cores_idhm)):
        if ind in df_temporal.columns and not df_temporal[ind].isna().all():
            line = ax2.plot(df_temporal['ano'], df_temporal[ind], 
                          color=cor, marker='s', linewidth=2, linestyle='--', 
                          label=nome, alpha=0.8)
            lines2.extend(line)
    
    ax2.tick_params(axis='y', labelcolor='tab:blue')
    
    # Combinar legendas
    lines = line1 + lines2
    labels = [l.get_label() for l in lines]
    ax1.legend(lines, labels, loc='upper left', bbox_to_anchor=(0, 1))
    
    plt.title('Evolução Temporal: IDHM vs Desmatamento\nSerra do Penitente (2012-2021)')
    plt.tight_layout()
    
    caminho_evolucao = fig_dir / "Figura11_Evolucao_Temporal_IDHM_Desmatamento.png"
    plt.savefig(caminho_evolucao, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Gráfico de evolução temporal salvo em: {caminho_evolucao}")

def gerar_heatmap_correlacao_idhm(df):
    """
    Gera heatmap de correlação entre indicadores IDHM e variáveis ambientais.
    """
    print("Gerando heatmap de correlação...")
    
    fig_dir = Path("results/figures")
    
    # Selecionar variáveis para correlação
    variaveis_interesse = ['area_desmatada_ha', 'GEE_tCO2e', 'pib']
    colunas_idhm = [col for col in df.columns if col.startswith('idhm_')]
    
    # Criar dataset para correlação
    colunas_correlacao = variaveis_interesse + colunas_idhm
    df_corr = df[colunas_correlacao].dropna()
    
    if len(df_corr) > 0:
        # Calcular matriz de correlação
        matriz_corr = df_corr.corr()
        
        # Criar heatmap
        plt.figure(figsize=(10, 8))
        mask = np.triu(np.ones_like(matriz_corr, dtype=bool))
        
        sns.heatmap(matriz_corr, mask=mask, annot=True, cmap='RdBu_r', center=0,
                   square=True, fmt='.3f', cbar_kws={'label': 'Coeficiente de Correlação'})
        
        plt.title('Matriz de Correlação: IDHM vs Variáveis Ambientais\nSerra do Penitente')
        plt.tight_layout()
        
        caminho_heatmap = fig_dir / "Figura12_Heatmap_Correlacao_IDHM.png"
        plt.savefig(caminho_heatmap, dpi=300, bbox_inches='tight')
        plt.close()
        print(f"Heatmap de correlação salvo em: {caminho_heatmap}")
    else:
        print("Dados insuficientes para gerar heatmap de correlação.")

def main():
    """
    Função principal que executa todas as visualizações.
    """
    print("="*60)
    print("GERAÇÃO DE VISUALIZAÇÕES: IDHM vs DESMATAMENTO")
    print("="*60)
    
    # Carregar dados
    df = carregar_dados_idhm_desmatamento()
    
    if df is None:
        print("Erro: Não foi possível carregar os dados.")
        return
    
    # Gerar visualizações
    try:
        gerar_scatter_idhm_desmatamento(df)
        gerar_evolucao_temporal_idhm_desmatamento(df)
        gerar_heatmap_correlacao_idhm(df)
        
        print("\n" + "="*60)
        print("✅ TODAS AS VISUALIZAÇÕES GERADAS COM SUCESSO!")
        print("="*60)
        
        print("\nFiguras geradas:")
        print("- Figura10_Correlacao_IDHM_Desmatamento.png")
        print("- Figura11_Evolucao_Temporal_IDHM_Desmatamento.png")
        print("- Figura12_Heatmap_Correlacao_IDHM.png")
        
    except Exception as e:
        print(f"Erro durante a geração das visualizações: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()