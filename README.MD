# BUILT-RAG V1

![CI](https://github.com/th1agOx/BUILT-RAG-Tecnology/actions/workflows/ci.yml/badge.svg)

## Sobre
Serviço de entrega sob demanda com precificação personalizada, usando assistentes de IA para automatizar o atendimento. Os assistentes respondem a partir de uma base de conhecimento (vault no Obsidian) usando RAG.

## Instalação
`bash
uv sync
`

## Checks de qualidade
Rodar os seguintes comandos:
- uv run ruff check .
- uv run ruff format --check .
- uv run mypy src
- uv run pytest
- uv run lint-imports

## Como o CI funciona
O CI roda em cada `push` e `pull_request` nos branches `main` e `dev`, com dois jobs:

- **quality**: executa os cinco checks do `AGENTS.md` (`ruff check`, `ruff format --check`, `mypy src`, `pytest`, `lint-imports`) em máquina limpa (`ubuntu-24.04`), usando `uv sync --locked` e a versão do Python definida em `.python-version`.
- **secrets**: varre o histórico do repositório com `gitleaks`, buscando segredos ou chaves expostos.

Para rodar os mesmos checks localmente, use:
```
uv run ruff check .
uv run ruff format --check .
uv run mypy src
uv run pytest
uv run lint-imports
```

## Documentação
- [docs/glossary.md](docs/glossary.md)
- [docs/adr/0001-ddd.md](docs/adr/0001-ddd.md)
- [docs/adr/0002-v1-scope.md](docs/adr/0002-v1-scope.md)
- [docs/adr/0003-v1-architecture.md](docs/adr/0003-v1-architecture.md)
- [docs/sprints/US-00.md](docs/sprints/US-00.md)

## Etapas da Sprint
- Etapa 1: Projeto base
- Etapa 2: Esqueleto
- Etapa 3: Qualidade local
- Etapa 4: Testes de arquitetura
- Etapa 5: CI
- Etapa 6: Governança (sua responsabilidade)
- Etapa 7: Documentação e fechamento
