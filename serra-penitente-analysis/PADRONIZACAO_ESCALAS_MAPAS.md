# Padronização de Escalas dos Mapas

Este documento identifica e corrige inconsistências nas escalas dos mapas utilizados no artigo científico.

## Inconsistências Identificadas

### 1. Formatação das Escalas

**Problema**: Diferentes formatos de escala no mesmo documento

- `1:1\,500\,000` (com vírgulas LaTeX)
- `1:4\,000\,000` (com vírgulas LaTeX)
- `1:1 500 000` (com espaços)

**Solução**: Padronizar usando vírgulas LaTeX (`\,`) para separação de milhares

### 2. Escalas Utilizadas por Figura

| Figura | Descrição | Escala Atual | Escala Recomendada | Justificativa |
|--------|-----------|--------------|-------------------|---------------|
| Fig. Municípios Serra do Penitente | Localização municipal | 1:1.500.000 | 1:1.500.000 | ✅ Adequada para visualização municipal |
| Fig. MATOPIBA Localização | Contexto regional | 1:4.000.000 | 1:4.000.000 | ✅ Adequada para contexto regional |
| Fig. Reserva Legal | Áreas de conservação | 1:1 500 000 | 1:1.500.000 | 🔧 Corrigir formatação |
| Fig. Malha Rodoviária | Infraestrutura de transporte | 1:1 500 000 | 1:1.500.000 | 🔧 Corrigir formatação |

## Justificativas para as Escalas

### Escala 1:1.500.000 (Mapas Locais)
- **Uso**: Figuras que mostram detalhes da Serra do Penitente
- **Justificativa**: Permite visualização adequada dos três municípios (Alto Parnaíba, Balsas, Tasso Fragoso) e suas características específicas
- **Aplicação**: Mapas de municípios, reserva legal, infraestrutura rodoviária

### Escala 1:4.000.000 (Mapa Regional)
- **Uso**: Figura de localização do MATOPIBA
- **Justificativa**: Necessária para mostrar o contexto regional do projeto MATOPIBA no Maranhão e a posição da Serra do Penitente
- **Aplicação**: Mapa de contexto regional

## Correções Necessárias

### 1. Padronização da Formatação

**Arquivo**: `main.tex`

**Linhas a corrigir**:
- Linha ~126: `escala 1:1 500 000` → `escala 1:1\,500\,000`
- Linha ~136: `escala 1:1 500 000` → `escala 1:1\,500\,000`

### 2. Verificação de Consistência

**Critérios para escolha de escala**:
1. **Área de cobertura**: Mapas locais (Serra do Penitente) vs. regionais (MATOPIBA)
2. **Nível de detalhe**: Infraestrutura específica vs. contexto geral
3. **Propósito da visualização**: Análise detalhada vs. localização geográfica

## Padrão Recomendado

### Formatação LaTeX
```latex
% Para escalas com milhares
escala 1:1\,500\,000
escala 1:4\,000\,000

% Para escalas sem milhares
escala 1:250\,000
```

### Metadados Cartográficos Padrão
```latex
% Exemplo completo
Projeção Universal Transversa de Mercator (UTM),
Meridiano Central 45° W, Datum SIRGAS 2000 Zona 23 S;
escala 1:1\,500\,000.
Fontes: IBGE (2022) e Embrapa (2015).
```

## Implementação

### Etapa 1: Correção Imediata
- [x] Identificar inconsistências de formatação
- [ ] Corrigir formatação no arquivo `main.tex`
- [ ] Verificar se as escalas são apropriadas para cada mapa

### Etapa 2: Validação
- [ ] Revisar se todas as escalas seguem o padrão LaTeX
- [ ] Confirmar que as escalas são adequadas ao propósito de cada figura
- [ ] Verificar consistência com outros elementos cartográficos

### Etapa 3: Documentação
- [x] Documentar justificativas para cada escala escolhida
- [ ] Criar checklist para futuras figuras cartográficas
- [ ] Estabelecer padrões para novos mapas

## Checklist para Novos Mapas

- [ ] Escala formatada com vírgulas LaTeX (`\,`)
- [ ] Escala apropriada para o nível de detalhe necessário
- [ ] Projeção e datum especificados
- [ ] Fontes dos dados citadas
- [ ] Elaboração cartográfica creditada
- [ ] Consistência com outros mapas do mesmo nível

## Observações Importantes

1. **Escalas Geográficas Distintas**: O artigo trabalha com duas escalas geográficas principais:
   - **Estadual**: Amazônia e Cerrado maranhenses (279 Mt C)
   - **Local**: Serra do Penitente (2,86 MtCO₂e)

2. **Complementaridade**: As diferentes escalas são complementares e atendem a propósitos específicos de análise

3. **Padrão Cartográfico**: Todos os mapas seguem o padrão UTM 23S, SIRGAS-2000, garantindo consistência geodésica

## Resultado Esperado

Após as correções:
- ✅ Formatação consistente de todas as escalas
- ✅ Escalas apropriadas para cada tipo de visualização
- ✅ Justificativas claras para as escolhas de escala
- ✅ Padrão estabelecido para futuras figuras cartográficas
