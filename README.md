# Pipeline de Análise de Carbono e Desmatamento - Serra do Penitente

## Descrição

Este projeto implementa um pipeline completo de análise de dados para estudar as relações entre desenvolvimento econômico, desmatamento e preços de carbono na região da Serra do Penitente. O sistema integra dados de múltiplas fontes (IBGE, MapBiomas, INPE, EU-ETS) e utiliza técnicas de machine learning para modelagem preditiva e análise de causalidade.

### Principais Funcionalidades

- **Extração e processamento** de dados de PIB municipal, cobertura do solo, alertas de desmatamento e preços de carbono
- **Consolidação** de datasets heterogêneos em formato padronizado
- **Modelagem preditiva** com 9 algoritmos de machine learning
- **Análise de causalidade** temporal entre variáveis econômicas e ambientais
- **Visualizações** científicas em formatos PNG e PDF vetorial
- **Validação automática** com testes unitários e verificação de integridade
- **Análise socioeconômica** com integração de dados do IDHM

## Instalação

### Pré-requisitos

- Python 3.10 ou superior
- Git
- Acesso à internet para APIs externas

### Configuração do Ambiente

1. **Clone o repositório:**
   ```bash
   git clone <url-do-repositorio>
   cd trabalho_Felipe_CO2
   ```

2. **Crie um ambiente virtual:**
   ```bash
   python -m venv venv
   
   # Windows
   venv\Scripts\activate
   
   # Linux/Mac
   source venv/bin/activate
   ```

3. **Instale as dependências:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure variáveis de ambiente** (opcional, para API MapBiomas):
   ```bash
   # Windows
   set MAPBIOMAS_EMAIL=seu_email@exemplo.com
   set MAPBIOMAS_PASSWORD=sua_senha
   
   # Linux/Mac
   export MAPBIOMAS_EMAIL=seu_email@exemplo.com
   export MAPBIOMAS_PASSWORD=sua_senha
   ```

### Dependências Principais

- **Análise de dados:** pandas, numpy, scipy
- **Machine Learning:** scikit-learn, xgboost
- **Visualização:** matplotlib, seaborn
- **Testes:** pytest, pytest-cov
- **APIs:** requests, openpyxl

## Execução

### Execução Completa do Pipeline

**Opção 1: Script automatizado**
```bash
python run_pipeline_validation.py
```

**Opção 2: Jupyter Notebook (interativo)**
```bash
jupyter notebook run_pipeline_validation.ipynb
```

### Execução de Scripts Individuais

```bash
# Extração de dados
python src/01_extrair_pib_municipal.py
python src/02_extrair_cobertura_municipal.py
python src/03_extrair_alertas_desmatamento.py
python src/04_extrair_uso_terra_timeseries.py

# Consolidação e modelagem
python src/05_consolidar_dados_carbono.py
python src/06_consolidar_dados_carbono_com_idhm.py

# Geração de figuras
python src/07_gerar_figuras_carbono.py
python src/08_gerar_figuras_consolidadas.py

# Análises específicas
python src/09_gerar_visualizacoes_idhm_desmatamento.py
python src/10_analisar_politicas_por_estratos_idhm.py
```

### Execução de Testes

```bash
# Todos os testes
python run_tests.py

# Testes específicos
python run_tests.py --test TestMunicipio
python run_tests.py --verbose

# Com cobertura
pytest tests/ --cov=src --cov-report=html
```

## Estrutura do Projeto

```
trabalho_Felipe_CO2/
├── data/
│   ├── raw/                    # Dados brutos originais
│   ├── generated/              # Dados processados (criado automaticamente)
│   └── README.md              # Documentação dos datasets
├── src/
│   ├── 01_extrair_pib_municipal.py
│   ├── 02_extrair_cobertura_municipal.py
│   ├── 03_extrair_alertas_desmatamento.py
│   ├── 04_extrair_uso_terra_timeseries.py
│   ├── 05_consolidar_dados_carbono.py
│   ├── 06_consolidar_dados_carbono_com_idhm.py
│   ├── 07_gerar_figuras_carbono.py
│   ├── 08_gerar_figuras_consolidadas.py
│   ├── 09_gerar_visualizacoes_idhm_desmatamento.py
│   ├── 10_analisar_politicas_por_estratos_idhm.py
│   ├── comparar_modelos_com_sem_idhm.py
│   ├── validacao.py           # Funções de validação de dados
│   └── variaveis.py           # Constantes e configurações
├── tests/
│   └── test_funcoes_criticas.py
├── results/                    # Resultados e figuras (criado automaticamente)
│   ├── figures/               # Figuras PNG
│   └── figuras_consolidadas/  # Figuras PDF vetoriais
├── requirements.txt
├── run_tests.py
├── run_pipeline_validation.py
├── run_pipeline_validation.ipynb
└── README.md
```

### Arquivos de Saída

**Dados processados (`data/generated/`):**
- `pib_municipal_serra_penitente_ibge.csv`
- `mapbiomas_cobertura_municipal_long.csv`
- `alertas_serra_penitente.csv`
- `uso_terra_serra_penitente_timeseries.csv`
- `carbono_serra_penitente.csv`
- `carbono_serra_penitente_com_idhm.csv`

**Resultados de modelagem (`results/`):**
- `carbon_price_model_all_results.csv`
- `metricas_modelos_com_idhm.csv`
- `feature_importance_*.csv`

**Figuras científicas (`results/figures/` e `results/figuras_consolidadas/`):**
- Evolução temporal de variáveis
- Comparação de modelos de ML
- Matrizes de causalidade e correlação
- Análises de importância de features

## Documentação Técnica

Para informações detalhadas sobre metodologia, implementação e resultados, consulte:

- **[Resumo Técnico](resumo_tecnico.md)**: Metodologia científica, bases de dados, modelagem estatística e análises de causalidade
- **[Pipeline Detalhado](resumo_pipeline.md)**: Documentação completa de cada script, entradas, saídas e melhorias implementadas
- **[Documentação dos Dados](data/README.md)**: Origem, limitações e características dos datasets utilizados

### Principais Melhorias Implementadas

- **Sistema de logging estruturado** com níveis apropriados (INFO, WARNING, ERROR)
- **Testes automatizados** com 12 testes unitários e cobertura de funções críticas
- **Validação robusta de dados** com verificação de schemas e integridade
- **Tratamento de exceções** específico para diferentes tipos de erro
- **Análise socioeconômica** com integração de dados do IDHM
- **Análise de políticas** segmentada por estratos de desenvolvimento

## Referências

### Fontes de Dados

- **IBGE** - Instituto Brasileiro de Geografia e Estatística
  - PIB Municipal: https://www.ibge.gov.br/estatisticas/economicas/contas-nacionais/

- **MapBiomas** - Projeto de Mapeamento Anual do Uso e Cobertura da Terra no Brasil
  - Dados de cobertura: https://mapbiomas.org/
  - API de Alertas: https://alerta.mapbiomas.org/

- **PNUD** - Programa das Nações Unidas para o Desenvolvimento
  - Atlas do Desenvolvimento Humano: http://www.atlasbrasil.org.br/

- **European Energy Exchange (EEX)**
  - Preços de carbono EU ETS: https://www.eex.com/

### Tecnologias Utilizadas

- **Python 3.8+** - Linguagem principal
- **Pandas & NumPy** - Manipulação e análise de dados
- **Scikit-learn** - Machine learning e validação
- **XGBoost** - Algoritmos de gradient boosting
- **Matplotlib & Seaborn** - Visualização científica
- **Statsmodels** - Análises estatísticas e causalidade
- **Pytest** - Framework de testes

### Metodologia Científica

- **Validação temporal:** TimeSeriesSplit com k=10 folds
- **Métricas de avaliação:** MSE (Mean Squared Error) e R²
- **Análise de causalidade:** Teste de Granger com lag máximo de 2
- **Segmentação socioeconômica:** Estratos baseados em IDHM e PIB per capita

## Licença

Este projeto é desenvolvido para fins acadêmicos e de pesquisa. Os dados utilizados estão sujeitos às licenças de suas respectivas fontes:

- Dados do IBGE: Domínio público
- Dados do MapBiomas: Licença Creative Commons
- Dados do PNUD: Uso acadêmico permitido
- Dados do EU ETS: Uso público com atribuição

## Contato e Suporte

**Desenvolvedor:** Felipe  
**Projeto:** Análise de Carbono e Desmatamento - Serra do Penitente  
**Versão:** 1.0  
**Última atualização:** Dezembro 2024

### Como Contribuir

1. Faça um fork do projeto
2. Crie uma branch para sua feature (`git checkout -b feature/nova-funcionalidade`)
3. Execute os testes (`python run_tests.py`)
4. Commit suas mudanças (`git commit -am 'Adiciona nova funcionalidade'`)
5. Push para a branch (`git push origin feature/nova-funcionalidade`)
6. Abra um Pull Request

### Reportar Problemas

- Execute os testes de validação: `python run_tests.py`
- Verifique os logs de execução para identificar erros
- Consulte a documentação técnica em `resumo_tecnico.md`
- Valide a integridade dos dados de entrada

---

**Nota:** Este README fornece uma visão geral do projeto. Para detalhes técnicos específicos, consulte os arquivos de documentação referenciados acima.