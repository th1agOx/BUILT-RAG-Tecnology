# Glossary

> Fonte única da linguagem da BUILT. Leia este arquivo antes de nomear qualquer coisa no código, nos testes ou nos pipelines.

## Por que este arquivo existe

O glossary diz, para pessoas e para máquinas, o que cada termo significa e como ele aparece no código. Ele existe por cinco motivos:

1. **Uma palavra, um significado.** Sem ele, cada agente inventa sinônimos (`Customer`, `Account`, `Lesson`, `Insight`) e o código passa a falar de coisas que a vault chama de outro jeito.
2. **Liga o código à vault.** Os termos de tipo de documento são os da vault (Built Knowledge Model V1). O código usa exatamente os mesmos nomes.
3. **É contexto obrigatório para quem escreve ou mexe no código.** Isso vale para o agent writer, para futuros agentes autônomos e para robôs de automação (CI, testes, linters, validadores). Quem for alterar código, teste ou pipeline lê este arquivo antes.
4. **Evita erro silencioso.** Nome de classe, pasta, campo, teste e mensagem de erro seguem o glossary. Nome diferente é erro de revisão, não detalhe de estilo.
5. **Faz a ponte entre idiomas.** O produto e os textos para pessoas são em português. Os identificadores de código são em inglês, porque a estrutura da vault nasceu em inglês. Este arquivo é a tradução oficial entre os dois.

## Como usar

- Escreva o termo exatamente como aparece na coluna **Term**.
- Não crie sinônimos. A coluna **Não use** lista os mais comuns.
- Precisa de um termo novo? Acrescente aqui e destaque na descrição da mudança.
- Mudar o significado de um termo é mudança de contrato e exige aprovação humana.
- Texto para pessoas (mensagens, documentos, respostas do chatbot) é em português. Nomes no código são em inglês.

## Document types (termos da vault)

| Term        | ID prefix | O que é                                                                                         | Não use                    |
| ----------- | --------- | ----------------------------------------------------------------------------------------------- | -------------------------- |
| CORE        | `cor`     | Identidade, princípios, políticas e contratos da própria Built. Inclui o Built Knowledge Model. | Config, Settings           |
| METHODOLOGY | `met`     | Como a Built trabalha, de forma reutilizável.                                                   | Framework, Approach        |
| CLIENT      | `cli`     | Um cliente da Built: cadastro e contexto. É o dono do tenant.                                   | Customer, Account, Company |
| PROJECT     | `prj`     | Um projeto feito para um cliente. Sempre pertence a um CLIENT.                                  | Job, Engagement            |
| EVENT       | `evt`     | Algo que aconteceu, com data. É fato, não opinião.                                              | Log, Occurrence            |
| DECISION    | `dec`     | Uma escolha tomada pela Built, com alternativas e motivo.                                       | Choice, Resolution         |
| LEARNING    | `lrn`     | Generalização derivada de evidências. Sempre aponta suas fontes (EVENT ou EXPERIMENT).          | Lesson, Insight            |
| PROCESS     | `prc`     | Passo a passo operacional que se repete.                                                        | Workflow, Procedure        |
| SYSTEM      | `sys`     | Ferramenta ou sistema usado na operação da Built.                                               | Tool, Service              |
| PRODUCT     | `prd`     | O que a Built vende.                                                                            | Offer, Package             |
| CHANNEL     | `chn`     | Canal de aquisição ou de comunicação.                                                           | Medium, Source             |
| EXPERIMENT  | `exp`     | Teste com hipótese, método e resultado.                                                         | Test, Trial, Study         |

Observação: este glossary define o **significado** dos termos. Quem pode ver cada tipo de documento **não** está aqui. Essa regra mora só no contexto `policy`, para existir em um único lugar.

## Termos de arquitetura

| Term           | O que é                                                                                                                                | Não use                  |
| -------------- | -------------------------------------------------------------------------------------------------------------------------------------- | ------------------------ |
| Context        | Pasta de `src/built/` com um assunto de negócio próprio: `policy`, `knowledge`, `rag`.                                                 | Module, Service          |
| Floor (andar)  | Papel técnico dentro de um contexto completo: `domain/`, `application/` e `infrastructure/`. Na V1, só o `policy` tem os três andares. | Layer, Tier              |
| Layer (Camada) | Etapa da trilha de desenvolvimento (Camada 0 a 7), com prova de aceite. Não é o mesmo que andar.                                       | Phase, Stage             |
| Port           | Interface que o núcleo define para falar com o mundo externo (LLM, telemetria, recuperação).                                           | Contract, Abstract class |
| Adapter        | Implementação de uma porta com uma tecnologia concreta (API de LLM, Qdrant).                                                           | Driver, Wrapper          |
| Principal      | Quem pergunta: o perfil de uso e o tenant, vindos da sessão autenticada.                                                               | User, Caller             |
| Profile        | Perfil de uso: lead, cliente ou operação, que correspondem às LLMs 1, 2 e 3.                                                           | Role, Persona            |
| Context gate   | Conferência dos chunks recuperados antes de irem para a LLM. Falha fechado.                                                            | Guard                    |
| Output linter  | Conferência da resposta da LLM depois de gerada.                                                                                       | Validator, Sanitizer     |

## Palavras com dois sentidos

Algumas palavras existem na vault e no código com sentidos diferentes. Siga esta tabela para não misturar.

| Palavra  | Na vault                                                       | No código                                                                                                                                               |
| -------- | -------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------- |
| event    | Tipo de documento EVENT: algo que aconteceu na Built.          | Sinal interno do sistema (domain event). Use o nome com sufixo claro (`...Detected`, `...Occurred`) e a base `DomainEvent`.                             |
| decision | Tipo de documento DECISION.                                    | `AccessDecision`: resultado de uma checagem de acesso (permitir ou negar).                                                                              |
| policy   | Documentos CORE de política (por exemplo, política de preços). | Contexto `policy`: as regras de acesso do sistema.                                                                                                      |
| client   | CLIENT: cliente da Built.                                      | Em código de rede, escreva `http_client`, `qdrant_client`. Nunca só `client`.                                                                           |
| domain   | (não se aplica)                                                | Só o andar `domain/` do `policy`, com as regras puras de acesso. Não existe contexto chamado `domain`: o modelo do documento vive em `knowledge/model`. |

## Ainda não definido

Os campos de metadata do frontmatter da vault (`visibilidade`, `escopo`, `status` e outros) hoje estão em português no contrato. O mapeamento deles para nomes em inglês será definido quando a camada de `knowledge/model` começar. Até lá, ninguém inventa esses nomes.
