# Relatório de defeito detectado pelo CI: F0, suíte de testes vazia

Registro no formato de QA. Serve de evidência para a reunião de 2026-11-10 e de exemplo de estudo.

## 1. Identificação

| Campo | Valor |
|---|---|
| ID | F0 |
| Título | O job `quality` falha porque nenhum teste foi coletado (pytest, código de saída 5) |
| Projeto | BUILT-RAG-Tecnology |
| Pull request | #3 |
| Job / etapa | `quality`, etapa do `uv run pytest` |
| Evidência (run) | https://github.com/th1agOx/BUILT-RAG-Tecnology/actions/runs/42264936744/job/128054270081?pr=3#step:9:9 |
| Detectado por | CI (GitHub Actions), de forma automática |
| Data do achado | 2026-11-09 |
| Commit / branch | _hash: 05f1053d78176365b6c75edf615fe005a0edc405 _nome: Implementando CI  |
| Hora da run | _preencher: Nov 6, 2026, 14:52:00 |
| Severidade | Média: bloqueia o merge, mas não há dado nem segurança em risco |
| Tipo | Achado não planejado (não foi injetado de propósito) |
| Status | Aberto. Será corrigido pela Etapa 4 da US-00 |

## 2. Ambiente (copiado do log)

- pytest 9.1.1, Python 3.12.3
- `rootdir`: `/home/runner/work/BUILT-RAG-Tecnology/BUILT-RAG-Tecnology`
- `configfile`: `pyproject.toml`, `testpaths`: `tests`
- Plugins carregados: xdist, anyio, platformdirs, asyncio (modo STRICT), hypothesis, deepeval, rerunfailures, cov, repeat
- Variáveis: `PYTHON_VERSION` 3.12, `UV_PYTHON_INSTALL_DIR`, `UV_CACHE_DIR`

## 3. Passos para reproduzir

1. Abrir um pull request com o esqueleto da Camada 0 e a pasta `tests/architecture/` sem nenhum arquivo `test_*.py`.
2. O workflow roda o job `quality`.
3. Na etapa de testes, o CI executa `uv run pytest`.

Reprodução local: `uv run pytest` na raiz do repositório.

## 4. Resultado esperado e resultado obtido

| | Descrição |
|---|---|
| Esperado | Se não há teste nenhum, o CI não pode dar verde, porque "nenhum teste rodou" não prova nada. |
| Obtido | `collected 0 items`, `no tests ran in 0.80s`, `Error: Process completed with exit code 5`. O job `quality` ficou vermelho. |

## 5. Análise

- O código 5 do pytest significa "nenhum teste coletado". Não é falha de teste: é ausência de teste.
- O pytest só coleta arquivos chamados `test_*.py` ou `*_test.py` dentro de `testpaths` (`tests`).
- **Causa provável:** a Etapa 4 (testes de arquitetura) ainda não foi executada, então `tests/architecture/` não tem arquivo coletável. _Ainda não confirmada._ Para confirmar, rodar `ls tests/architecture` e `uv run pytest --collect-only -q` e anexar a saída aqui.
- A US-00 previa exatamente esse comportamento antes da Etapa 4. O CI está certo em recusar.

## 6. Por que isto é um bom comportamento (valor do achado)

O CI protege contra o cenário "ninguém percebeu que nenhum teste rodou". Se o código 5 fosse tolerado, a suíte poderia esvaziar por engano (arquivo renomeado, pasta errada) e o pipeline continuaria verde. Por isso a regra é: **o CI nunca aceita código 5**.

## 7. Correção e verificação

| Item | Plano |
|---|---|
| Correção | Executar a Etapa 4 da US-00: criar os testes de arquitetura (14 casos). |
| Controle verde (C0) | Depois da Etapa 4, repetir a run na branch limpa e registrar o link: o `quality` deve ficar verde. |
| Reteste do F0 | Esvaziar `tests/architecture/` em uma branch descartável e confirmar que o CI volta a ficar vermelho (prova de que o alarme continua ativo). |

## 8. Pontos de atenção levantados na análise

- O log mostra plugins (`rerunfailures`, `repeat`, `hypothesis`, `deepeval`) que a US-00 não listava. Conferir no `pyproject.toml` que não existe `--reruns` em `addopts`: repetir teste que falha esconde instabilidade.
- As dependências já estavam instaladas antes da sprint, então esse ponto não é um defeito.

## 9. Evidências anexas

- [ ] Link da run (seção 1)
- [ ] Print do trecho `collected 0 items` e `exit code 5`
- [ ] Saída de `ls tests/architecture` e `uv run pytest --collect-only -q`
- [ ] Link da run verde (C0), depois da Etapa 4