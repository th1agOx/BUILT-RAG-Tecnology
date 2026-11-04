# ADR-0003: Arquitetura simplificada da V1

- **Status:** Aceito
- **Data:** 2026-11-04
- **Decisor:** Thiago (BUILT)
- **Refina:** ADR-0001. O desenho completo continua sendo o alvo para a V2 e a V3.

## Contexto

O ADR-0001 define DDD com Bounded Contexts, cada um com três andares (`domain`, `application`, `infrastructure`). Na V1 existe uma só LLM (a do funil), uma só entrada, nenhum tenant, e a maior parte do trabalho é técnica: ler arquivos, chamar o Qdrant, chamar a LLM.

Três andares em todos os contextos geraria arquivos vazios, interfaces que só repassam dados e mais passos de revisão, sem proteger nada a mais. Uma sugestão externa de simplificação foi avaliada e adotamos parte dela. O que protege o produto (o `policy`, o gate de contexto e o linter de output) fica intacto.

## Decisão

### 1. Estrutura da V1

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
    ├── ports.py          # interfaces que o pipeline conhece (LLM, telemetria, recuperação)
    ├── retriever.py      # único que lê o índice, sempre com o filtro do policy
    ├── gate.py           # gate de contexto
    ├── prompt.py         # montagem do prompt e limite de janela
    ├── output_linter.py  # linter de output
    ├── pipeline.py       # orquestra o fluxo da V1
    └── adapters/         # LLM e telemetria (a tecnologia)
```

A pasta `entrypoints/` (a entrada por perfil) nasce na Camada 4. O contexto `qualification` nasce na Camada 5.

Os andares `domain/`, `application/` e `infrastructure/` existem só dentro do `policy`. Nunca ficam soltos na raiz de `src/built/`.

### 2. O que cada parte faz

| Parte                 | Responsabilidade                                                                                 |
| --------------------- | ------------------------------------------------------------------------------------------------ |
| `shared_kernel`       | Peças comuns mínimas: IDs, tipo de resultado, esquema do payload do índice. Só biblioteca padrão |
| `policy`              | Quem pergunta e o que pode ver. É o coração do sistema (core domain)                             |
| `knowledge/model`     | O que é um documento válido (contrato Built Knowledge Model) e seu ciclo de vida                 |
| `knowledge/ingestion` | Lê a vault, valida, divide em chunks e indexa                                                    |
| `knowledge/index`     | O único lugar que fala com o Qdrant                                                              |
| `rag`                 | Responde perguntas, em um fluxo determinístico                                                   |

### 3. Regras de arquitetura

| #   | Regra                                                                                                                                                                                                                                                         |
| --- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| R1  | No `policy`: `infrastructure` → `application` → `domain`. Nunca no sentido contrário                                                                                                                                                                          |
| R2  | `policy/domain` só importa a biblioteca padrão, `built.shared_kernel`, ele mesmo e `built.policy.published`                                                                                                                                                   |
| R3  | `shared_kernel` só importa a biblioteca padrão e a si mesmo. Nenhum contexto, nenhuma biblioteca externa                                                                                                                                                      |
| R4  | `knowledge`, `rag` e `entrypoints` só usam do `policy`: `built.policy.published` e `built.policy.application`                                                                                                                                                 |
| R5  | **Regra de ouro:** `built.knowledge.index` só é importado pela `ingestion` (escrita) e pelo `rag/retriever.py` (leitura). Assim ninguém consulta o Qdrant sem passar pelo filtro do `policy`, e dá para ter chaves do Qdrant separadas para leitura e escrita |
| R6  | Só o próprio `rag/adapters` importa `rag/adapters`. O restante do `rag` conhece apenas `rag/ports.py`. Na Camada 4, a regra é estendida para permitir a montagem na entrada                                                                                   |

As regras são verificadas por testes de arquitetura (Camada 0).

### 4. Rígido onde mora a segurança, flexível onde o comportamento muda

- **Rígido:** `policy`, gate, linter de output, a regra de ouro do índice e o `shared_kernel` puro. Estas partes não mudam quando o comportamento do assistente muda.
- **Flexível:** prompts, modelo de LLM, fluxo de qualificação e parâmetros de busca. Mudam sem tocar nas partes rígidas.

### 5. O que ficou de fora

| Item                                                                 | Motivo                                                               |
| -------------------------------------------------------------------- | -------------------------------------------------------------------- |
| `orchestration/` com agente, `tools/` e function calling             | Pertence à V2 (ADR-0002). Na V1 o fluxo é um pipeline determinístico |
| Conexões (Phoenix, banco vetorial, logger) dentro do `shared_kernel` | Quebraria R2 e R3: a tecnologia entraria no `policy`                 |
| Busca no índice sem passar pelo `policy`                             | Brecha de acesso. A R5 impede                                        |
| Três andares em `knowledge` e `rag`                                  | Cerimônia sem ganho na V1                                            |

### 6. Quando promover um módulo ao desenho completo

Um módulo plano vira contexto com três andares quando tiver pelo menos uma destas características:

- uma regra de negócio real, além de entrada e saída;
- mais de uma entrada consumindo o módulo (por exemplo, cliente e operação);
- necessidade de virar um serviço separado.

Isso deve acontecer com a LLM 2, a LLM 3 e os agentes de pós-venda.

## Consequências

**Boas**

- Menos pastas, menos código de repasse e menos passos de revisão na V1.
- A segurança continua verificável por máquina.
- A estrutura de partida já aponta as fronteiras para a V2 e a V3.

**Custos**

- `knowledge` e `rag` terão menos isolamento formal. Compensamos com as regras R4 a R6.
- A promoção para contexto completo será uma refatoração planejada.

## Quando revisar

- Quando entrar a LLM 2 ou a LLM 3.
- Quando um módulo atender algum critério da seção 6.
- Quando os dados reais de uso mostrarem que o `rag` precisa ser dividido.
