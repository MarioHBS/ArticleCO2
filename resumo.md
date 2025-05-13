# Resumo Técnico

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
   for train_idx, test_idx in tscv.split(X):
       Xtr, Xte = X.iloc[train_idx], X.iloc[test_idx]
       ytr, yte = y.iloc[train_idx], y.iloc[test_idx]
       scaler = StandardScaler().fit(Xtr)
       Xtr_s, Xte_s = scaler.transform(Xtr), scaler.transform(Xte)
       model.fit(Xtr_s, ytr)
       pred = model.predict(Xte_s)
       mse_fold = ((pred - yte) ** 2).mean()
       ...
   ```

4. **Modelos avaliados:** Regressão Linear, Lasso, KNN, Decision Tree, Random Forest, MLP, SVR, Dummy, XGBoost.

5. **Cálculo do MSE médio:** Média dos 10 valores de EQM (MSE) de cada modelo para comparação.

## 4. Geração de tabelas e figuras

| Elemento     | Como foi gerado / código                                 | Local no artigo  |
| ------------ | -------------------------------------------------------- | ---------------- |
| **Tabela 1** | Contagem de registros e atributos em cada base           | Metodologia, § B |
| **Tabela 2** | `mse_df` com colunas `Model` e `MSE` (média k-fold)      | Resultados, § A  |
| **Tabela 3** | Seleção de atributos (ex.: prob. de inclusão ou RFECV)   | Resultados, § C  |
| **Figura 1** | Painéis GEE (1985-2023) e PIB (2002-2021) com `axvspan`  | Metodologia, § B |
| **Figura 2** | `sns.barplot(data=mse_df, x='Model', y='MSE')`           | Resultados, § A  |
| **Figura 3** | `sns.barplot(x=FEATURE_COLS, y=rf.feature_importances_)` | Resultados, § C  |
| **Figura 4** | `sns.heatmap(corr, annot=True, fmt='.2f')`               | Resultados, § D  |

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

---

**Implementação técnica:**

* Linguagem: Python 3.x
* Bibliotecas: Pandas, NumPy, Scikit‑Learn, Matplotlib, Seaborn
* Saída gráfica: PDF vetorial para LaTeX
* Validação: TimeSeriesSplit k=10

Este fluxo assegura coerência metodológica, qualidade das figuras e robustez nas comparações quantitativas.
