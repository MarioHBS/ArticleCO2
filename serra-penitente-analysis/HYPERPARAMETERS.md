# Documentação de Hiperparâmetros dos Modelos

Este documento lista todos os hiperparâmetros utilizados nos modelos de aprendizado de máquina para garantir a reprodutibilidade dos resultados.

## Modelos Principais (Scripts 05, 06, 07, 08)

### Random Forest Regressor
- **n_estimators**: 100 (padrão na maioria dos scripts)
- **max_depth**: 10 (script 06), 6 (XGBoost no script 06), sem limite (scripts 05, 07, 08)
- **random_state**: 42 (scripts 05, 06, 07), 0 (script 08)
- **min_samples_split**: 5 (script 06)
- **min_samples_leaf**: 2 (script 06)

### Decision Tree Regressor
- **max_depth**: 8 (script 06), sem limite (scripts 05, 07, 08)
- **random_state**: 42 (scripts 05, 06, 07), 0 (script 08)
- **min_samples_split**: 10 (script 06)
- **min_samples_leaf**: 5 (script 06)

### XGBoost Regressor
- **n_estimators**: 100
- **max_depth**: 6
- **learning_rate**: 0.1
- **subsample**: 0.8 (script 06)
- **colsample_bytree**: 0.8 (script 06)
- **random_state**: 42 (scripts 05, 06, 07), 0 (script 08)

### MLP Regressor (Multi-layer Perceptron)
- **max_iter**: 1000 (scripts 05, 07), 2000 (script 08)
- **random_state**: 42 (scripts 05, 06, 07), 0 (script 08)
- **hidden_layer_sizes**: (100,) (padrão)
- **alpha**: 0.0001 (padrão)

### Lasso Regression
- **alpha**: 0.01 (scripts 05, 07, 08), 1.0 (script 06)
- **random_state**: 42 (scripts 05, 06, 07), 0 (script 08)
- **max_iter**: 1000 (padrão)

### Linear Regression
- **fit_intercept**: True (padrão)
- **normalize**: False (padrão, deprecated)

### K-Nearest Neighbors (KNN)
- **n_neighbors**: 5 (padrão)
- **weights**: 'uniform' (padrão)
- **algorithm**: 'auto' (padrão)

### Support Vector Regressor (SVR)
- **kernel**: 'rbf' (padrão)
- **C**: 1.0 (padrão)
- **gamma**: 'scale' (padrão)

### Dummy Regressor (Baseline)
- **strategy**: 'mean' (padrão)
- **random_state**: 42

## Validação Cruzada

### K-Fold Cross Validation
- **n_splits**: 5 (script 06), 10 (outros scripts)
- **shuffle**: True
- **random_state**: 42

### Time Series Split
- **n_splits**: 5 (implementação temporal melhorada)
- **test_size**: 0.2 (20% para teste)

## Divisão Treino/Teste
- **test_size**: 0.2 (20% para teste)
- **random_state**: 42
- **stratify**: None (dados de regressão)

## Feature Selection

### Variance Threshold
- **threshold**: 0.0 (remove features com variância zero)

### SelectKBest
- **score_func**: f_regression
- **k**: 'all' ou número específico de features

### Recursive Feature Elimination (RFE)
- **estimator**: RandomForestRegressor(n_estimators=50, random_state=42)
- **n_features_to_select**: número específico baseado no dataset

## Escalamento de Features
- **StandardScaler**: fit_transform no treino, transform no teste
- **with_mean**: True (padrão)
- **with_std**: True (padrão)

## Observações Importantes

1. **Inconsistências entre Scripts**: Alguns hiperparâmetros variam entre scripts (ex: random_state=42 vs 0)
2. **Recomendação**: Padronizar random_state=42 em todos os scripts para consistência
3. **Reprodutibilidade**: Todos os random_state estão definidos para garantir resultados reproduzíveis
4. **Otimização**: Os hiperparâmetros não foram otimizados via grid search ou random search

## Scripts Específicos

### Script 05 (consolidar_dados_carbono.py)
- Foco em modelos básicos sem otimização
- Random state consistente = 42

### Script 06 (consolidar_dados_carbono_com_idhm.py)
- Modelos mais otimizados com limitação de profundidade
- Inclui regularização adicional
- Validação cruzada com k=5

### Script 07 (gerar_figuras_carbono.py)
- Configuração similar ao script 05
- Foco na geração de visualizações

### Script 08 (gerar_figuras_consolidadas.py)
- Random state = 0 (diferente dos outros)
- Configuração mais simples para figuras finais

## Recomendações para Melhoria

1. **Padronizar random_state=42** em todos os scripts
2. **Implementar grid search** para otimização de hiperparâmetros
3. **Documentar justificativas** para escolhas específicas de hiperparâmetros
4. **Criar arquivo de configuração** centralizado para hiperparâmetros
5. **Validar sensibilidade** dos resultados a mudanças nos hiperparâmetros