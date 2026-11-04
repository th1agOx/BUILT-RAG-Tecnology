# BUILT-RAG V1

## Sobre
Serviço de entrega sob demanda com precificação personalizada, usando assistentes de IA para automatizar o atendimento. Os assistentes respondem a partir de uma base de conhecimento (vault no Obsidian) usando RAG.

## Instalação
`ash
uv sync
`

## Checks de qualidade
Rodar os seguintes comandos:
- uv run ruff check .
- uv run ruff format --check .
- uv run mypy src
- uv run pytest
- uv run lint-imports

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
- Etapa 5: CI (adiada)
- Etapa 6: Governança (adiada)
- Etapa 7: Documentação e fechamento
