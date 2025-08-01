# Pipeline Detalhado - Processamento de Dados de Carbono

Este documento descreve detalhadamente cada script do pipeline de processamento de dados, incluindo suas funções específicas, entradas, saídas e arquivos gerados.

## Visão Geral do Pipeline

O pipeline é composto por 7 scripts principais (00-06) mais 2 scripts de validação que executam e verificam todo o processo sequencialmente.

## Scripts Principais

### 00_extrair_pib_municipal.py

**Função:** Extrai e processa dados de PIB municipal do IBGE para os três municípios da Serra do Penitente.

**Entradas:**
- `data/raw/pib_municipios_ibge_2002_2009.xls`
- `data/raw/pib_municipios_ibge_2010_2021.xlsx`

**Processamento:**
- Carrega planilhas XLS/XLSX com detecção automática de colunas
- Renomeia colunas dinamicamente baseado nos cabeçalhos reais
- Filtra apenas os municípios definidos em `variaveis.MUNICIPIOS`
- Concatena dados de ambos os períodos (2002-2009 e 2010-2021)
- Padroniza formato: `['codigo_ibge', 'municipio', 'ano', 'pib']`

**Saída:**
- `data/partial/pib_municipal_serra_penitente_ibge.csv`

---

### 01_extrair_cobertura_municipal.py

**Função:** Extrai dados de cobertura do solo por bioma do arquivo MapBiomas e transforma de formato wide para long.

**Entradas:**
- `data/raw/cobertura_solo_mapbiomas_municipios_brasil.xlsx` (planilha COVERAGE_9)

**Processamento:**
- Carrega planilha COVERAGE_9 do arquivo MapBiomas
- Renomeia colunas para padrão do pipeline
- Identifica colunas de anos dinamicamente
- Filtra apenas municípios de Serra do Penitente (códigos: 2100501, 2101400, 2112001)
- Converte colunas de anos para formato numérico
- Transforma dados de wide para long format usando `melt()`

**Saída:**
- `data/partial/mapbiomas_cobertura_municipal_long.csv`

---

### 02_extrair_alertas_desmatamento.py

**Função:** Extrai alertas de desmatamento via API local MapBiomas para os municípios de interesse.

**Entradas:**
- API local MapBiomas (endpoints `/token` e `/alerts/all`)
- Variáveis de ambiente: `MAPBIOMAS_EMAIL` e `MAPBIOMAS_PASSWORD`

**Processamento:**
- Obtém token de autenticação via endpoint `/token`
- Busca todos os alertas para territórios específicos via `/alerts/all`
- Filtra alertas por período (2019-2024)
- Processa dados de localização e área
- Converte coordenadas e calcula áreas em hectares

**Saída:**
- `data/partial/alertas_serra_penitente.csv`

---

### 03_extrair_uso_terra_timeseries.py

**Função:** Processa dados de uso da terra em séries temporais, agregando por município, uso e ano.

**Entradas:**
- `data/raw/cobertura_solo_mapbiomas_municipios_brasil.xlsx` (planilha COVERAGE_9)

**Processamento:**
- Carrega dados de cobertura do MapBiomas
- Renomeia colunas (`geocode` → `codigo_ibge`, `class` → `uso`)
- Transforma de formato wide para long
- Filtra apenas municípios da Serra do Penitente
- Converte áreas de hectares para km²
- Agrega dados por município, uso e ano

**Saída:**
- `data/partial/uso_terra_serra_penitente_timeseries.csv`

---

### 04_consolidar_dados_carbono.py

**Função:** Consolida todos os dados processados, treina modelos de machine learning e gera métricas de avaliação.

**Entradas:**
- `data/partial/pib_municipal_serra_penitente_ibge.csv`
- `data/partial/mapbiomas_cobertura_municipal_long.csv`
- `data/partial/alertas_serra_penitente.csv`
- `data/raw/precos_carbono_eu_ets.xlsx`

**Processamento:**
- Extrai informações de município dos alertas via `crossedCitiesList`
- Agrega dados de PIB, GEE e alertas por município e ano
- Carrega e processa preços de carbono EU-ETS
- Realiza merge de todas as bases de dados
- Treina 9 modelos de machine learning:
  - Linear Regression, Lasso, KNN, Decision Tree
  - Random Forest, MLP, SVR, Dummy, XGBoost
- Avalia modelos usando TimeSeriesSplit (k=10)
- Calcula métricas MSE para cada modelo

**Saídas:**
- `data/generated/carbono_serra_penitente.csv` (dataset consolidado)
- `results/carbon_price_model_all_results.csv` (métricas dos modelos)

---

### 05_gerar_figuras_carbono.py

**Função:** Gera todas as figuras do artigo em formato PNG com nomenclatura numerada.

**Entradas:**
- `data/generated/carbono_serra_penitente.csv`
- `data/raw/precos_carbono_eu_ets.xlsx`
- `results/carbon_price_model_all_results.csv`

**Processamento:**
- Carrega dados consolidados e métricas dos modelos
- Gera figuras de evolução temporal (PIB, GEE, desmatamento)
- Cria gráfico de barras comparando MSE dos modelos
- Gera heatmap de correlação entre variáveis
- Produz scatters de valores reais vs. previstos para cada modelo
- Cria gráfico de importância das variáveis (Random Forest)
- Gera evolução temporal do preço do carbono

**Saídas (results/figures/):**
- `Figura01_Evolucao_PIB.png`
- `Figura02_Evolucao_GEE.png`
- `Figura03_Evolucao_Desmatamento.png`
- `Figura04_EQM_Modelos.png`
- `Figura05_Correlacoes.png`
- `Figura07_1_LinearRegression.png` até `Figura07_9_XGBoost.png`
- `Figura08_Importancia_Variaveis.png`
- `Figura09_Evolucao_Preco_Carbono.png`

---

### 06_gerar_figuras_consolidadas.py

**Função:** Gera figuras finais em formato vetorial PDF para uso em LaTeX.

**Entradas:**
- `data/generated/carbono_serra_penitente.csv`
- `data/raw/precos_carbono_eu_ets.xlsx`

**Processamento:**
- Carrega dados consolidados
- Gera painéis sincronizados de emissões GEE e PIB municipal
- Cria comparação de MSE entre modelos usando TimeSeriesSplit
- Produz gráfico de importância de variáveis
- Gera matriz de correlação em formato vetorial
- Aplica configurações específicas para LaTeX (fontes, tamanhos)

**Saídas (results/figuras_consolidadas/):**
- `Figura01_Paineis_Sincronizados.pdf`
- `Figura02_Comparacao_MSE_Modelos.pdf`
- `Figura03_Importancia_Variaveis.pdf`
- `Figura04_Matriz_Correlacao.pdf`

---

## Scripts de Validação

### run_pipeline_validation.py

**Função:** Script automatizado que executa todo o pipeline sequencialmente e valida as saídas.

**Processamento:**
- Define sequência de execução dos scripts 00-05
- Executa cada script via `subprocess`
- Verifica existência dos arquivos de saída esperados
- Valida figuras geradas usando padrões glob
- Reporta status de sucesso/falha para cada etapa
- Interrompe execução em caso de erro

**Validações:**
- Arquivos CSV em `data/partial/` e `data/generated/`
- Figuras PNG em `results/figures/`
- Métricas de modelos em `results/`

### run_pipeline_validation.ipynb

**Função:** Versão interativa do pipeline de validação em Jupyter Notebook.

**Características:**
- Execução passo-a-passo com documentação
- Visualização de saídas em tempo real
- Facilita depuração e análise intermediária
- Mesma lógica de validação do script Python
- Ideal para desenvolvimento e teste

---

## Estrutura de Arquivos Gerados

### data/partial/
Arquivos intermediários gerados durante o processamento:

- **pib_municipal_serra_penitente_ibge.csv**
  - PIB municipal filtrado para os 3 municípios
  - Colunas: `codigo_ibge`, `municipio`, `ano`, `pib`
  - Período: 2002-2021

- **mapbiomas_cobertura_municipal_long.csv**
  - Dados de cobertura em formato long
  - Colunas: `codigo_ibge`, `municipio`, `bioma`, `classe_*`, `ano`, `area_ha`
  - Período: 1985-2023

- **alertas_serra_penitente.csv**
  - Alertas de desmatamento via API
  - Colunas: `alertCode`, `detectedAt`, `areaHa`, `crossedCitiesList`, etc.
  - Período: 2019-2024

- **uso_terra_serra_penitente_timeseries.csv**
  - Séries temporais de uso da terra
  - Colunas: `codigo_ibge`, `municipio`, `year`, `uso`, `area_ha`, `area_km2`
  - Período: 1985-2023

### data/generated/
Arquivos finais consolidados:

- **carbono_serra_penitente.csv**
  - Dataset final consolidado
  - Colunas: `municipio`, `ano`, `pib`, `GEE_tCO2e`, `area_desmatada_ha`, `carbon_price_usd`
  - Base para modelagem e análises
  - 136 registros (município × ano)

### results/
Resultados de modelagem e figuras:

- **carbon_price_model_all_results.csv**
  - Métricas de avaliação dos 9 modelos
  - Colunas: `Model`, `MSE`
  - Resultados do TimeSeriesSplit k=10

- **figures/** (figuras PNG)
- **figuras_consolidadas/** (figuras PDF vetoriais)

---

## Fluxo de Execução

1. **Extração individual** (scripts 00-03): Processa cada fonte de dados separadamente
2. **Consolidação** (script 04): Une todos os dados e treina modelos
3. **Visualização** (scripts 05-06): Gera figuras em diferentes formatos
4. **Validação** (scripts de validação): Verifica integridade do pipeline

## Dependências

- **Dados externos:** Arquivos Excel/XLS em `data/raw/`
- **API local:** MapBiomas Alert API rodando localmente
- **Configuração:** Variáveis de ambiente para autenticação
- **Bibliotecas:** pandas, scikit-learn, matplotlib, seaborn, xgboost

Este pipeline garante reprodutibilidade, rastreabilidade e validação automática de todo o processo de análise de dados de carbono para a região da Serra do Penitente.