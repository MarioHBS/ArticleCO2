# Documentação dos Dados

Este diretório contém os datasets utilizados no pipeline de análise de carbono e desmatamento para municípios da região da Serra do Penitente.

## Estrutura de Diretórios

```
data/
├── raw/           # Dados brutos originais
└── generated/     # Dados processados pelo pipeline (criado automaticamente)
```

## Datasets Disponíveis

### 1. PIB Municipal - IBGE

**Arquivos:**
- `pib_municipios_ibge_2002_2009.xls`
- `pib_municipios_ibge_2010_2021.xlsx`

**Origem:** Instituto Brasileiro de Geografia e Estatística (IBGE)
**Fonte:** Sistema de Contas Regionais do Brasil
**URL:** https://www.ibge.gov.br/estatisticas/economicas/contas-nacionais/

**Período de Cobertura:** 2002-2021
**Data de Coleta:** Dezembro 2024
**Última Atualização IBGE:** Dezembro 2023

**Descrição:** Produto Interno Bruto dos municípios brasileiros a preços correntes e constantes.

**Limitações:**
- Dados disponíveis apenas até 2021
- Metodologia de cálculo alterada em 2010 (quebra de série)
- Valores em reais correntes necessitam deflacionamento para análises temporais
- Alguns municípios podem ter dados ausentes em anos específicos

### 2. Cobertura do Solo - MapBiomas

**Arquivo:** `cobertura_solo_mapbiomas_municipios_brasil.xlsx`

**Origem:** Projeto MapBiomas
**Fonte:** Coleção 8.0 - Dados de Cobertura e Uso da Terra
**URL:** https://mapbiomas.org/

**Período de Cobertura:** 1985-2022
**Data de Coleta:** Dezembro 2024
**Versão:** Coleção 8.0 (2023)

**Descrição:** Dados de cobertura e uso da terra por município, derivados de classificação de imagens de satélite Landsat.

**Limitações:**
- Resolução espacial de 30 metros
- Possíveis erros de classificação em áreas de transição
- Dados sujeitos a revisões em novas coleções
- Cobertura de nuvens pode afetar a qualidade em algumas regiões
- Metodologia pode variar entre diferentes versões da coleção

### 3. IDHM Municipal

**Arquivo:** `idhm_municipios_serra_penitente.xlsx`

**Origem:** Programa das Nações Unidas para o Desenvolvimento (PNUD)
**Fonte:** Atlas do Desenvolvimento Humano no Brasil
**URL:** http://www.atlasbrasil.org.br/

**Período de Cobertura:** 1991, 2000, 2010
**Data de Coleta:** Dezembro 2024
**Última Atualização:** 2013 (baseado no Censo 2010)

**Descrição:** Índice de Desenvolvimento Humano Municipal e seus componentes (longevidade, educação, renda) para municípios da região de estudo.

**Limitações:**
- Dados disponíveis apenas para anos censitários
- Metodologia de cálculo específica para o contexto brasileiro
- Não há dados mais recentes que 2010
- Limitado aos municípios da região da Serra do Penitente
- Comparações temporais devem considerar mudanças metodológicas

### 4. Preços de Carbono - EU ETS

**Arquivo:** `precos_carbono_eu_ets.xlsx`

**Origem:** European Energy Exchange (EEX)
**Fonte:** EU Emissions Trading System (EU ETS)
**URL:** https://www.eex.com/

**Período de Cobertura:** 2008-2024
**Data de Coleta:** Dezembro 2024
**Frequência:** Diária

**Descrição:** Preços históricos de créditos de carbono no mercado europeu (EUR/tCO2).

**Limitações:**
- Preços específicos do mercado europeu
- Volatilidade alta influenciada por fatores políticos e econômicos
- Pode não refletir preços de carbono em outros mercados
- Conversão cambial necessária para análises em reais
- Dados sujeitos a revisões e correções

## Considerações Gerais

### Qualidade dos Dados
- Todos os datasets passam por validação automática de schema
- Verificações de integridade são executadas antes do processamento
- Dados ausentes são identificados e tratados conforme metodologia específica

### Atualizações
- Dados brutos devem ser atualizados manualmente conforme disponibilidade das fontes
- Pipeline automatizado processa dados atualizados mantendo consistência
- Verificar periodicamente as fontes oficiais para novas versões

### Uso Responsável
- Citar adequadamente as fontes em publicações
- Respeitar licenças e termos de uso de cada dataset
- Considerar limitações metodológicas nas análises
- Validar resultados com especialistas do domínio

## Contato e Suporte

Para questões sobre os dados ou metodologia:
- Consultar documentação técnica em `resumo_tecnico.md`
- Verificar pipeline de processamento em `resumo_pipeline.md`
- Executar testes de validação com `python run_tests.py`

---

**Última Atualização:** Dezembro 2024
**Versão do Pipeline:** 1.0
**Responsável:** Felipe - Análise de Carbono e Desmatamento