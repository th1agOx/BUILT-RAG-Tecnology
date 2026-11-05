# ADR-0002: Escopo da V1 e decisões de plataforma

- **Status:** Aceito
- **Data:** 2026-11-05
- **Decisor:** Thiago (BUILT)

## Contexto

A V1 é o chatbot de topo de funil (LLM 1). Ele é público, fica exposto na web, só qualifica leads e só enxerga documentos públicos. Por ser público, a segurança vem primeiro e não se adia para uma versão futura.

O foco inicial de medição é **custo e desempenho** (tokens, tempo, gasto). A qualidade das respostas depende do conteúdo da vault, que será indexado aos poucos, e entra na avaliação em uma etapa posterior.

## Decisões

### 1. Contextos e entradas

- Contextos da V1: `policy` e `knowledge`, mais o `shared_kernel` puro, o pacote `infrastructure` (motor `rag` e adaptadores) e `entrypoints`. A estrutura completa está no ADR-0003, que refina o ADR-0001.
- Os perfis de uso (lead, cliente, operação) **não são contextos**. São portas de entrada, em `entrypoints/`. Todas chamam o mesmo fluxo do `rag`, mudando só o perfil. A V1 tem uma entrada: o chat de funil (LLM 1). A pasta `entrypoints/` existe desde a Camada 0, mas o código dela chega na Camada 4.
- O contexto `qualification` (as perguntas, a pontuação e o encaminhamento para humano) nasce na Camada 5.
- Pós-venda, suporte e sustentação serão contextos novos no futuro. Os atuais não mudam.
- **Porta pública:** o `policy` publica `built.policy.published` (vocabulário) e `built.policy.application`. O resto do sistema segue as regras do ADR-0003. Ninguém importa as peças internas do `policy`.

### 2. Fluxo da V1

```
Pergunta
  → checagem leve da pergunta
  → sessão (Principal)
  → busca com filtro do Qdrant
  → gate de contexto
  → montagem do prompt (limite de janela)
  → LLM
  → linter de output (formato + conteúdo)
  → resposta
```

Se a LLM falhar ou demorar, o sistema tenta uma vez de novo. Se continuar falhando, envia uma mensagem pronta e encaminha para um humano (falha segura).

### 3. O que entra na V1

- Limite de janela de contexto por perfil (a regra do limite mora no `policy`).
- Structured output em JSON, conferido pelo linter de output.
- Guardrails: filtro de busca, gate de contexto (falha fechado), linter de output e checagem leve da pergunta.
- Falha segura.
- Observabilidade mínima (seção 5).

### 4. Checagem da pergunta

A proteção real não depende dela, porque a LLM 1 só vê documentos públicos e o gate e o linter continuam valendo. Por isso a checagem é branda:

- Uma mensagem estranha nunca bloqueia sozinha. Ela só deixa uma marca.
- A decisão olha a sessão inteira (saídas do assunto, tentativas repetidas de mudar as regras, ritmo das mensagens), e não uma mensagem isolada.
- A reação é gradual: segue normal, responde e redireciona, encaminha para humano, limita o ritmo.
- Bloqueio direto só em casos óbvios (mensagem gigante, lixo).
- Na Camada 4 (sem sessão) ela é mínima: limite de tamanho e marcação. Na Camada 5, com histórico, passa a olhar a conversa.
- Medimos quantas vezes ela marca algo indevidamente.

### 5. Observabilidade

- **Telemetria:** OpenTelemetry. **Visualização:** Phoenix.
- **Camada 4 (mínima):** cada pergunta recebe um ID. Registramos tempo por etapa (busca, gate, LLM, linter), tokens, custo estimado e contadores de incidentes do gate e do linter.
- **Camada 7 (completa):** painéis, alertas e trilha de auditoria.
- **Privacidade (obrigatório):** traces e logs guardam IDs, números e tempos. Nunca guardam o texto da pergunta, da resposta, dos chunks nem dos documentos. Alguns instrumentadores de LLM registram o conteúdo por padrão, então a configuração deve desligar isso e a Camada 4 precisa de um teste que comprove. Confirmar como desligar na versão usada.
- A telemetria vive em `infrastructure/adapters/telemetry`, atrás de uma porta definida em `infrastructure/rag/ports.py`. O `policy/domain` e o `shared_kernel` não a importam.
- Confirmar na documentação como o Phoenix recebe os dados do OpenTelemetry e como ele é hospedado.

### 6. Formatos

- Resposta da LLM: JSON, validado pelo linter de output. O conteúdo (campos por perfil) ainda está em aberto.
- API pública (site e chat): JSON sobre HTTP.
- Qdrant: REST ou gRPC é uma escolha do adaptador e não afeta as regras.
- gRPC com Protocol Buffers entre serviços só entra quando um contexto virar um serviço separado. Enquanto for um monólito, as chamadas acontecem dentro do mesmo processo.

### 7. Autenticação (em espera)

- Na V1 não há área de login nem de usuário. O lead é uma sessão anônima.
- No futuro, o site da BUILT poderá enviar um token de autenticação, para a LLM 2, o pós-qualificação e o acompanhamento e suporte dos serviços. O foco da operação não é o acompanhamento pelo site, então isso fica em espera.
- Quando entrar, o tenant virá do token validado, nunca do texto digitado, e a validação mora no andar `policy/infrastructure`. Até lá, esse andar fica vazio.

## Fica para depois (V2), decidido por dados

| Item | Dado que decide | Sinal para avançar |
|---|---|---|
| Streaming | Tempo até a resposta (p95), desistência da conversa | Leads desistem esperando |
| Fallback de modelo | Taxa de erro e timeout do provedor | Falhas frequentes |
| Prompt caching | Tokens fixos por pergunta e volume | Custo relevante |
| Tool calling e agentes | Ação real necessária | Pós-venda |

Os limites numéricos de cada sinal serão definidos pelo dono quando houver dados reais.

**Por que o streaming não entra na V1:** o linter de output só consegue conferir a resposta inteira, e o streaming envia o texto aos poucos. Um conteúdo proibido poderia aparecer na tela antes da conferência.

**Por que o fallback exige cuidado:** outro modelo se comporta diferente. O modelo reserva precisa passar no mesmo eval e no mesmo linter, e a troca acontece só por erro, tempo esgotado ou limite do provedor, nunca por "resposta ruim".

## Decisões em aberto

- Campos do JSON de resposta por perfil.
- As 4 perguntas de qualificação, a pontuação e o destino do encaminhamento (CRM ou WhatsApp).
- Valores do limite de consumo por perfil e limites numéricos dos gatilhos da V2.
- Estratégia de coleções no Qdrant.
- Mecanismo de autenticação (em espera, seção 7).
- Busca híbrida e re-ranker: decisão de adotar já tomada. A recomendação é medir antes com busca só densa, para ter uma linha de base, e usar um modelo multilíngue (a base é em português).

## Consequências

- O que entra na V1 é pequeno e verificável, e cada camada tem prova de aceite.
- Os itens adiados avançam por dado, o que evita construir algo que não compensa.
- A observabilidade começa cedo e dá os números de custo e desempenho para decidir a V2.
- Custo: a telemetria precisa de cuidado com privacidade desde o início.

## Quando revisar

- Quando houver dados reais de uso (custo, latência, erro).
- Quando entrar a LLM 2 ou a LLM 3.
- Quando um contexto precisar virar serviço separado.