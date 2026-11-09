# ADR-0003: Estrutura de pastas e arquitetura da V1

- **Status:** Aceito
- **Data:** 2026-11-05 (substitui a versão de 2026-11-04, que mantinha `knowledge` e `rag` como módulos planos)
- **Decisor:** Thiago (BUILT)
- **Refina:** ADR-0001. É a fonte única da árvore de pastas e das regras de importação (R1 a R7).

## Contexto

O ADR-0001 define DDD com Bounded Contexts. Na V1 existe uma só LLM (a do funil), uma só entrada e nenhum tenant, então três andares em todos os contextos seriam cerimônia sem ganho.

Mas a árvore de pastas não pode mudar de formato quando a V2 e a V3 chegarem. Mover pasta custa caro: quebra imports, testes de arquitetura, documentos e a memória dos agentes. Por isso a decisão é: **o formato final fica definido agora**. Na V1 algumas pastas ficam quase vazias. Depois, o sistema cresce com pastas novas, nunca com pastas mudando de lugar.

## Decisão

### 1. Estrutura

```
src/built/
├── shared_kernel/            # contratos e tipos comuns (só biblioteca padrão)
├── policy/                   # contexto completo: quem vê o quê
│   ├── published/            # vocabulário público do policy
│   ├── domain/               # andar: regras puras
│   ├── application/          # andar: casos de uso e portas
│   └── infrastructure/       # andar: tecnologia do policy (token, sessão)
├── knowledge/                # contexto: vault → índice
│   ├── model/                # o que é um documento válido
│   └── ingestion/            # lê a vault, valida, divide em chunks e indexa
├── infrastructure/           # pacote: o motor de resposta e tudo que é externo
│   ├── rag/                  # motor de resposta
│   │   ├── ports.py          # interfaces que o motor conhece
│   │   ├── retriever.py      # busca, sempre com o filtro do policy
│   │   ├── gate.py           # gate de contexto
│   │   ├── prompt.py         # montagem do prompt e limite de janela
│   │   ├── output_linter.py  # linter de output
│   │   └── pipeline.py       # orquestra o fluxo
│   └── adapters/             # contratos com o mundo externo
│       ├── qdrant/           # único que fala com o Qdrant
│       ├── llm/              # provedor de LLM
│       └── telemetry/        # OpenTelemetry e Phoenix
└── entrypoints/              # a API: por onde o mundo chega (código na Camada 4)
```

Os andares `domain/`, `application/` e `infrastructure/` existem só dentro do `policy`. Nunca ficam soltos na raiz de `src/built/`.

**Atenção ao nome `infrastructure`.** Ele aparece duas vezes, com sentidos diferentes:

- o **andar** `policy/infrastructure`: a tecnologia que só o `policy` usa (validar token, por exemplo);
- o **pacote** `infrastructure/`: o motor de resposta e os adaptadores de todo o sistema.

Em texto, escreva sempre "andar infrastructure do policy" ou "pacote infrastructure".

### 2. O que cada parte faz

| Parte | Responsabilidade |
|---|---|
| `shared_kernel` | A ponte comum entre as partes: IDs, tipos e o formato dos dados que viajam entre vault, API, backend e, no futuro, outros serviços. Só dados simples (biblioteca padrão). Nunca lógica, nunca conexão |
| `policy` | Quem pergunta e o que pode ver. É o coração do sistema (core domain) |
| `knowledge` | Alimenta a base: o que é um documento válido (`model`) e a ingestão da vault (`ingestion`) |
| `infrastructure/rag` | O motor que responde: busca, gate, prompt, linter de output e pipeline |
| `infrastructure/adapters` | Os contratos com o que é externo: Qdrant, LLM e telemetria |
| `entrypoints` | Os endpoints da API. Montam as peças e chamam o pipeline |

### 3. Regras de arquitetura

| # | Regra |
|---|---|
| R1 | No `policy`: `infrastructure` → `application` → `domain`. Nunca no sentido contrário |
| R2 | `policy/domain` só importa a biblioteca padrão, `built.shared_kernel`, ele mesmo e `built.policy.published` |
| R3 | `shared_kernel` só importa a biblioteca padrão e a si mesmo. Nenhum contexto, nenhuma biblioteca externa |
| R4 | Fora do `policy`, tudo (`knowledge`, `infrastructure`, `entrypoints`) só usa do `policy`: `built.policy.published` e `built.policy.application` |
| R5 | **Regra de ouro:** `built.infrastructure.adapters.qdrant` só é importado por `built.knowledge.ingestion`, por `built.entrypoints` e por ele mesmo. A busca sempre passa pelo `rag`, que exige o filtro do `policy` |
| R6 | `built.infrastructure.rag` nunca importa `built.infrastructure.adapters`: o motor conhece só as portas (`rag/ports.py`). Os adaptadores `llm` e `telemetry` só são importados por `built.entrypoints` e por eles mesmos |
| R7 | Os módulos de `built.infrastructure.rag` só importam a biblioteca padrão, `built.shared_kernel`, `built.policy.published`, `built.policy.application` e eles mesmos. Nenhuma biblioteca externa |

As regras são verificadas por testes de arquitetura (Camada 0).

**Sobre a R7:** ela é uma lista permitida, então barra qualquer biblioteca de terceiros dentro do `rag`, até as inofensivas (por exemplo, `pydantic`). Se uma delas for necessária no futuro, a decisão é do dono e a R7 é revisada por ADR, nunca contornada.

**Sobre a R5 e a R6:** as peças externas são ligadas ao motor na hora de montar a aplicação, em `entrypoints`. Quando o adaptador do Qdrant for criado, ele ganha dois módulos separados, `reader` e `writer`, e a R5 será refinada: `entrypoints` só importa o `reader` e só a ingestão importa o `writer`. Assim dá para ter chaves do Qdrant diferentes para ler e para escrever.

### 4. Rígido onde mora a segurança, flexível onde o comportamento muda

- **Rígido:** `policy`, gate, linter de output, a regra de ouro do Qdrant e o `shared_kernel` puro. Estas partes não mudam quando o comportamento do assistente muda.
- **Flexível:** prompts, modelo de LLM, fluxo de qualificação e parâmetros de busca.

### 5. Por que o `rag` mora dentro do pacote `infrastructure`

Foi uma escolha do dono: o motor de resposta é uma capacidade técnica que o negócio consome, e fica ao lado dos adaptadores que ele usa. Isso mantém o formato estável.

O custo é de leitura: o nome `infrastructure` sugere tecnologia, mas `gate`, `prompt` e `output_linter` são regras puras. Para não confundir os agentes:

- a R7 impõe isso por teste: nenhum módulo do `rag` importa biblioteca externa (só biblioteca padrão e o que a R7 lista). A regra 10 do `AGENTS.md` repete o motivo para os agentes;
- o motor só conhece as portas (R6);
- se esse custo pesar, o ADR pode ser revisado e o `rag` sobe um nível, sem mudar o resto.

### 6. Como o formato se mantém na V2 e na V3

| O que chega | Onde entra |
|---|---|
| LLM 2 e LLM 3 | Mesmo motor (`infrastructure/rag`). O que muda é o perfil, que vem do `policy`, e as rotas novas em `entrypoints` |
| Autenticação por token (site da BUILT) | No andar `policy/infrastructure`. Em espera na V1 (ADR-0002) |
| Qualificação de leads (Camada 5) | Pasta nova `qualification/`, um contexto novo |
| Leitura de documento anexado no chat | Módulo novo em `knowledge`. Entrada não confiável, sem previsão na V1 |
| Agentes e tool calling (V2) | Pasta nova, decidida em ADR quando houver dado que justifique (ADR-0002) |
| Um contexto virar serviço separado | Sai a pasta inteira. O que eles compartilham já está no `shared_kernel` |
| Novo provedor externo (outro banco, outro LLM) | Pasta nova em `infrastructure/adapters` |

### 7. O que ficou de fora

| Item | Motivo |
|---|---|
| Conexões (Phoenix, Qdrant, logger) no `shared_kernel` | Quebraria R3: a tecnologia entraria no coração |
| Busca no índice sem passar pelo `policy` | Brecha de acesso. A R5 e o filtro obrigatório impedem |
| Três andares em `knowledge` e `entrypoints` | Cerimônia sem ganho na V1 |

## Consequências

**Boas**

- O formato da árvore fica estável da V1 à V3.
- A segurança continua verificável por máquina.
- Tecnologia externa fica toda em um só lugar.

**Custos**

- Algumas pastas existem só com docstring na V1.
- O nome `infrastructure` aparece em dois lugares (andar e pacote).
- A pureza dos módulos do `rag` depende da regra 10 do `AGENTS.md` e da revisão do dono.

## Quando revisar

- Quando entrar a LLM 2 ou a LLM 3.
- Se o nome `infrastructure` continuar confundindo os agentes.
- Quando os dados reais de uso mostrarem que o motor precisa ser dividido.