# Regas Fixas Para o Agente Writeródigo, testes ou CI. Leia antes de qualquer tarefa.
 
**Antes de começar, leia:**
 
1. `docs/glossary.md`: a linguagem do projeto.
2. `docs/adr/0001-ddd.md`: a arquitetura e os contextos.
3. O prompt da camada atual: o escopo e a prova de aceite.
## A. Escopo e camadas
 
1. Trabalhe só na camada e na US do prompt atual. Não adiante camadas futuras e não aproveite para refatorar fora do escopo.
2. Uma camada só está pronta quando a prova de aceite é atendida e demonstrada. Liste cada item e como você verificou.
3. Dúvida sobre regra de negócio, acesso ou escopo: pare e pergunte. Não suponha.
## B. Linguagem
 
4. Identificadores (classes, funções, pastas, campos) em inglês. Textos para pessoas (mensagens, documentos, respostas) em português.
5. Use os termos do glossary exatamente como estão. Não invente sinônimos. Termo novo entra no glossary, no mesmo PR, e é destacado na descrição.
6. Para palavras com dois sentidos (`event`, `decision`, `policy`, `client`, `domain`), siga a tabela do glossary.
## C. Arquitetura
 
7. As dependências apontam para dentro: `infrastructure` → `application` → `domain`. O andar `domain` não importa infraestrutura nem frameworks.
8. Um contexto não importa os detalhes internos de outro. Só a interface pública (`application`) ou o vocabulário publicado por `policy`.
9. Nenhuma regra de visibilidade, escopo, tenant ou perfil fora do contexto `policy`. Nada de `if profile == ...` em outros lugares. O padrão é negar: valor ausente, desconhecido ou inválido significa acesso negado.
10. Qdrant, LLM, JWT, GitHub e arquivos só em `infrastructure`, atrás de uma porta.
## D. Segurança e dados
 
11. Nunca use dado real em código, testes ou fixtures: nada de nome de cliente real, CPF, CNPJ, telefone ou e-mail. Use dados fictícios, marcados com a tag `ficticio`.
12. Nunca versione segredos (chaves de API, tokens, `.env`). Só `.env.example`, sem valores. Se encontrar um segredo no repositório, pare e avise.
13. Valores em R$ e tabelas de preço existem só em documentos `interno`. Nunca em código, fixtures públicas ou respostas. Logs registram IDs, nunca conteúdo de documento nem nomes de cliente.
14. A identidade do tenant vem da sessão autenticada e é passada como parâmetro. Nunca vem do texto da pergunta, de variável global ou de contexto implícito.
15. Violação de política significa falhar fechado: registre o incidente e interrompa. Nunca deixe passar.
## E. Testes e qualidade
 
16. Antes de dizer que terminou, rode todos os checks e informe o resultado real.
17. Nunca apague, pule, enfraqueça ou altere um teste, um limiar ou uma configuração de checagem só para passar. Se um teste parecer errado, explique e pergunte.
18. Todo código novo tem tipos e teste. Teste de segurança (acesso e vazamento) não é opcional.
## F. Git, dependências e entrega
 
19. Nunca faça push direto em `main` ou `dev`. Trabalhe numa branch criada a partir de `dev` (`feat/us-XX-descricao`) e abra um PR para `dev`. Quem faz o merge é o dono. Um PR por US, com commits pequenos (`feat:`, `fix:`, `docs:`, `test:`, `chore:`).
20. Não altere as pastas protegidas sem pedido explícito no prompt: `policy/domain`, `tests/architecture`, `.github`, `docs` e este arquivo. Se o prompt pedir, destaque no PR.
21. Só adicione dependência listada no prompt da camada. Qualquer outra precisa de aprovação antes. As versões ficam travadas no `uv.lock`.
22. Termine com um resumo simples, em português: o que foi feito, por quê, como verificar, suposições e riscos. Se algum check falhou, diga qual e por quê. Nunca esconda uma falha.
## Como verificar (os checks)
 
```
uv run ruff check .
uv run ruff format --check .
uv run mypy src
uv run pytest
uv run lint-imports
```
 
Em caso de dúvida, pare e pergunte.