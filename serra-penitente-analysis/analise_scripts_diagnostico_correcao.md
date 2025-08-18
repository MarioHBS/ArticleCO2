# Análise dos Scripts de Diagnóstico e Correção

## Resumo Executivo

Este documento analisa todos os scripts criados para diagnósticos e correções no projeto Serra Penitente Analysis, fornecendo recomendações sobre quais manter, remover ou reorganizar.

## Scripts Analisados

### 1. Scripts de Diagnóstico (Raiz)

#### 1.1 `analyze_baseline_problem.py`

- **Função**: Análise exploratória dos dados consolidados
- **Status**: ✅ **MANTER**
- **Justificativa**: Script útil para análise ad-hoc dos dados
- **Recomendação**: Mover para pasta `diagnosis/`

#### 1.2 `check_idhm_file.py`

- **Função**: Verificação específica do arquivo IDHM
- **Status**: ❌ **REMOVER**
- **Justificativa**: Funcionalidade já incorporada nos scripts principais
- **Alternativa**: Usar `test_idhm_loading.py` para testes

#### 1.3 `check_results.py`

- **Função**: Verificação dos resultados dos modelos
- **Status**: ✅ **MANTER**
- **Justificativa**: Útil para validação rápida dos resultados
- **Recomendação**: Mover para pasta `diagnosis/`

### 2. Scripts de Correção (Raiz)

#### 2.1 `fix_baseline_problem.py`

- **Função**: Correção do problema de baseline negativo
- **Status**: ❌ **REMOVER**
- **Justificativa**: Correção já aplicada nos scripts principais
- **Observação**: Manter apenas como referência histórica

#### 2.2 `fix_orphan_references.py`

- **Função**: Reativação de referências bibliográficas órfãs
- **Status**: ❌ **REMOVER**
- **Justificativa**: Correção específica já aplicada
- **Observação**: Script pontual, não necessário manter

#### 2.3 `fix_temporal_cross_validation.py`

- **Função**: Correção da validação cruzada temporal
- **Status**: ❌ **REMOVER**
- **Justificativa**: Correção já incorporada nos scripts principais
- **Observação**: Lógica migrada para scripts de modelagem

#### 2.4 `fix_unit_inconsistencies.py`

- **Função**: Correção de inconsistências de unidades
- **Status**: ❌ **REMOVER**
- **Justificativa**: Correção específica já aplicada
- **Observação**: Script pontual, não necessário manter

### 3. Scripts de Teste (Raiz)

#### 3.1 `test_corrected_modeling.py`

- **Função**: Teste da modelagem com dados corrigidos
- **Status**: ❌ **REMOVER**
- **Justificativa**: Funcionalidade coberta pelos testes unitários
- **Alternativa**: Usar `tests/test_funcoes_criticas.py`

#### 3.2 `test_idhm_loading.py`

- **Função**: Teste específico do carregamento IDHM
- **Status**: ✅ **MANTER**
- **Justificativa**: Teste específico útil para debugging
- **Recomendação**: Mover para pasta `tests/`

#### 3.3 `run_tests.py`

- **Função**: Executor de todos os testes unitários
- **Status**: ✅ **MANTER**
- **Justificativa**: Script essencial para execução de testes
- **Recomendação**: Manter na raiz

### 4. Scripts de Implementação (Raiz)

#### 4.1 `implement_diebold_mariano_test.py`

- **Função**: Implementação do teste Diebold-Mariano
- **Status**: ✅ **MANTER**
- **Justificativa**: Análise estatística avançada importante
- **Recomendação**: Mover para pasta `analysis/`

#### 4.2 `implement_feature_selection.py`

- **Função**: Implementação de seleção de features
- **Status**: ❌ **REMOVER**
- **Justificativa**: Funcionalidade já incorporada nos scripts principais
- **Observação**: Lógica migrada para scripts de modelagem

#### 4.3 `standardize_temporal_periods.py`

- **Função**: Padronização de períodos temporais
- **Status**: ❌ **REMOVER**
- **Justificativa**: Correção específica já aplicada
- **Observação**: Script pontual, não necessário manter

### 5. Scripts de Validação

#### 5.1 `validate_final_results.py`

- **Função**: Validação dos resultados finais
- **Status**: ✅ **MANTER**
- **Justificativa**: Script importante para validação final
- **Recomendação**: Manter na raiz

### 6. Pasta `diagnosis/`

#### 6.1 `analisar_idhm.py`

- **Status**: ✅ **MANTER**
- **Justificativa**: Análise específica dos dados IDHM

#### 6.2 `debug_categories.py`

- **Status**: ✅ **MANTER**
- **Justificativa**: Debug da API MapBiomas

#### 6.3 `debug_extrair_alertas.py`

- **Status**: ✅ **MANTER**
- **Justificativa**: Debug específico dos alertas

#### 6.4 `get_municipality_ids.py`

- **Status**: ✅ **MANTER**
- **Justificativa**: Utilitário para obter IDs dos municípios

#### 6.5 `introspect_alert_types.py`

- **Status**: ✅ **MANTER**
- **Justificativa**: Análise dos tipos de alertas

## Estrutura Proposta

```text
serra-penitente-analysis/
├── src/                           # Scripts principais (01-10)
├── tests/                         # Testes unitários
│   ├── test_idhm_loading.py      # Movido da raiz
│   └── ...
├── diagnosis/                     # Scripts de diagnóstico
│   ├── analyze_baseline_problem.py  # Movido da raiz
│   ├── check_results.py            # Movido da raiz
│   ├── analisar_idhm.py
│   ├── debug_categories.py
│   ├── debug_extrair_alertas.py
│   ├── get_municipality_ids.py
│   └── introspect_alert_types.py
├── analysis/                      # Análises avançadas
│   └── implement_diebold_mariano_test.py  # Movido da raiz
├── run_tests.py                   # Executor de testes (raiz)
├── validate_final_results.py      # Validação final (raiz)
└── ...
```

## Scripts a Remover

### Imediatamente

- `check_idhm_file.py` - Funcionalidade duplicada
- `fix_baseline_problem.py` - Correção já aplicada
- `fix_orphan_references.py` - Correção pontual aplicada
- `fix_temporal_cross_validation.py` - Correção já incorporada
- `fix_unit_inconsistencies.py` - Correção pontual aplicada
- `test_corrected_modeling.py` - Coberto pelos testes unitários
- `implement_feature_selection.py` - Funcionalidade incorporada
- `standardize_temporal_periods.py` - Correção pontual aplicada

## Scripts a Mover

### Para `tests/`

- `test_idhm_loading.py`

### Para `diagnosis/`

- `analyze_baseline_problem.py`
- `check_results.py`

### Para `analysis/`

- `implement_diebold_mariano_test.py`

## Scripts a Manter na Raiz

- `run_tests.py` - Executor principal de testes
- `validate_final_results.py` - Validação final do pipeline

## Benefícios da Reorganização

1. **Clareza**: Separação clara entre scripts de produção, testes, diagnóstico e análises
2. **Manutenibilidade**: Redução de scripts obsoletos
3. **Organização**: Estrutura mais limpa e profissional
4. **Eficiência**: Foco nos scripts realmente necessários

## Próximos Passos

1. Criar pasta `analysis/` se não existir
2. Mover scripts conforme recomendações
3. Remover scripts obsoletos
4. Atualizar documentação e imports
5. Testar pipeline após reorganização

---

**Data da Análise**: 2025-01-18
**Responsável**: Sistema de IA - Análise de Código
**Status**: Proposta para Aprovação
