# Linting com Ruff

Este projeto utiliza **Ruff** como ferramenta de linting e formatação de código, substituindo o Flake8 anteriormente usado.

## Sobre o Ruff

Ruff é um linter extremamente rápido para Python, escrito em Rust, que combina funcionalidades de múltiplas ferramentas:

- Flake8 (verificação de estilo)
- isort (organização de imports)
- pyupgrade (modernização de código)
- E muitas outras regras

## Instalação

O Ruff está incluído no `requirements.txt`:

```bash
pip install -r requirements.txt
```

## Uso

### Script de Linting

Use o script `lint.py` para facilitar o uso:

```bash
# Verificar código
python lint.py

# Corrigir problemas automaticamente
python lint.py --fix

# Formatar código
python lint.py --format
```

### Comandos Diretos

```bash
# Verificar código
ruff check src/

# Corrigir problemas automaticamente
ruff check src/ --fix

# Formatar código
ruff format src/
```

## Configuração

A configuração do Ruff está no arquivo `pyproject.toml` na seção `[tool.ruff]`.

### Regras Ignoradas

Para projetos científicos, algumas regras são ignoradas por serem muito restritivas:

- `E501`: Linha muito longa
- `S101`: Uso de assert
- `T201/T203`: Declarações print/pprint
- `PLR0913/PLR0912/PLR0915`: Muitos argumentos/branches/statements
- `BLE001`: Captura de exceção genérica
- `FBT001/FBT002`: Argumentos booleanos
- `PLC0415`: Imports dentro de funções
- `EM101/EM102`: Literais em exceções
- `G004`: F-strings em logging
- E outras específicas para análise de dados

## Migração do Flake8

### Alterações Realizadas

1. **Removido**: Arquivo `.flake8`
2. **Atualizado**: `requirements.txt` (flake8 → ruff)
3. **Adicionado**: Configuração no `pyproject.toml`
4. **Criado**: Script `lint.py` para facilitar o uso

### Benefícios da Migração

- **Performance**: Ruff é 10-100x mais rápido que Flake8
- **Funcionalidades**: Combina múltiplas ferramentas em uma
- **Correção Automática**: Pode corrigir muitos problemas automaticamente
- **Configuração Unificada**: Tudo no `pyproject.toml`

## Integração com IDEs

### VS Code

Instale a extensão "Ruff" e adicione ao `settings.json`:

```json
{
    "[python]": {
        "editor.defaultFormatter": "charliermarsh.ruff",
        "editor.codeActionsOnSave": {
            "source.organizeImports": true,
            "source.fixAll": true
        }
    }
}
```

### PyCharm

Configure Ruff como ferramenta externa ou use plugins disponíveis.

## Comandos Úteis

```bash
# Verificar apenas imports não utilizados
ruff check src/ --select F401

# Verificar apenas variáveis não utilizadas
ruff check src/ --select F841

# Mostrar todas as regras disponíveis
ruff linter

# Explicar uma regra específica
ruff rule E501
```

## Resolução de Problemas

### Erro de Configuração

Se houver erros na configuração do `pyproject.toml`, verifique:
- Sintaxe TOML correta
- Nomes de regras válidos
- Estrutura das seções

### Performance

Para projetos grandes, use:
```bash
# Verificar apenas arquivos modificados
ruff check $(git diff --name-only --diff-filter=AM | grep '\.py$')
```

## Recursos Adicionais

- [Documentação Oficial do Ruff](https://docs.astral.sh/ruff/)
- [Lista Completa de Regras](https://docs.astral.sh/ruff/rules/)
- [Guia de Migração](https://docs.astral.sh/ruff/faq/#how-does-ruff-compare-to-flake8)
