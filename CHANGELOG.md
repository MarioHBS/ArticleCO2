# Changelog

Todas as mudanças notáveis neste projeto serão documentadas neste arquivo.

O formato é baseado em [Keep a Changelog](https://keepachangelog.com/pt-BR/1.0.0/),
e este projeto adere ao [Semantic Versioning](https://semver.org/lang/pt-BR/).

## [Não Lançado]

### Adicionado
- Estrutura de monorepo com dois projetos separados
- Scripts de configuração automática (`quick_setup.py`, `setup_environment.py`)
- Script executor completo da análise (`run_serra_penitente_analysis.py`)
- Gerenciador do servidor MapBiomas (`start_mapbiomas_server.py`)
- Script de debug interativo (`debug_interactive.py`)
- Configurações completas do VS Code (tasks, launch, settings, extensions)
- Arquivo de dependências unificado (`requirements.txt`)
- Configuração de ambiente padronizada (`.env.example`)
- Documentação principal do projeto (`README.md`)
- Configurações de teste unificadas (`pyproject.toml`, `pytest.ini`)
- Configurações de formatação de código (`.flake8`, `.editorconfig`)
- Estrutura de diretórios padronizada

### Modificado
- Reorganização da estrutura de pastas para monorepo
- Atualização dos caminhos no `variaveis.py` para estrutura relativa
- Configuração do `.gitignore` para ignorar arquivos gerados
- Padronização das configurações de desenvolvimento

### Corrigido
- Caminhos relativos para compatibilidade com monorepo
- Configurações de ambiente para ambos os projetos
- Estrutura de testes para projetos separados

## [1.0.0] - 2024-01-XX

### Adicionado
- Projeto inicial Serra Penitente Analysis
- Projeto inicial MapBiomas Alert API
- Pipeline de análise de carbono e desmatamento
- API local para dados do MapBiomas
- Scripts numerados de processamento (01-10)
- Sistema de validação de pipeline
- Geração de relatórios e visualizações
- Análise de causalidade de Granger
- Modelagem preditiva com XGBoost
- Processamento de dados geoespaciais

---

## Tipos de Mudanças

- **Adicionado** para novas funcionalidades
- **Modificado** para mudanças em funcionalidades existentes
- **Depreciado** para funcionalidades que serão removidas em breve
- **Removido** para funcionalidades removidas
- **Corrigido** para correções de bugs
- **Segurança** para vulnerabilidades de segurança

## Convenções de Commit

Este projeto segue as convenções:

- `feat:` Nova funcionalidade
- `fix:` Correção de bug
- `docs:` Mudanças na documentação
- `style:` Formatação, ponto e vírgula ausente, etc
- `refactor:` Refatoração de código
- `test:` Adição ou correção de testes
- `chore:` Manutenção geral

## Versionamento

Este projeto usa [Semantic Versioning](https://semver.org/lang/pt-BR/):

- **MAJOR**: Mudanças incompatíveis na API
- **MINOR**: Funcionalidades adicionadas de forma compatível
- **PATCH**: Correções de bugs compatíveis

## Contribuindo

Para contribuir com este projeto:

1. Faça um fork do projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'feat: adiciona AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## Suporte

Para suporte, consulte:

- [README.md](README.md) - Documentação principal
- [Issues](../../issues) - Problemas conhecidos
- [Discussions](../../discussions) - Discussões da comunidade