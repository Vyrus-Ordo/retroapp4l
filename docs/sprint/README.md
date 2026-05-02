# RetroApp 4L — Sprint Planning Index

## Visão Geral

Este diretório contém o planejamento detalhado de cada sprint do projeto RetroApp 4L, conforme definido no [PRD v7.0](../RetroApp_4L_PRD_v7.md) seção 12.3.

## Estrutura de Repositórios

```
backend/        # Django — API REST + WebSocket
frontend/       # Nuxt 3 + Tailwind CSS — SPA
```

## Sprints

| Sprint | Documento | Foco | Entregáveis Principais |
|---|---|---|---|
| 1 | [SPRINT_1.md](./SPRINT_1.md) | Fundação | Estrutura do projeto, Docker, PostgreSQL, migrations, auth local + OAuth, criação de sessão com `team_key` |
| 2 | [SPRINT_2.md](./SPRINT_2.md) | Core Real-time | Django Channels + ASGI, consumers WebSocket, máquina de estados de fases, cronômetro com pausa via Celery Beat |
| 3 | [SPRINT_3.md](./SPRINT_3.md) | Board 4L + Marcos | CRUD de cards, modelo `Milestone`, preparação/apresentação de marcos, board em tempo real |
| 4 | [SPRINT_4.md](./SPRINT_4.md) | Agrupamento + Votação | Agrupamento por seleção múltipla, dot voting restrito a `loathed`/`longed`, regra de 1 voto/card |
| 5 | [SPRINT_5.md](./SPRINT_5.md) | Fechamento do ciclo | Check de ações anteriores, action items, fase de Debate, encerramento, dashboard de histórico |
| 6 | [SPRINT_6.md](./SPRINT_6.md) | Frontend | Nuxt 3 + Tailwind CSS, todas as telas e componentes, alerta sonoro do cronômetro |
| 7 | [SPRINT_7.md](./SPRINT_7.md) | Polish + Qualidade | Painel de controle de entrada, presença em tempo real, testes E2E, cobertura ≥ 80%, acessibilidade |
| 8 | [SPRINT_8.md](./SPRINT_8.md) | Integrações (futuro) | Linear, GitHub Issues, exportação PDF/CSV, analytics, drag-and-drop |

## Handoffs

Cada sprint gera um documento de handoff (`SPRINT_N_HANDOFF.md`) na raiz do repositório, seguindo a estrutura definida no PRD seção 12.2. Os handoffs são o único mecanismo de continuidade entre sessões do agente de IA.

## Prompt de Inicialização de Sprint

```
Você é o desenvolvedor do RetroApp 4L, uma plataforma open source de retrospectivas ágeis.

Leia o arquivo SPRINT_1.md no diretorio docs/sprint do repositório.
Ele contém o estado atual do projeto e exatamente o que deve ser feito nesta sprint.

Siga os padrões estabelecidos nas sprints anteriores.
Para o frontend, aplique rigorosamente o design system descrito na seção 7 do PRD:
classes utilitárias do Tailwind CSS, fonte Inter, tokens de cor do tailwind.config.ts,
escala de espaçamento 4px, componentes definidos.

Ao finalizar, gere o rascunho do SPRINT_(N+1)_HANDOFF.md seguindo a estrutura definida no PRD.
Não tome decisões arquiteturais ou visuais não previstas no PRD sem registrar explicitamente
no handoff para validação do Tech Lead.
```

## Dependências entre Sprints

```
Sprint 1 (Foundation)
  └── Sprint 2 (Core Real-time)
        └── Sprint 3 (Board 4L + Marcos)
              └── Sprint 4 (Agrupamento + Votação)
                    └── Sprint 5 (Fechamento do ciclo)
                          └── Sprint 6 (Frontend)
                                └── Sprint 7 (Polish + Quality)
                                      └── Sprint 8 (Integrações — futuro)
```

Sprints 1-5 são backend-first (API + WebSocket). Sprint 6 implementa o frontend consumindo a API. Sprint 7 refina e testa. Sprint 8 é pós-MVP.
