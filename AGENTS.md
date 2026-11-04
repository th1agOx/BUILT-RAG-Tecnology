# AGENTS.md: regras para agentes da BUILT

Estas regras valem para o agent writer, para agentes autônomos e para robôs de automação que mexam em código, testes ou CI. Leia antes de qualquer tarefa.

**Antes de começar, leia:**

1. `docs/glossary.md`: a linguagem do projeto.
2. `docs/adr/0001-ddd.md`: por que DDD e Bounded Contexts.
3. `docs/adr/0002-v1-scope.md`: o que entra na V1, o que fica para depois e as decisões de plataforma.
4. `docs/adr/0003-v1-architecture.md`: a estrutura da V1 e as regras de arquitetura.
5. O arquivo da sprint atual (por exemplo `docs/sprints/US-00.md`): as etapas e a prova de aceite.

## A. Escopo e etapas

1. Trabalhe só na etapa atual do prompt. Cada US é uma sprint com várias etapas: execute uma por vez, pare ao terminar e espere o dono dizer "próxima". Não adiante etapas ou camadas futuras e não aproveite para refatorar fora do escopo.

   **Ordem de construção** (vale a partir da Camada 1, quando passa a existir código de negócio). Escreva de dentro para fora, nesta ordem, e **pare ao fim de cada passo** para o dono conferir:
   - **1º, regras sem tecnologia:** `policy/domain`, `knowledge/model` e, no `rag`, `gate.py`, `prompt.py` e `output_linter.py`. Só biblioteca padrão, `shared_kernel` e o que o `policy` publica.
   - **2º, casos de uso e portas:** `policy/application`, `rag/ports.py` e `rag/pipeline.py`.
   - **3º, tecnologia:** `policy/infrastructure`, `knowledge/ingestion`, `knowledge/index`, `rag/retriever.py` e `rag/adapters/`.
   - **4º, entrada (`entrypoints/`):** só depois que os três passos anteriores estiverem aprovados.

   Em cada passo:
   - Escreva só o que a prova de aceite da etapa exige. Código sem uso não entra. Se o passo ainda não precisa de algo, não crie.
   - Entregue o código e um resumo curto: o que existe, o que cada peça faz e como verificar. Os testes do passo são só os que o dono especificou (regra 18).
   - Espere o "ok" do dono antes de começar o passo seguinte.
   - Não altere um passo já aprovado para acomodar o seguinte. Se achar que é preciso, pare e explique o motivo.

2. Uma camada só está pronta quando a prova de aceite é atendida e demonstrada. Liste cada item e como você verificou.
3. Dúvida sobre regra de negócio, acesso ou escopo: pare e pergunte. Não suponha.

## B. Linguagem

4. Identificadores (classes, funções, pastas, campos) em inglês. Textos para pessoas (mensagens, documentos, respostas) em português. Comentários e docstrings também em português simples.
5. Use os termos do glossary exatamente como estão. Não invente sinônimos. Termo novo entra no glossary, no mesmo PR, e é destacado na descrição.
6. Para palavras com dois sentidos (`event`, `decision`, `policy`, `client`, `domain`), siga a tabela do glossary.

## C. Arquitetura

7. As dependências apontam para dentro. No `policy`: `infrastructure` → `application` → `domain`, e o andar `domain` só usa a biblioteca padrão. No `rag`, os módulos centrais (`retriever`, `gate`, `prompt`, `output_linter`, `pipeline`) conhecem as portas (`rag/ports.py`) e nunca os adaptadores (`rag/adapters/`). O `shared_kernel` só usa a biblioteca padrão.

   **Estrutura da V1** (ADR-0003). Os andares `domain/`, `application/` e `infrastructure/` existem só dentro do `policy`. Nunca ficam soltos na raiz de `src/built/`:

   ```
   src/built/
   ├── shared_kernel/        # tipos e utilitários puros (não é um contexto)
   ├── policy/               # contexto com os três andares
   │   ├── published/        # vocabulário público do policy
   │   ├── domain/           # andar: regras puras
   │   ├── application/      # andar: orquestra e define portas
   │   └── infrastructure/   # andar: tecnologia
   ├── knowledge/            # contexto: vault → índice
   │   ├── model/            # o que é um documento válido
   │   ├── ingestion/        # lê, valida, divide em chunks e indexa
   │   └── index/            # único lugar que fala com o Qdrant
   └── rag/                  # contexto: responde perguntas
       ├── ports.py  retriever.py  gate.py  prompt.py  output_linter.py  pipeline.py
       └── adapters/         # LLM e telemetria
   ```

   A pasta `entrypoints/` nasce na Camada 4.

8. Um contexto não importa as peças internas de outro. Do `policy`, os outros só usam `built.policy.published` e `built.policy.application`. Só a `ingestion` escreve no índice (`knowledge/index`) e só o `rag/retriever.py` lê dele.
9. Nenhuma regra de visibilidade, escopo, tenant ou perfil fora do contexto `policy`. Nada de `if profile == ...` em outros lugares. O padrão é negar: valor ausente, desconhecido ou inválido significa acesso negado.
10. Tecnologia (Qdrant, LLM, JWT, arquivos, telemetria com OpenTelemetry e Phoenix) só em `policy/infrastructure`, `knowledge/ingestion`, `knowledge/index` e `rag/adapters/`, atrás de uma porta. Nunca em `policy/domain`, `policy/application`, `shared_kernel`, `knowledge/model` nem nos módulos centrais do `rag`.

## D. Segurança e dados

11. Nunca use dado real em código, testes ou fixtures: nada de nome de cliente real, CPF, CNPJ, telefone ou e-mail. Use dados fictícios, marcados com a tag `ficticio`.
12. Nunca versione segredos (chaves de API, tokens, `.env`). Só `.env.example`, sem valores. Se encontrar um segredo no repositório, pare e avise.
13. Valores em R$ e tabelas de preço existem só em documentos `interno`. Nunca em código, fixtures públicas ou respostas. Logs e telemetria registram IDs, números e tempos, nunca o texto da pergunta, da resposta, de chunks ou de documentos, nem nomes de cliente.
14. A identidade do tenant vem da sessão autenticada e é passada como parâmetro. Nunca vem do texto da pergunta, de variável global ou de contexto implícito.
15. Violação de política significa falhar fechado: registre o incidente e interrompa. Nunca deixe passar.
16. portas do Qdrant e do Phoenix abertas só para o seu computador (127.0.0.1), nunca para a rede.

## E. Testes e qualidade

17. Antes de dizer que terminou, rode todos os checks e informe o resultado real.
18. Nunca apague, pule, enfraqueça ou altere um teste, um limiar ou uma configuração de checagem só para passar. Se um teste parecer errado, explique e pergunte.
19. **O dono define o que é testado.** Os testes respondem a perguntas definidas pelo dono: o relatório conceitual e o plano de testes dele, ou os casos listados no prompt da etapa. O agente não decide a estratégia de testes.
    - Escreva só os testes dos casos que o dono especificou. Cada teste começa com uma docstring de uma linha com a **pergunta que ele responde**, em português e em termos de negócio (por exemplo: "Um perfil lead consegue ver um documento interno?"), e cita o caso do dono.
    - Não escreva teste por conta própria: nada de teste só para subir cobertura, nada de teste que apenas repete o que o código faz e nada de mock que torne a resposta óbvia.
    - Sentiu falta de um caso? Não escreva. Liste em "Casos sugeridos (não escritos)" no resumo, para o dono avaliar.
    - Etapa com código, mas sem casos de teste definidos: pare e peça os casos antes de continuar.
    - Todo código novo tem tipos.
    - Teste de segurança (acesso e vazamento) continua obrigatório, mas os casos também são definidos pelo dono.

## F. Dependências e entrega

20. Não altere as pastas e arquivos protegidos sem pedido explícito no prompt: `policy/domain`, `tests/architecture`, `.github`, `docs`, este arquivo, `pyproject.toml`, `uv.lock`, `.pre-commit-config.yaml` e futuramente `Dockerfile`, `docker-compose.yml`, .`dockerignore` . Se o prompt pedir, destaque no resumo.
21. Só adicione dependência listada no prompt da etapa. Qualquer outra precisa de aprovação antes. As versões ficam travadas no `uv.lock`.
22. Termine com um resumo simples, em português: o que foi feito, por quê, como verificar, suposições, riscos e casos de teste sugeridos (não escritos). Se algum check falhou, diga qual e por quê. Nunca esconda uma falha.

## Como verificar (os checks)

```
uv run ruff check .
uv run ruff format --check .
uv run mypy src
uv run pytest
uv run lint-imports
```

Em caso de dúvida, pare e pergunte.
