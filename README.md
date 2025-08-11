# Projeto Serra do Penitente + MapBiomas API Server

## Visão Geral

Este repositório contém dois projetos integrados para análise de dados ambientais e econômicos:

1. **Serra Penitente Analysis** - Pipeline de análise de carbono e desmatamento
2. **MapBiomas Alert API Server** - Servidor local para API do MapBiomas Alert

## Estrutura do Projeto

```
trabalho_Felipe_CO2/
├── 📁 serra-penitente-analysis/     # Projeto de análise principal
│   ├── 📁 src/                      # Scripts numerados (01-10)
│   ├── 📁 data/                     # Dados brutos e processados
│   ├── 📁 tests/                    # Testes unitários
│   └── 📄 README.md                 # Documentação específica
├── 📁 mapbiomas-alert-api/          # Servidor local MapBiomas
│   ├── 📁 src/                      # Código do servidor FastAPI
│   ├── 📄 run_server.py             # Script para iniciar servidor
│   └── 📄 README.md                 # Documentação da API
├── 📁 results/                      # Resultados gerados (CSV, figuras)
├── 📁 resultados_fixos/             # Relatórios finais
├── 📄 requirements.txt              # Dependências unificadas
├── 📄 quick_setup.py                # Configuração completa automática
├── 📄 setup_environment.py          # Configuração passo a passo
├── 📄 start_mapbiomas_server.py     # Gerenciador do servidor
├── 📄 run_serra_penitente_analysis.py # Executor completo da análise
└── 📄 .env.example                  # Modelo de configuração
```

## 🚀 Início Rápido

### Configuração Automática (Recomendado)

```bash
# 1. Clone o repositório
git clone <url-do-repositorio>
cd trabalho_Felipe_CO2

# 2. Configure todo o ambiente de uma vez
python quick_setup.py

# 3. Execute a análise completa
python run_serra_penitente_analysis.py
```

### Configuração Passo a Passo

```bash
# 1. Configure o ambiente
python setup_environment.py

# 2. Inicie o servidor MapBiomas API
python start_mapbiomas_server.py

# 3. Execute a análise (em outro terminal)
cd serra-penitente-analysis
python run_pipeline_validation.py
```

### Configuração Manual

```bash
# 1. Criar ambiente virtual
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate

# 2. Instalar dependências
pip install -r requirements.txt

# 3. Criar diretórios
mkdir results results\figures results\figuras_consolidadas

# 4. Configurar ambiente
copy .env.example .env
# Edite o arquivo .env com suas credenciais
```

## 🖥️ Uso Diário

### Execução Completa (Recomendado)

```bash
# Executa análise completa com verificações automáticas
python run_serra_penitente_analysis.py

# Ou pular verificação do servidor MapBiomas
python run_serra_penitente_analysis.py --skip-server-check
```

### Execução Manual

```bash
# 1. Iniciar servidor em terminal separado
python start_mapbiomas_server.py

# Verificar se está funcionando
# Acesse: http://localhost:8000/health
# Documentação: http://localhost:8000/docs

# 2. Executar análise (em outro terminal)
cd serra-penitente-analysis

# Executar pipeline completo
python run_pipeline_validation.py

# Ou executar scripts individuais
python src/01_extrair_pib_municipal.py
python src/02_extrair_cobertura_municipal.py
# ... etc
```

### 3. Parar Servidor

```bash
# Parar servidor MapBiomas
python start_mapbiomas_server.py --stop
```

## 📊 Componentes

### Serra Penitente Analysis

**Funcionalidades:**
- Extração de dados de PIB municipal (IBGE)
- Processamento de dados de cobertura do solo (MapBiomas)
- Análise de alertas de desmatamento (INPE/MapBiomas)
- Modelagem preditiva com 9 algoritmos de ML
- Análise de causalidade temporal
- Visualizações científicas (PNG/PDF)
- Integração com dados socioeconômicos (IDHM)

**Scripts Principais:**
- `01_extrair_pib_municipal.py` - Extração PIB municipal
- `02_extrair_cobertura_municipal.py` - Dados MapBiomas
- `03_extrair_alertas_desmatamento.py` - Alertas INPE
- `04_extrair_uso_terra_timeseries.py` - Séries temporais
- `05_consolidar_dados_carbono.py` - Consolidação
- `06_consolidar_dados_carbono_com_idhm.py` - Integração IDHM
- `07_gerar_figuras_carbono.py` - Visualizações
- `08_gerar_figuras_consolidadas.py` - Figuras finais
- `09_gerar_visualizacoes_idhm_desmatamento.py` - Análise IDHM
- `10_analisar_politicas_por_estratos_idhm.py` - Políticas públicas

### MapBiomas Alert API Server

**Funcionalidades:**
- Wrapper RESTful para API GraphQL do MapBiomas
- Autenticação automática
- Cache de requisições
- Documentação interativa (Swagger)
- Endpoints para alertas, territórios e relatórios

**Endpoints Principais:**
- `GET /health` - Status do servidor
- `POST /token` - Autenticação
- `GET /alerts` - Listar alertas
- `GET /alert/{alertCode}` - Detalhes do alerta
- `GET /territories/options` - Opções de territórios

## 🔧 Pré-requisitos

- **Python 3.10+**
- **Conta MapBiomas Alert** (https://alerta.mapbiomas.org/)
- **Conexão com internet** (para APIs externas)
- **8GB RAM** (recomendado para processamento)
- **2GB espaço livre** (para dados e resultados)

## ⚙️ Configuração

### Variáveis de Ambiente (.env)

```env
# Credenciais MapBiomas Alert
MAPBIOMAS_EMAIL=seu_email@exemplo.com
MAPBIOMAS_PASSWORD=sua_senha_aqui

# Configurações do Pipeline
LOG_LEVEL=INFO
DATA_DIR=serra-penitente-analysis/data
RESULTS_DIR=results

# Configurações de API
API_TIMEOUT=30
MAX_RETRIES=3
NUM_THREADS=4

# Desenvolvimento
DEBUG_MODE=false
```

### Dados Necessários

Coloque os seguintes arquivos em `serra-penitente-analysis/data/raw/`:

- `pib_municipios_ibge_2002_2009.xls`
- `pib_municipios_ibge_2010_2021.xlsx`
- `cobertura_solo_mapbiomas_municipios_brasil.xlsx`
- `precos_carbono_eu_ets.xlsx`
- `idhm_municipios_serra_penitente.xlsx`

## 🧪 Testes

```bash
# Executar todos os testes
pytest serra-penitente-analysis/tests/

# Testes específicos
pytest serra-penitente-analysis/tests/test_funcoes_criticas.py

# Com cobertura
pytest --cov=serra-penitente-analysis/src serra-penitente-analysis/tests/

# Testes do servidor MapBiomas
pytest mapbiomas-alert-api/tests/
```

## 📈 Resultados

### Estrutura de Saída

```
results/
├── 📊 *.csv                        # Dados processados
├── 📁 figures/                      # Figuras PNG
│   ├── Figura01_Evolucao_PIB.png
│   ├── Figura03_Evolucao_GEE.png
│   └── ...
└── 📁 figuras_consolidadas/         # Figuras PDF
    ├── Figura01_Paineis_GEE_PIB.pdf
    └── ...

resultados_fixos/
├── 📄 relatorio_academico_precos_carbono.txt
├── 📄 relatorio_analise_estratos_desenvolvimento.txt
├── 📄 relatorio_impacto_idhm.txt
└── 📄 relatorio_precos_carbono_detalhado.txt
```

### Principais Outputs

- **Modelos ML:** Métricas de 9 algoritmos (R², MSE, MAE)
- **Causalidade:** Testes de Granger entre variáveis
- **Visualizações:** 14+ figuras científicas
- **Relatórios:** Análises textuais detalhadas
- **Dados:** CSVs consolidados para uso posterior

## 🔍 Monitoramento

### Logs

```bash
# Ver logs do servidor MapBiomas
tail -f logs/mapbiomas_server.log

# Ver logs da análise
tail -f logs/serra_penitente.log
```

### Status do Sistema

```bash
# Verificar servidor
curl http://localhost:8000/health

# Verificar processos
ps aux | grep python

# Verificar portas
netstat -an | grep 8000
```

## 🚨 Solução de Problemas

### Problemas Comuns

**Configuração Inicial:**
```bash
# Reconfigure tudo automaticamente
python quick_setup.py --force
```

**Servidor não inicia:**
```bash
# Verificar se a porta está ocupada
netstat -an | grep 8000

# Parar processos conflitantes
python start_mapbiomas_server.py --stop

# Ou execute análise sem verificação
python run_serra_penitente_analysis.py --skip-server-check
```

**Erro de dependências:**
```bash
# Reinstalar dependências
pip install --upgrade -r requirements.txt

# Ou reinstale forçando
python quick_setup.py --force

# Verificar versão Python
python --version
```

**Dados não encontrados:**
```bash
# Verificar estrutura de pastas
ls -la serra-penitente-analysis/data/raw/

# Recriar diretórios
python setup_environment.py
```

**Credenciais inválidas:**
```bash
# Verificar arquivo .env
cat .env

# Testar credenciais manualmente
curl -X POST http://localhost:8000/token \
  -H "Content-Type: application/json" \
  -d '{"email":"seu_email","password":"sua_senha"}'
```

### Comandos de Diagnóstico

```bash
# Verificar estrutura do projeto
python quick_setup.py --skip-deps

# Testar apenas importações
python -c "import pandas, numpy, matplotlib, sklearn; print('✅ Dependências OK')"

# Verificar servidor MapBiomas
curl http://localhost:8000/health
```

## 🤝 Contribuição

### Padrões de Código

- **Encoding:** UTF-8 em todos os arquivos
- **Formatação:** Black (line-length=100)
- **Linting:** Flake8
- **Testes:** Pytest com cobertura >80%
- **Commits:** Mensagens em português

### Workflow

1. Fork do repositório
2. Criar branch para feature
3. Implementar mudanças
4. Executar testes
5. Submeter Pull Request

### Estrutura de Commits

```
feat: adicionar nova funcionalidade X
fix: corrigir bug na função Y
docs: atualizar documentação Z
test: adicionar testes para W
refactor: melhorar código V
```

## 📄 Licença

Este projeto está sob licença MIT. Veja o arquivo `LICENSE` para detalhes.

## 📞 Suporte

- **Issues:** Use o sistema de issues do GitHub
- **Documentação:** Consulte os READMEs específicos
- **Email:** developer.mario.santos@gmail.com

### 🆘 Comandos de Emergência

Se encontrar problemas:

1. **Primeiro**: Execute `python quick_setup.py --force` para reconfigurar
2. **Verifique**: Os logs em `logs/` para detalhes dos erros
3. **Teste**: Componentes individuais usando os scripts de utilidade
4. **Documente**: Problemas encontrados para melhorias futuras

**Reset Completo:**
```bash
# Reset completo
python quick_setup.py --force

# Análise sem dependências externas
python run_serra_penitente_analysis.py --skip-server-check

# Verificação de saúde do sistema
python -c "import sys; print(f'Python: {sys.version}'); import pandas, numpy; print('✅ Dependências básicas OK')"
```

---

**Desenvolvido por:** Mário Henrique
**Instituição:** Sem Instituição
**Última atualização:** Agosto de 2025
