# Testes de Aceitação do CI — Portões de Qualidade e Segredos

Este documento registra a verificação de que os jobs do CI (`quality` e `secrets`) barram violações conforme esperado, com base nos portões configurados em `.github/workflows/ci.yml` e nas regras de arquitetura R1–R6 (ADR-0003).

## Objetivo

Provar, por meio de execuções controladas em branches de teste, que o CI funciona como portão de qualidade e segurança:

- O job `quality` deve ficar vermelho quando houver violação de regra de importação, erro de formatação ou erro de tipo.
- O job `secrets` deve ficar vermelho quando houver segredo exposto no histórico.
- Nenhuma alteração deve passar sem passar por todos os portões.

## Escopo

Os portões verificados pelo CI são:

| Job | Passo | Comando | O que verifica |
|-----|-------|---------|----------------|
| `quality` | ruff check | `uv run ruff check .` | Lint (regras E, F, I, B, UP, SIM, N, S, C4, PT, RUF, T20) |
| `quality` | ruff format | `uv run ruff format --check .` | Formatação de código |
| `quality` | mypy | `uv run mypy src` | Tipagem estrita (mypy strict) |
| `quality` | pytest | `uv run pytest` | Testes de arquitetura (casos do dono + R2/R3 via AST) |
| `quality` | lint-imports | `uv run lint-imports` (com `PYTHONPATH: src`) | Regras de importação R1–R6 (import-linter) |
| `secrets` | gitleaks | `gitleaks detect --source . --verbose` | Segredos expostos no histórico |

> **Nota:** O passo `lint-imports` requer `PYTHONPATH: src` porque o projeto usa layout `src/` e o import-linter (via grimp) precisa encontrar o pacote `built` para analisar os contratos R1–R6.

## Casos de Teste de Aceitação

| ID | O que foi injetado | Portão esperado | Passo esperado para falha | Resultado esperado | Resultado obtido | Evidência (link da run) |
|----|--------------------|-----------------|---------------------------|--------------------|------------------|-------------------------|
| F1 | `policy/domain` importa `httpx` (viola R2) | `quality` | `lint-imports` / `pytest` | Vermelho | | |
| F2 | Segredo falso e óbvio no histórico | `secrets` | `gitleaks detect` | Vermelho | | |
| F3 | Erro de formatação (ex: linha > 100 colunas) | `quality` | `ruff format --check` | Vermelho | | |
| F4 | Erro de tipo (ex: tipo incompatível) | `quality` | `mypy src` | Vermelho | | |
| C0 | Nenhuma mudança (controle) | Todos | — | Verde | | |

## Regras de Governabilidade

Estas regras aplicam-se à execução dos testes de aceitação e ao uso do CI:

1. **Branches de teste nunca são mescladas.** Qualquer branch criada para validar um caso (F1–F4) deve ser descartada pelo dono após a coleta da evidência.
2. **O dono decide o que apagar.** Nenhum agente ou automação deve apagar branches, PRs ou runs sem autorização explícita do dono.
3. **Dados fictícios apenas.** Nenhum dado real (nome de cliente, CPF, CNPJ, telefone, e-mail, chave de API, token) deve ser usado nos testes. Use dados marcados com a tag `ficticio`.
4. **O CI é portão, não aviso.** Quando o plano e a proteção de branch permitirem, um PR com `quality` vermelho ou `secrets` vermelho não pode ser mesclado.
5. **Rastreabilidade.** Cada caso de teste deve ter sua evidência vinculada (link da execução no GitHub Actions) antes de ser considerado concluído.

## Critério de Sucesso

Um caso de teste é considerado satisfeito quando:

- Para casos F1–F4: o job esperado fica vermelho no passo especificado, e a evidência (link da run) é registrada na tabela acima.
- Para caso C0: ambos os jobs (`quality` e `secrets`) ficam verdes, e a evidência é registrada.

## Como Executar Cada Caso

### F1 — Import proibido (R2)
1. Crie uma branch de teste a partir de `main` ou `dev`.
2. Inje em `src/built/policy/domain/__init__.py`: `import httpx`.
3. Abra um PR.
4. Confirme que o job `quality` fica vermelho no passo `lint-imports` (ou `pytest`, se o teste R2 capturar).
5. Não mescle a branch.

### F2 — Segredo falso
1. Crie uma branch de teste.
2. Adicione um segredo óbvio e fictício (ex: `API_KEY = "sk-1234567890abcdef"` falso) em qualquer arquivo.
3. Abra um PR.
4. Confirme que o job `secrets` fica vermelho.
5. Não mescle a branch.

### F3 — Erro de formatação
1. Crie uma branch de teste.
2. Introduza uma linha com mais de 100 colunas ou sem newline no fim em qualquer `.py`.
3. Abra um PR.
4. Confirme que o job `quality` fica vermelho no passo `ruff format --check`.
5. Não mescle a branch.

### F4 — Erro de tipo
1. Crie uma branch de teste.
2. Introduza um erro de tipagem em `src/` (ex: variável tipada como `str` recebendo `int` sem cast).
3. Abra um PR.
4. Confirme que o job `quality` fica vermelho no passo `mypy src`.
5. Não mescle a branch.

### C0 — Controle (sem mudança)
1. Abra um PR sem alterações de código (ou com alteração apenas de documentação não rastreada por checks).
2. Confirme que `quality` e `secrets` ficam verdes.
3. Não mescle a branch.

## Evidências Pendentes

A coluna "Evidência (link da run)" deve ser preenchida com o link da execução do GitHub Actions para cada caso após a validação manual pelo dono.
