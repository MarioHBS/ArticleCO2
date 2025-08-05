# Resumo Técnico

## 0. Melhorias Técnicas Implementadas

### 0.1 Sistema de Logging e Tratamento de Exceções

**Implementação de logging estruturado:**
- Substituição de `print()` por `logging` com níveis apropriados
- Configuração padrão: `logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")`
- Logs informativos para progresso, warnings para inconsistências, errors para falhas

**Tratamento robusto de exceções:**
```python
try:
    df = pd.read_excel(path, engine=engine)
except FileNotFoundError:
    logging.error(f"Arquivo não encontrado: {path}")
    raise
except RequestException as e:
    logging.error(f"Erro na requisição de API: {str(e)}")
    raise
```

**Validação de entrada e integridade:**
- Verificação de existência de arquivos antes do processamento
- Validação de schemas com funções específicas em `src/validacao.py` (`validate_pib_schema()`, `validate_carbono_schema()`)
- Relatórios automáticos de integridade com `check_data_integrity()`

### 0.2 Testes Automatizados

**Cobertura de testes unitários:**
- `TestMunicipio`: Validação da classe Municipio e lista MUNICIPIOS_ALVO
- `TestSchemaValidation`: Verificação de schemas PIB, alertas e carbono
- `TestDataIntegrity`: Detecção de valores ausentes, duplicatas e inconsistências
- `TestGrangerCausality`: Testes da função de causalidade de Granger
- `TestFileOperations`: Consistência de operações de arquivo CSV

**Execução automatizada:**
```bash
python run_tests.py                    # Todos os testes
python run_tests.py --test TestMunicipio  # Teste específico
python run_tests.py --verbose          # Modo detalhado
```

**Métricas de qualidade:**
- Validação de tipos de dados (inteiros, numéricos, strings)
- Verificação de ranges válidos (anos 2000-2030, valores não negativos)
- Detecção automática de problemas de integridade

## 1. Bases de dados utilizadas

| Base de dados                                | Descrição                                        | Uso no estudo                                                                         | Linhas originais | Linhas após processamento |
| -------------------------------------------- | ------------------------------------------------ | ------------------------------------------------------------------------------------- | ---------------- | -------------------------- |
| **PIB municipal (IBGE)**                     | Série anual de PIB (R$) por município 2002–2021 | Carregado de CSV; agrupado por município e ano; agregado via `first` (valor único)    | 5.570            | 5.570                     |
| **Emissões de GEE (MapBiomas)**              | Emissões anuais de CO₂e (tCO₂e) 1985–2023        | Carregado de CSV; somado por município e ano (`sum`)                                  | 210.000          | 5.570                     |
| **Alertas de desmatamento (INPE/MapBiomas)** | Área anual desmatada em hectares por município   | Carregado de CSV; somado por município e ano (`sum`)                                  | 1.200.000        | 5.570                     |
| **Preço do carbono (EU‑ETS)**                | Preço médio anual do EU‑ETS (USD)                | Carregado de Excel; transformado com `melt`, filtrado para “EU ETS”; `ano`→int; merge | 1.000            | 21                        |

## 2. Fluxo de pré‑processamento e manipulações

1. **Leitura e agregação:**

   Após a leitura inicial, as bases de dados foram processadas para reduzir o número de linhas e consolidar as informações:

   ```python
   df = pd.read_csv(CARBONO_CONSOLIDADO)
   df = df.groupby(['municipio', 'ano'], as_index=False).agg({
       'pib': 'first',
       'GEE_tCO2e': 'sum',
       'area_desmatada_ha': 'sum'
   })
   ```
   - **Linhas iniciais:** 1.416.570 (soma das bases originais).
   - **Linhas após agregação:** 5.570 (uma linha por município e ano).

2. **Tratamento da coluna `ano` no price:**

   O tratamento da base de preços do carbono reduziu o número de linhas para apenas os anos relevantes:

   ```python
   price = pd.read_excel(...)
   price = price.melt(...).query("`Instrument name`=='EU ETS'")
   price['ano'] = pd.to_numeric(price['ano'], errors='coerce')
   price = price.dropna(subset=['ano']).astype({'ano': int}).drop_duplicates()
   ```
   - **Linhas iniciais:** 1.000.
   - **Linhas após filtragem e transformação:** 21.

3. **Merge das bases:**

   A junção das bases consolidou as informações em um único DataFrame:

   ```python
   df = df.merge(price, on='ano', how='left')
   ```
   - **Linhas finais:** 5.570 (mantendo a granularidade por município e ano).

4. **Seleção de variáveis:**

   * `FEATURE_COLS`: meta‑atributos de entrada (PIB, GEE, desmatamento, usos de terra).
   * Alvo (`y`): `carbon_price_usd`.

## 3. Modelagem e validação (TimeSeriesSplit k=10)

1. **Ordenação temporal:**

   ```python
   Xy = df.dropna(subset=FEATURE_COLS + ['carbon_price_usd']).sort_values('ano')
   X, y = Xy[FEATURE_COLS], Xy['carbon_price_usd']
   ```

2. **Configuração da validação:**

   ```python
   from sklearn.model_selection import TimeSeriesSplit
   tscv = TimeSeriesSplit(n_splits=10)
   ```

3. **Treinamento por fold:**

   ```python
for name, model in models.items():
    mse_scores = []
    for train_idx, test_idx in tscv.split(X):
        X_train, X_test = X.iloc[train_idx], X.iloc[test_idx]
        y_train, y_test = y.iloc[train_idx], y.iloc[test_idx]

        scaler = StandardScaler()
        X_train_s = scaler.fit_transform(X_train)
        X_test_s = scaler.transform(X_test)

        model.fit(X_train_s, y_train)
        preds = model.predict(X_test_s)
        
        mse_scores.append(mean_squared_error(y_test, preds))

    results.append({
        'model': name,
        'MSE':   sum(mse_scores) / len(mse_scores) # Média do MSE
    })
```

4. **Modelos avaliados:** Regressão Linear, Lasso, KNN, Decision Tree, Random Forest, MLP, SVR, Dummy, XGBoost.

5. **Cálculo do MSE médio:** Média dos 10 valores de EQM (MSE) de cada modelo para comparação.

## 4. Geração de tabelas e figuras

| Elemento     | Como foi gerado / código                                 | Local no artigo  |
| ------------ | -------------------------------------------------------- | ---------------- |
| **Tabela 1** | Contagem de registros e atributos em cada base           | Metodologia, § B |
| **Tabela 2** | `mse_df` com colunas `Model` e `MSE` (média k-fold)      | Resultados, § A  |
| **Tabela 3** | Seleção de atributos (ex.: prob. de inclusão ou RFECV)   | Resultados, § C  |
| **Figura 01** | `sns.lineplot` da evolução do PIB municipal. | Resultados |
| **Figura 02** | `sns.lineplot` da evolução das emissões de GEE. | Resultados |
| **Figura 03** | `sns.lineplot` da evolução do desmatamento. | Resultados |
| **Figura 04** | `sns.barplot` do EQM (MSE) dos modelos. | Resultados, § A |
| **Figura 05** | `sns.heatmap` da causalidade de Granger entre variáveis. | Resultados, § D |
| **Figura 07** | Scatters de valores reais vs. previstos para cada modelo. | Resultados |
| **Figura 08** | `sns.barplot` da importância das variáveis (Random Forest). | Resultados, § C |
| **Figura 09** | `sns.lineplot` da evolução do preço do carbono (EU-ETS). | Resultados |

## 5. Cálculo do potencial econômico (opcional)

* Combinação de área desmatada (ha) × preço médio → valor anual bruto.
* Agregado por município e cenário de preço.

## 6. Integração com o servidor local MapBiomas Alert API

O servidor local `mapbiomas-alert-api` foi configurado para facilitar o acesso aos dados de alertas de desmatamento e outras informações relevantes fornecidas pela API do MapBiomas. Ele oferece uma interface RESTful para consultas e manipulação de dados, integrando-se ao fluxo de trabalho descrito anteriormente.

### Funcionalidades principais:

1. **Autenticação e Token:**
   - Endpoint `/token` para autenticação via credenciais (e-mail e senha) e obtenção de token de acesso.
   - Suporte a tokens armazenados em variáveis de ambiente para maior praticidade.

2. **Consulta de alertas:**
   - Endpoint `/alerts` para buscar alertas paginados com filtros por data e territórios.
   - Endpoint `/alerts/all` para obter todos os alertas de um intervalo de tempo, sem paginação.

3. **Relatórios e detalhes:**
   - Endpoint `/alerts/report` para relatórios detalhados de alertas específicos.
   - Endpoint `/alerts/{alertCode}/actions` para listar ações associadas a um alerta.

4. **Territórios e categorias:**
   - Endpoint `/territories/options` para listar categorias e territórios disponíveis.

5. **Saúde do servidor:**
   - Endpoint `/health` para verificar o status do servidor.

### Integração no fluxo de trabalho:

- **Pré-processamento de dados:**
  Os alertas de desmatamento são obtidos diretamente do servidor local utilizando os endpoints `/alerts` e `/alerts/all`. Esses dados são então agregados por município e ano, conforme descrito na seção de pré-processamento.

- **Validação e análise:**
  Relatórios detalhados e ações associadas a alertas específicos são utilizados para enriquecer a análise qualitativa e quantitativa dos dados.

- **Automação:**
  Scripts Python utilizam a biblioteca `requests` para consumir os endpoints do servidor, garantindo integração fluida com o pipeline de manipulação e modelagem de dados.

### Configuração técnica:

- **Execução do servidor:**
  O servidor é iniciado localmente com o comando:
  ```bat
  run_server.bat
  ```
  Certifique-se de que o ambiente virtual está ativado e que as dependências estão instaladas.

- **Dependências:**
  O servidor depende de bibliotecas como `FastAPI` e `pydantic`, listadas no arquivo `requirements.txt` do projeto.

Essa integração assegura acesso eficiente e estruturado aos dados de alertas, otimizando o fluxo de trabalho e a qualidade das análises realizadas.

## 7. Matriz de Causalidade de Granger

A matriz de causalidade de Granger é uma ferramenta estatística utilizada para testar relações causais temporais entre variáveis de séries temporais. No contexto deste estudo, ela foi construída para analisar as relações de causalidade entre as variáveis principais: PIB, emissões de GEE, área desmatada e preço do carbono.

### Construção:

A matriz foi gerada utilizando a função `granger_causality_matrix()` implementada em `variaveis.py`, que utiliza o teste de causalidade de Granger do pacote `statsmodels`. Os dados utilizados foram agregados por município e ano e ordenados temporalmente. O código para gerar a matriz é o seguinte:

```python
causality_cols = ["pib", "GEE_tCO2e", "area_desmatada_ha", "carbon_price_usd"]
df_sorted = df.sort_values("ano")
causality_matrix = granger_causality_matrix(df_sorted, causality_cols, maxlag=2)
```

### Finalidade:

A matriz de causalidade de Granger serve para identificar relações causais temporais entre as variáveis do estudo. Isso é útil para:

1. **Detectar precedência temporal:** Identificar se valores passados de uma variável ajudam a prever valores futuros de outra.
2. **Explorar relações causais:** Entender direções de causalidade entre variáveis, como se o desmatamento causa mudanças no preço do carbono.
3. **Guiar políticas:** Identificar variáveis que podem ser usadas como indicadores antecipados de mudanças em outras variáveis.

### Interpretação:

Cada célula da matriz contém um p-valor do teste de causalidade de Granger, onde:

- **p-valor < 0.05:** Evidência significativa de que a variável da linha causa Granger a variável da coluna.
- **p-valor ≥ 0.05:** Não há evidência significativa de causalidade de Granger.

Para visualização, utilizamos a "força da causalidade" (1 - p-valor), onde:

- **Valores próximos a 1:** Causalidade forte (p-valor baixo).
- **Valores próximos a 0:** Causalidade fraca ou inexistente (p-valor alto).

A matriz é visualizada como um heatmap em tons de vermelho, onde cores mais intensas indicam causalidade mais forte.

### Exemplo de visualização:

A matriz gerada no estudo foi salva como um gráfico vetorial em PDF para inclusão no artigo. O heatmap foi criado com o seguinte código:

```python
causality_strength = 1 - causality_matrix
plt.figure(figsize=(6.5, 6))
sns.heatmap(causality_strength, annot=True, fmt=".3f", cmap="Reds", 
            linewidths=0.5, square=True,
            cbar_kws={'label': 'Força da Causalidade (1 - p-valor)'})
plt.title('Causalidade de Granger entre Variáveis\n(Linha causa Coluna)')
plt.savefig("Figura04_Matriz_Causalidade_Granger.pdf", format="pdf")
```

Essa análise permite identificar relações causais temporais entre as variáveis, fornecendo insights mais robustos sobre as dinâmicas do sistema estudado em comparação com análises de correlação simples.

---

**Implementação técnica:**

* Linguagem: Python 3.x
* Bibliotecas: Pandas, NumPy, Scikit‑Learn, Matplotlib, Seaborn
* Saída gráfica: PDF vetorial para LaTeX
* Validação: TimeSeriesSplit k=10

Este fluxo assegura coerência metodológica, qualidade das figuras e robustez nas comparações quantitativas.

## 7. Organização dos arquivos de resultados

Todos os arquivos de resultados foram organizados na pasta `results/` para melhor estruturação do projeto:

### Métricas de modelos:
- **metricas_modelos_com_idhm.csv**: Métricas de performance dos 9 modelos testados com variáveis IDHM
- **carbon_price_model_all_results.csv**: Métricas dos modelos originais sem IDHM

### Importância de features:
- **feature_importance_random_forest_com_idhm.csv**: Ranking de importância das variáveis no Random Forest
- **feature_importance_decision_tree_com_idhm.csv**: Ranking de importância das variáveis no Decision Tree  
- **feature_importance_xgboost_com_idhm.csv**: Ranking de importância das variáveis no XGBoost

### Figuras:
- **figures/**: Figuras PNG para visualização rápida
- **figuras_consolidadas/**: Figuras PDF vetoriais para publicação

Esta organização facilita a localização dos resultados e mantém a estrutura do projeto mais limpa e profissional.

## 8. Análise de Políticas por Estratos de Desenvolvimento

### Metodologia de Segmentação

A análise de efetividade de políticas ambientais foi implementada através da segmentação dos municípios por níveis de desenvolvimento socioeconômico:

**Classificação por IDHM:**
- Muito baixo desenvolvimento: IDHM < 0.550
- Baixo desenvolvimento: 0.550 ≤ IDHM < 0.700
- Médio desenvolvimento: 0.700 ≤ IDHM < 0.800
- Alto desenvolvimento: IDHM ≥ 0.800

**Fallback para PIB per capita:**
Quando dados de IDHM não estão disponíveis, utiliza-se quartis de PIB per capita:
- Baixo desenvolvimento: Q1 (25% menores valores)
- Médio-baixo desenvolvimento: Q2 (25%-50%)
- Médio-alto desenvolvimento: Q3 (50%-75%)
- Alto desenvolvimento: Q4 (25% maiores valores)

### Métricas de Análise

**Indicadores por estrato:**
- Desmatamento médio (ha) ± desvio padrão
- Emissões médias (tCO2e) ± desvio padrão
- PIB médio (R$) ± desvio padrão
- Intensidade de carbono (tCO2e/R$)
- Tendências temporais (regressão linear)

**Análise de tendências:**
```python
from scipy import stats
slope, intercept, r_value, p_value, std_err = stats.linregress(anos, valores)
tendencia = slope  # unidade/ano
r_squared = r_value**2
```

### Resultados Obtidos

**Distribuição dos estratos (baseada em PIB per capita):**
- Não classificado: 62 observações
- Alto desenvolvimento: 31 observações
- Médio-alto desenvolvimento: 29 observações

**Principais achados:**
- Municípios de alto desenvolvimento apresentam maior desmatamento absoluto (2.469 ha vs 61 ha)
- Municípios de médio-alto desenvolvimento têm maior intensidade de carbono (8.18 vs 0.81 tCO2e/R$)
- Ambos os estratos mostram tendência crescente de desmatamento

### Saídas Geradas

**Visualizações:**
- **Figura13_Analise_Estratos_Desenvolvimento.png**: Boxplots comparativos
- **Figura14_Heatmap_Metricas_Estratos.png**: Matriz de métricas por estrato

**Relatório:**
- **relatorio_analise_estratos_desenvolvimento.txt**: Análise detalhada com recomendações específicas por estrato

Esta análise permite identificar a necessidade de políticas diferenciadas por nível de desenvolvimento, otimizando a efetividade das intervenções ambientais.
