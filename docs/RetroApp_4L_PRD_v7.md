# RetroApp 4L — Documento de Requisitos do Produto (PRD)

**Versão:** 7.0 — MVP (Open Source / Infraestrutura Zero-Cost)
**Data:** Maio 2026
**Status:** Versão consolidada — adaptação open source
**Audiência:** Agente de IA (executor principal), Tech Lead (revisão / infra / deploy)
**Licença:** MIT

> **Changelog v7.0:**
> - Projeto convertido para open source; todas as referências a fornecedores específicos removidas
> - Design system substituído: Tailwind CSS (utility-first, configurável, padrão da comunidade)
> - Modelo de autenticação alterado: auth local (e-mail + senha) como primário, OAuth opcional (Google, GitHub)
> - Restrição de domínio removida; substituída por lista de domínios permitidos configurável via variável de ambiente (opcional)
> - Integração com rastreadores externos removida do escopo completamente
> - Stack de frontend atualizada: Nuxt 3 + Tailwind CSS
> - Stack de infraestrutura mantida: Fly.io, Neon, Upstash, Vercel (zero-cost)
> - Todos os textos de interface convertidos para inglês (produto open source global)

---

## 1. Visão Geral

O RetroApp 4L é uma plataforma web open source para conduzir retrospectivas de sprint estruturadas na metodologia dos 4 Ls (Liked, Loathed, Longed For, Learned). O produto combina colaboração em tempo real, cronômetro sincronizado e rastreabilidade de itens de ação — fechando o ciclo entre o que é decidido na retro e o que é executado na sprint seguinte.

O projeto é projetado para ser auto-hospedado, gratuito para rodar em escala de MVP, e fácil de estender por agentes de IA ou contribuidores humanos.

### 1.1 Problema

- Retrospectivas conduzidas em ferramentas genéricas (Miro, EasyRetro, Google Jamboard) não estão integradas ao fluxo de trabalho do time.
- Itens de ação decididos nas retros raramente se tornam tarefas rastreáveis.
- Não há mecanismo para verificar, na retro seguinte, se as ações da sprint anterior foram cumpridas.
- Não há histórico centralizado de retrospectivas para acompanhar a evolução do time ciclo a ciclo.

### 1.2 Objetivos do MVP

- Conduzir retrospectivas 4L com colaboração em tempo real (board compartilhado + cronômetro sincronizado).
- Autenticar usuários via contas locais (e-mail + senha), com OAuth opcional (Google, GitHub).
- Permitir ao facilitador convidar membros via link privado.
- Verificar ações da sprint anterior antes de iniciar a reflexão.
- Registrar itens de ação com responsável e prazo.
- Salvar automaticamente todas as retrospectivas para consulta futura.
- Operar com custo zero de infraestrutura utilizando tiers gratuitos de plataformas cloud.

### 1.3 Critérios de Sucesso do MVP

| Indicador | Meta |
|---|---|
| Adoção | ≥ 80% das retrospectivas do time conduzidas no RetroApp 4L |
| Rastreabilidade | ≥ 70% dos itens de ação registrados com responsável e prazo preenchidos |
| Reabertura | ≥ 50% das sessões incluem a verificação de ações da sprint anterior |
| Estabilidade | Zero incidentes de dessincronização de board em produção |
| Satisfação | NPS interno ≥ 7 após pesquisa com facilitadores (mínimo 5 respostas) |
| Custo | Custo total de infraestrutura = R$ 0,00 durante o período MVP |

### 1.4 Fora do Escopo do MVP

- Integrações com rastreadores externos de tarefas (Jira, Linear, Asana, GitHub Issues).
- Exportação em PDF, CSV ou DOCX.
- Mascaramento de cards durante a fase de escrita.
- Relatórios e analytics de tendências entre sprints.
- Drag-and-drop para agrupamento de cards (fase 2).
- SSO / SAML para deployments enterprise.

---

## 2. Premissas de Desenvolvimento

### 2.1 Modelo de execução

- **O desenvolvedor é um agente de IA (ex: Claude Code CLI)**, rodando autonomamente por sessão.
- **O Tech Lead (humano)** é responsável por: revisão de código, decisões de infra, configuração de ambiente, deploy, escrita e validação do documento de handoff ao final de cada sprint.
- O agente de IA **não tem memória entre sessões**. Todo contexto necessário deve estar no documento de handoff. Se não está no handoff, não existe para a próxima sessão.

### 2.2 Consequências arquiteturais

- **Convenção sobre configuração:** código deve seguir padrões idiomáticos do Django e do Tailwind CSS.
- **Estrutura de arquivos previsível:** definida na Sprint 1 e nunca alterada sem atualização explícita no handoff.
- **Testes como documentação viva:** cada sprint produz testes que descrevem o comportamento implementado.
- **Sem "magia" implícita:** evitar padrões que dependem de estado global ou comportamento implícito difícil de rastrear.

### 2.3 Responsabilidades por papel

| Responsabilidade | Agente de IA | Tech Lead |
|---|---|---|
| Implementar features das sprints | ✅ | — |
| Escrever testes unitários e de integração | ✅ | Revisa |
| Criar e atualizar migrations | ✅ | Revisa e executa |
| Configurar ambiente local (docker-compose) | ✅ | Valida |
| Provisionar infra (Fly.io, Neon, Upstash, Vercel) | — | ✅ |
| Configurar CI/CD (GitHub Actions) | Gera o YAML | ✅ executa |
| Revisar PRs e validar comportamento | — | ✅ |
| Escrever documento de handoff da sprint | Gera rascunho | ✅ valida e assina |
| Decisões de produto não previstas no PRD | — | ✅ |

---

## 3. Perfis de Usuário

### Facilitador
Membro do time responsável por criar e conduzir a sessão. Prepara os marcos antes da retro, controla o avanço entre fases, configura o cronômetro (com pausa e retomada), gerencia entrada de participantes e é o único com permissão de agrupar cards e encerrar a sessão.

**Necessidades principais:** controle total do fluxo, visibilidade do estado de todos os participantes, ferramentas ágeis para agrupamento, capacidade de intervir em qualquer fase sem travar a sessão.

### Participante
Membro do time convidado via link. Pode criar, editar e excluir seus próprios cards, votar (apenas nas colunas designadas), participar do debate e registrar itens de ação. Não pode avançar fases, agrupar cards, gerenciar entrada de participantes ou encerrar a sessão.

**Necessidades principais:** interface rápida para adicionar cards, clareza sobre em qual fase está e o que se espera dela naquele momento, visibilidade dos marcos e do card em foco durante o debate.

---

## 4. User Stories

### Facilitador

**US-01 — Criar sessão**
> Como facilitador, quero criar uma sessão de retrospectiva informando o nome da sprint e o identificador do time, para que o time tenha contexto antes de entrar no board e as retros possam ser agrupadas por time.

**Critérios de aceite:**
- Campo obrigatório: nome da sprint.
- Campo obrigatório: `team_key` (identificador do time, estilo slug). Dropdown com sugestões de valores usados anteriormente pelo facilitador.
- Campo opcional: descrição livre.
- Sessão inicia no estado `setup` (preparação offline).

---

**US-02 — Convidar participantes**
> Como facilitador, quero compartilhar um link de convite privado, para que apenas as pessoas certas participem da sessão.

**Critérios de aceite:**
- Link contém token UUID v4, gerado quando o facilitador ativa o lobby.
- O link pode ser revogado pelo facilitador a qualquer momento.
- Ao acessar o link, o participante deve ser autenticado antes de entrar.
- Após o facilitador iniciar a sessão (status diferente de `lobby`), o link é automaticamente bloqueado para novas entradas.
- Tentativas de entrada com link bloqueado exibem mensagem informativa.

---

**US-02b — Gerenciar entrada de participantes após o início**
> Como facilitador, quero liberar temporariamente o acesso a participantes que não conseguiram entrar antes do início da sessão.

**Critérios de aceite:**
- Painel de participantes exibe status do link (ativo/bloqueado) apenas para o facilitador.
- Botão "Permitir nova entrada" reativa o link por 2 minutos ou até o próximo ingresso, o que ocorrer primeiro.
- Após ingresso ou expiração, link volta a ser bloqueado automaticamente.
- Ação registrada no `AccessLog`.
- Participantes já presentes não são afetados.
- Novo participante recebe snapshot completo da sessão via WebSocket.

---

**US-03 — Controlar fases**
> Como facilitador, quero avançar as fases manualmente, para que o time não passe para a próxima etapa antes de estar pronto.

**Critérios de aceite:**
- Botão de avanço de fase visível apenas para o facilitador.
- Ao avançar, todos os participantes recebem o evento `phase.changed` em tempo real.
- O facilitador pode avançar mesmo antes do cronômetro zerar.
- Confirmação obrigatória antes de avançar para a fase de encerramento.
- Facilitador pode pausar e retomar o cronômetro em qualquer fase cronometrada. Estado de pausa refletido para todos via `timer.paused` e `timer.resumed`.

---

**US-04 — Configurar dot voting**
> Como facilitador, quero definir o número de votos por participante antes da fase de votação, para garantir que a priorização seja forçada.

**Critérios de aceite:**
- Configuração disponível no lobby ou antes da fase de votação.
- Valor padrão: 3 votos por participante.
- Intervalo permitido: 1 a 10 votos.
- Contador de votos restantes visível para cada participante durante a votação.

---

**US-05 — Encerrar sessão**
> Como facilitador, quero encerrar a sessão e salvar o resultado, para que o time possa consultar o histórico depois.

**Critérios de aceite:**
- Botão de encerramento disponível apenas na fase `actions`.
- Confirmação obrigatória com aviso sobre itens de ação sem responsável.
- Ao encerrar, a sessão muda para `closed` e aparece no dashboard de histórico.

---

**US-07a — Preparar marcos (Facilitador)**
> Como facilitador, quero registrar marcos da sprint antes de iniciar a retrospectiva, para chegar na sessão com contexto organizado.

**Critérios de aceite:**
- Disponível na tela de preparação (`setup`), antes de ativar o lobby.
- Categorias: Conquista, Desafio, Mudança, Reconhecimento, Outro.
- Campo de texto livre para descrição (máx. 500 caracteres).
- Facilitador pode adicionar, editar e excluir marcos durante a preparação.

---

**US-07c — Apresentar marcos no início da sessão**
> Como facilitador, quero apresentar os marcos da sprint que preparei, para alinhar o time sobre eventos importantes antes de revisar as ações pendentes.

**Critérios de aceite:**
- Tela de apresentação dedicada (fase `presentation`) exibindo marcos registrados na preparação.
- Participantes visualizam em tempo real, somente leitura.
- Facilitador controla a navegação entre marcos.
- Botão "Avançar para Check de Ações" disponível apenas para o facilitador.
- Se não houver marcos, fase é automaticamente pulada.
- Marcos permanecem visíveis como contexto (barra lateral/topo) durante fases seguintes.

---

**US-09 — Agrupar cards (Facilitador)**
> Como facilitador, quero agrupar cards similares de forma ágil, para eliminar duplicidades antes da votação.

**Critérios de aceite:**
- Apenas o facilitador vê os controles de agrupamento.
- Agrupamento via seleção múltipla: facilitador marca checkboxes nos cards e usa ação "Agrupar selecionados".
- Cards só podem ser agrupados com outros da **mesma coluna**.
- Cards agrupados são exibidos aninhados sob o card pai.
- Facilitador pode desagrupar cards.
- Fase sem cronômetro: facilitador avança manualmente quando terminar.
- Eventos `card.grouped` e `card.ungrouped` transmitidos para todos em tempo real.

---

**US-12 — Conduzir debate focado (Facilitador)**
> Como facilitador, quero conduzir uma discussão estruturada sobre os cards mais votados.

**Critérios de aceite:**
- Tela exibe cards ordenados por número de votos (decrescente).
- Destaque visual para os 3–5 mais votados.
- Facilitador clica em um card para "colocar em foco", sinalizando para todos qual ponto está sendo discutido.
- Apenas o facilitador controla a navegação entre cards em foco.
- Nenhum CRUD ou votação é permitido nesta fase (somente leitura).
- Cronômetro visível com controles de pausa/estender/avançar.

---

### Participante

**US-06 — Verificar ações anteriores**
> Como participante, quero ver as ações da retro anterior no início da sessão, para que o time avalie o que foi cumprido antes de refletir sobre a nova sprint.

**Critérios de aceite:**
- Fase opcional configurável pelo facilitador.
- Exibe a lista de action items da última retro **com o mesmo `team_key`** que esteja `closed`.
- Participantes podem marcar cada ação como "Concluída", "Em andamento" ou "Não iniciada".
- O status é salvo e visível no histórico da retro anterior.

---

**US-07b — Visualizar marcos (Participante)**
> Como participante, quero ver os marcos da sprint registrados pelo facilitador, para ter contexto compartilhado durante a reflexão 4L.

**Critérios de aceite:**
- Marcos visíveis em todas as fases (exceto lobby) como barra lateral ou topo colapsável.
- Exibidos em ordem cronológica de criação.
- Apenas leitura para participantes.

---

**US-08 — Adicionar card ao board**
> Como participante, quero adicionar um card em qualquer coluna do board 4L, para registrar minha percepção sobre a sprint.

**Critérios de aceite:**
- Quatro colunas disponíveis: Liked, Loathed, Longed For, Learned.
- Card criado aparece para todos em tempo real (evento `card.created`).
- Somente o autor pode editar ou excluir o próprio card.
- Limite de 500 caracteres por card.

---

**US-10 — Votar em cards prioritários**
> Como participante, quero distribuir meus votos entre os cards das colunas "Loathed" e "Longed For".

**Critérios de aceite:**
- Apenas cards das colunas `loathed` e `longed` são votáveis.
- Número de votos por participante definido pelo facilitador (padrão: 3, intervalo: 1–10).
- **Máximo de 1 voto por card por participante.**
- Contador de votos restantes visível e atualizado em tempo real.
- Voto pode ser desfeito enquanto a fase de votação estiver aberta.
- Não é possível votar no próprio card.
- Eventos `vote.cast` e `vote.revoked` transmitidos para todos em tempo real.

---

**US-11 — Registrar item de ação**
> Como participante, quero registrar um item de ação vinculado a um card, para que o que foi decidido na retro vire uma tarefa rastreável.

**Critérios de aceite:**
- Campos obrigatórios: descrição e responsável (dropdown de participantes).
- Campo opcional: prazo (date picker).
- Ação pode ser vinculada a um card específico ou criada de forma independente.

---

## 5. Fluxo da Sessão de Retrospectiva

| Fase | Duração padrão | Quem pode editar | Descrição |
|---|---|---|---|
| Preparação (offline) | — | Facilitador | Cria sessão, define `team_key`, registra marcos. Sessão em `setup`. |
| Lobby | — | Facilitador (controle) | Gera link de convite. Participantes chegam e se autenticam. |
| Apresentação | — (sem timer) | Facilitador (fala) / Todos (veem) | Facilitador apresenta marcos. Se não houver marcos, fase é pulada. |
| Check de ações | 5 min | Todos | Revisão dos itens de ação da última retro do mesmo `team_key`. Fase opcional. |
| Board 4L | 10 min | Todos | Reflexão 4 colunas com marcos visíveis como contexto. |
| Agrupamento | Flexível (sem timer) | **Facilitador** | Facilitador agrupa cards duplicados da mesma coluna via seleção múltipla. |
| Votação | 5 min | Todos | Dot voting **apenas nas colunas "Loathed" e "Longed For"**. Máx. 1 voto por card. |
| Debate | 10 min | Todos (leitura) / Facilitador (controle) | Discussão focada nos cards mais votados. |
| Ações | 10 min | Todos | Registro de itens de ação com descrição, responsável e prazo. |
| Encerrado | — | Facilitador | Sessão salva no histórico. |

---

## 6. Stack Tecnológica

### 6.1 Stack de desenvolvimento

| Camada | Tecnologia | Versão | Justificativa |
|---|---|---|---|
| **Backend** | Python + Django | 3.12 / 5.x | Ecossistema maduro; idiomático para agentes de IA |
| **API REST** | Django REST Framework | 3.15+ | Padrão de mercado para APIs Django |
| **WebSocket** | Django Channels + ASGI | 4.x | Solução oficial Django para WebSocket |
| **Servidor ASGI** | Daphne | 4.x | Servidor de referência para Django Channels |
| **Tarefas assíncronas** | Celery + Celery Beat | 5.x | Cronômetro no servidor e tarefas futuras |
| **Channel Layer / Broker** | Redis | 7.x | Backend obrigatório para Django Channels + Celery broker |
| **Banco de dados** | PostgreSQL | 16 | UUID nativo; comportamento previsível com Django ORM |
| **Autenticação** | django-allauth | 0.6x+ | Auth local (e-mail/senha) + OAuth opcional (Google, GitHub) |
| **Frontend** | Nuxt 3 (Vue 3) | 3.x | Framework Vue 3 moderno com excelente suporte SPA/SSR |
| **CSS** | Tailwind CSS | 3.x | Utility-first; configurável; alta cobertura em agentes de IA |
| **Containerização local** | Docker + docker-compose | — | Ambiente local reproduzível (apenas desenvolvimento) |

### 6.2 Infraestrutura (MVP Zero-Cost)

| Serviço | Plataforma | Tier gratuito | O que hospeda |
|---|---|---|---|
| **Backend Django + Daphne** | [Fly.io](https://fly.io) | Até 3 VMs compartilhadas (256 MB RAM cada) | Aplicação Django com ASGI (Daphne) |
| **Worker Celery + Beat** | Fly.io (segunda VM) | Mesmo tier gratuito | Processamento assíncrono do cronômetro |
| **PostgreSQL** | [Neon](https://neon.tech) | 0.5 GB armazenamento, conexões ilimitadas | Banco de dados principal |
| **Redis** | [Upstash](https://upstash.com) | Até 256 MB, 1000 conexões simultâneas | Channel Layer (WebSocket) + Celery broker |
| **Frontend SPA** | [Vercel](https://vercel.com) | 100 GB banda, builds ilimitados | Nuxt 3 static/SPA |
| **OAuth (opcional)** | Google Cloud Console / GitHub | Gratuito (credenciais OAuth) | OAuth opcional via django-allauth |

### 6.3 Arquitetura de deployment

```
[Frontend Nuxt SPA] (Vercel)
        |
[Fly.io App (Django + Daphne)] --> [Neon PostgreSQL]
        |                           [Upstash Redis]
[Fly.io Worker (Celery + Celery Beat)]

Ambiente de desenvolvimento: docker-compose com PostgreSQL local, Redis local
```

### 6.4 Limitações do tier gratuito e mitigação

| Limitação | Impacto | Mitigação |
|---|---|---|
| **Fly.io: 256 MB RAM por VM** | Memória pode ser apertada com 30 conexões simultâneas | Executar worker no mesmo container; monitorar. Se necessário, migrar para Oracle Cloud Free (24 GB RAM) |
| **Cold start após inatividade** | Primeiro acesso pode levar 2–5 segundos | Facilitador acessa a aplicação minutos antes da retro ("aquecimento") |
| **Neon: 0.5 GB armazenamento** | Histórico de várias retros pode consumir espaço | ~100 KB/retro × 24 retros em 60 dias < 5 MB. Sobra espaço |
| **Upstash: 256 MB Redis** | Mensagens WebSocket e tarefas Celery compartilham memória | Volume baixo para times pequenos. Configurar TTL em chaves expiradas |

### 6.5 Estrutura de repositórios

```
retroapp4l-backend/        # Django — API REST + WebSocket
retroapp4l-frontend/       # Nuxt 3 + Tailwind CSS — SPA
```

### 6.6 Estrutura de apps Django (imutável após Sprint 1)

```
retroapp4l/
├── config/              # settings, urls, asgi, wsgi
├── apps/
│   ├── users/           # Model User, OAuth callback, autenticação
│   ├── retrospectives/  # Models Retrospective, Participant, Milestone, AccessLog, fases
│   ├── cards/           # Models Card, CardVote, agrupamento
│   ├── actions/         # Model ActionItem, check de ações
│   └── realtime/        # Consumers WebSocket, eventos, Channel Groups
├── tasks/               # Celery tasks (sync_timer, etc.)
└── tests/               # Espelha a estrutura de apps/
```

---

## 7. Design System

> **Instrução para o agente de IA:** esta seção é a fonte de verdade para todas as decisões visuais do frontend. Nenhuma cor, fonte, espaçamento ou componente deve ser inventado. Se não está aqui, registre no handoff para validação do Tech Lead antes de prosseguir.

### 7.1 Visão geral

O RetroApp 4L usa **Tailwind CSS** como único sistema de estilos. Todas as decisões de design são expressas via classes utilitárias do Tailwind e uma configuração de tema customizada definida em `tailwind.config.ts`.

**Princípios norteadores:**
- Clareza acima de decoração. Todo elemento visual deve servir a um propósito funcional.
- Consistência via tokens. Nunca usar valores hex arbitrários — sempre usar tokens do tema Tailwind.
- Responsivo por padrão. Todos os layouts devem funcionar em desktop 1280px+ (primário) e tablet 768px (secundário).

### 7.2 Tipografia

- **Fonte:** Inter (Google Fonts). Pesos: 400, 500, 600, 700.
- **Import:** `@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap')`
- **Headings:** sempre `font-semibold` (600).
- **Tom de voz:** inglês, segunda pessoa informal. Sentence case em labels e botões. Erros são factuais, não dramáticos.

**Escala de tipo:**

| Classe Tailwind | Tamanho | Uso no RetroApp |
|---|---|---|
| `text-2xl font-semibold` | 24px/600 | Título da retrospectiva, nome da sprint |
| `text-xl font-semibold` | 20px/600 | Título de coluna (Liked, Loathed...) |
| `text-lg font-semibold` | 18px/600 | Título de seção (Presentation, Discussion) |
| `text-base font-normal` | 16px/400 | Corpo de texto, descrições |
| `text-sm font-medium` | 14px/500 | Labels de campos, texto de card |
| `text-sm font-normal` | 14px/400 | Texto secundário, metadados de card |
| `text-xs font-semibold` | 12px/600 | Chips de fase, badges de votação |
| `text-xs font-normal` | 12px/400 | Timestamps, texto terciário |

### 7.3 Paleta de cores

Definida em `tailwind.config.ts` sob `theme.extend.colors`. Nunca usar valores hex arbitrários inline.

```typescript
// tailwind.config.ts — extend.colors
colors: {
  brand: {
    50:  '#eff6ff',
    100: '#dbeafe',
    500: '#3b82f6',
    600: '#2563eb',
    700: '#1d4ed8',
  },
  success: {
    50:  '#f0fdf4',
    500: '#22c55e',
    600: '#16a34a',
  },
  warning: {
    50:  '#fff7ed',
    500: '#f97316',
    600: '#ea580c',
  },
  danger: {
    50:  '#fef2f2',
    500: '#ef4444',
    600: '#dc2626',
  },
}
```

**Uso semântico:**

| Token | Uso |
|---|---|
| `brand-500` | Ações primárias, fase ativa, cronômetro, links |
| `brand-600` | Hover de botão primário |
| `brand-700` | Pressed de botão primário |
| `slate-900` | Texto primário |
| `slate-600` | Texto secundário |
| `slate-400` | Texto terciário, placeholders |
| `slate-300` | Texto e bordas desabilitados |
| `slate-50` | Backgrounds secundários |
| `success-600` | Status "Done" em action items |
| `warning-500` | Status "In Progress"; coluna Loathed |
| `danger-500` | Erros, validações, status crítico |

**Mapeamento de cores por coluna do board 4L:**

| Coluna | Cor do header | Cor do badge |
|---|---|---|
| Liked (Loved) | `success-600` | `success-50` |
| Loathed | `warning-500` | `warning-50` |
| Longed For | `brand-500` | `brand-50` |
| Learned | `slate-600` | `slate-50` |

### 7.4 Espaçamento

Escala 4px-base do Tailwind. Sempre usar utilitários de espaçamento — nunca valores arbitrários.

| Tailwind | Valor | Uso típico no RetroApp |
|---|---|---|
| `gap-2` / `p-2` | 8px | Gap entre ícone e label; padding interno de chip |
| `gap-3` / `p-3` | 12px | Gap interno de campo de formulário |
| `gap-4` / `p-4` | 16px | Padding de card; gap entre cards na coluna |
| `gap-6` / `p-6` | 24px | Separador entre seções; padding mobile |
| `gap-8` / `p-8` | 32px | Padding horizontal desktop |
| `gap-10` / `p-10` | 40px | Padding vertical de seção desktop |

### 7.5 Bordas, raios e sombras

**Border radius:**

| Tailwind | Valor | Uso no RetroApp |
|---|---|---|
| `rounded` | 4px | Chips de fase, badges de voto |
| `rounded-lg` | 8px | Inputs, cards de retro |
| `rounded-xl` | 12px | Modais |
| `rounded-2xl` | 16px | Cards maiores, painéis |
| `rounded-full` | 999px | Avatars, pills de participante |

**Sombras:**

| Tailwind | Uso no RetroApp |
|---|---|
| `shadow-sm` | Cards de retro (estado normal) |
| `shadow-md` | Coluna do board em hover; card em hover |
| `shadow-lg` | Modais |
| `shadow-xl` | Dropdowns |

### 7.6 Estados de interação

Implementar rigorosamente com variantes Tailwind — não inventar hover/focus customizados:

| Estado | Regra |
|---|---|
| **Hover (botão sólido)** | `hover:bg-brand-600` |
| **Pressed (botão sólido)** | `active:bg-brand-700` |
| **Hover (ghost/outline)** | `hover:bg-slate-100` |
| **Disabled** | `disabled:bg-slate-100 disabled:text-slate-300 disabled:cursor-not-allowed` |
| **Focus** | `focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-black` |

### 7.7 Iconografia

- **Biblioteca:** Heroicons (licença MIT, companion oficial do Tailwind)
- **Pacote:** `@heroicons/vue` (`npm install @heroicons/vue`)
- **Variante:** outline preferido; solid para estados ativos/preenchidos
- **Tamanho:** `w-5 h-5` (20px) padrão; `w-4 h-4` (16px) para ícones inline
- **Posição em botões:** ícone à esquerda com `mr-2`; ícone à direita com `ml-2`

**Ícones definidos para o RetroApp:**

| Elemento | Heroicon |
|---|---|
| Criar retrospectiva | `PlusCircleIcon` |
| Copiar link de convite | `LinkIcon` |
| Avançar fase | `ArrowRightCircleIcon` |
| Cronômetro | `ClockIcon` |
| Pausar cronômetro | `PauseCircleIcon` |
| Retomar cronômetro | `PlayCircleIcon` |
| Card — Liked | `HandThumbUpIcon` |
| Card — Loathed | `HandThumbDownIcon` |
| Card — Longed For | `ClockIcon` |
| Card — Learned | `LightBulbIcon` |
| Marco | `FlagIcon` |
| Votação | `CircleStackIcon` (pequeno) |
| Item de ação | `CheckCircleIcon` |
| Participante online | `UserCircleIcon` (com dot verde) |
| Editar card | `PencilIcon` |
| Excluir card | `TrashIcon` |
| Agrupar card | `ArrowsPointingInIcon` |
| Desagrupar card | `ArrowsPointingOutIcon` |
| Card em foco (debate) | `ViewfinderCircleIcon` |
| Encerrar sessão | `LockClosedIcon` |
| Permitir entrada | `UserPlusIcon` |
| Link bloqueado | `NoSymbolIcon` |

### 7.8 Componentes UI específicos do RetroApp

#### RetroCard

```
┌─────────────────────────────────┐
│  [avatar 24px] Nome · timestamp │  ← text-xs text-slate-400
│                                 │
│  Conteúdo do card               │  ← text-sm font-medium text-slate-900
│                                 │
│  [✎] [🗑] · [● 3 votos]        │  ← Heroicons outline, text-xs
│  [☐] (checkbox agrupamento)     │  ← visível apenas para facilitador
└─────────────────────────────────┘
```

Classes Tailwind: `bg-white border border-slate-100 rounded-lg p-4 shadow-sm hover:shadow-md transition-shadow duration-150`

- Checkbox de agrupamento visível apenas na fase de agrupamento e apenas para o facilitador
- Ícone de voto visível apenas para cards `loathed` e `longed` na fase de votação
- Indicador "Seu card — não votável" em cards do próprio autor durante votação

#### MilestoneCard

```
┌─────────────────────────────────┐
│  🏆 Conquista                   │  ← text-xs font-semibold, cor da categoria
│                                 │
│  Deploy sem incidentes na sexta │  ← text-sm font-medium text-slate-900
│                                 │
│  Facilitador · timestamp        │  ← text-xs text-slate-400
└─────────────────────────────────┘
```

Classes Tailwind: `bg-white border border-slate-100 rounded-lg p-4`

#### PhaseChip (chip de fase ativa)

```
[ ● Fase atual  10:00 ]
```

Classes Tailwind: `bg-brand-50 text-brand-500 text-xs font-semibold rounded px-2 py-1`

#### VoteBadge (contador de votos no card)

```
[ ● 5 ]
```

Classes Tailwind: `text-brand-500 text-xs font-semibold`. Votos próprios: `bg-brand-50 rounded px-1`

#### TimerDisplay (cronômetro)

```
[ ⏱ 08:42 ]  [ ⏸ ]  [ ▶ ]
```

- Normal: `text-xl font-semibold text-slate-900`
- Alerta (< 60s): `text-warning-500`
- Crítico (< 30s): `text-danger-500`
- Transição: `transition-colors duration-150`
- Botões de pausa/retomar visíveis apenas para facilitador

#### ParticipantPanel (painel de participantes)

```
┌─────────────────────────────────────────────────┐
│  Participants (3 online)                         │
│                                                 │
│  ● Ana (online)                                 │
│  ● Bruno (online)                               │
│  ● Carol (online)                               │
│                                                 │
│  ─────────────────────────────────────────────  │
│  🔒 Invite link: BLOCKED                        │
│  Session has already started.                   │
│                                                 │
│  [Allow new entry]                              │
│                                                 │
│  Access log:                                    │
│  • Ana joined at 14:02                          │
│  • Bruno joined at 14:03                        │
│  • Link reopened at 14:12                       │
│  • Daniel joined at 14:13                       │
│  • Link auto-blocked at 14:13                   │
└─────────────────────────────────────────────────┘
```

- Seção de administração visível apenas para o facilitador
- Status do link atualizado em tempo real

#### MilestoneBar (barra de marcos)

```
┌──────────────────────────────────────────────────┐
│  🏆 Deploy sem incidentes  ⚡ Bug na API  🙌 On-call  [colapsável] │
└──────────────────────────────────────────────────┘
```

Visível durante Board, Agrupamento, Votação, Debate e Ações. Ordenado por `created_at`.

Classes Tailwind: `bg-slate-50 border-b border-slate-100 px-8 py-2 flex gap-4 flex-wrap text-sm`

#### ColumnHeader (cabeçalho de coluna do board)

```
┌────────────────────────────────────┐
│  [ícone]  LIKED              [3]   │
└────────────────────────────────────┘
```

- Background: cor semântica da coluna (ver 7.3)
- Título: `text-xs font-semibold uppercase tracking-wide text-white`
- Contador: `text-xs font-normal text-white/75`
- Border radius: `rounded-t-lg`
- Padding: `px-4 py-2`

#### FocusCard (card em foco no debate)

```
┌───────────────────────────────────────────────┐
│  ⭐ IN FOCUS                                   │
│                                               │
│  Loathed — "API instável na Black Friday"     │
│  ● 8 votos                                    │
│                                               │
│  ───────────────────────────────────────────  │
│  Up next:                                     │
│  • Longed For — "Dashboard de métricas" (5)   │
│  • Loathed — "Review lento" (4)               │
│  [Next card ▶]                                │
└───────────────────────────────────────────────┘
```

Visível apenas durante fase de Debate. Controles de navegação apenas para facilitador.

### 7.9 Layout do board

```
┌──────────────────────────────────────────────────────────────────┐
│  RetroApp 4L   Sprint 42 — Retro    [Fase: Board ⏱ 08:42]       │
│                                     [● Ana] [● Bruno] [● Carol]  │
├──────────────────────────────────────────────────────────────────┤
│  🏆 Deploy  ⚡ Bug API  🙌 Ana on-call              [colapsável] │
├──────────────┬──────────────┬──────────────┬────────────────────┤
│  👍 LIKED    │ 👎 LOATHED   │  ⏰ LONGED   │  💡 LEARNED        │
│  ─────────   │  ──────────  │  ─────────   │  ────────────      │
│  [card]      │  [card]      │  [card]      │  [card]            │
│  [card]      │              │              │  [card]            │
│              │              │              │                    │
│  [+ Add card]                                                   │
└──────────────┴──────────────┴──────────────┴────────────────────┘
```

- Barra de marcos entre header e board
- Padding horizontal: `px-8`
- Gap entre colunas: `gap-4`
- Background do board: `bg-slate-50`

### 7.10 Regras de voz e conteúdo

- Textos de interface em inglês (produto open source global).
- Segunda pessoa informal: "Add a card", "Your remaining votes: 2".
- Sentence case em labels e botões: "Advance phase", "Close session".
- Erros: factuais e diretos. "This field is required." — não "Oops! Something went wrong."
- Sem emoji em superfícies de produto. Heroicons substituem emoji.
- Datas: formato `MMM D, YYYY` ou relativo (`2 days ago`) para timestamps de card.
- Números de votos: sempre inteiros. Sem decimais.

---

## 8. Modelo de Dados

### users_user *(app: users)*

| Campo | Tipo Django | Tipo SQL | Descrição |
|---|---|---|---|
| id | UUIDField (PK) | uuid | |
| name | CharField(200) | varchar(200) | Nome completo |
| email | EmailField (unique) | varchar(254) | E-mail do usuário |
| password | AbstractUser default | varchar | Senha hasheada (auth local) |
| oauth_provider | CharField(50, nullable) | varchar(50) | `google` \| `github` \| null |
| oauth_id | CharField(200, nullable) | varchar(200) | ID do usuário no provedor OAuth |
| avatar_url | URLField (nullable) | varchar(200) | URL do avatar (OAuth ou gravatar) |
| is_active | BooleanField | boolean | Padrão Django |
| created_at | DateTimeField(auto_now_add) | timestamptz | |

> **Nota de auth:** `django-allauth` gerencia tanto contas locais (e-mail/senha) quanto sociais (OAuth). `oauth_provider` e `oauth_id` são preenchidos apenas para usuários OAuth. Usuários locais têm senha definida via hashing padrão do Django (PBKDF2).

### retrospectives_retrospective *(app: retrospectives)*

| Campo | Tipo Django | Tipo SQL | Descrição |
|---|---|---|---|
| id | UUIDField (PK) | uuid | |
| title | CharField(255) | varchar(255) | Título da retrospectiva |
| sprint_name | CharField(100, nullable) | varchar(100) | Nome da sprint |
| team_key | CharField(100) | varchar(100) | Identificador do time (slug). Obrigatório. |
| facilitator | ForeignKey(User) | uuid FK | |
| status | CharField(choices) | varchar(20) | `setup\|lobby\|presentation\|check\|board\|grouping\|voting\|discussion\|actions\|closed` |
| invite_token | UUIDField (unique, nullable) | uuid | Token do link de convite |
| invite_revoked_at | DateTimeField (nullable) | timestamptz | |
| max_votes_per_user | IntegerField (default=3) | integer | |
| skip_check_phase | BooleanField (default=False) | boolean | |
| timer_started_at | DateTimeField (nullable) | timestamptz | |
| timer_paused_at | DateTimeField (nullable) | timestamptz | Se preenchido, cronômetro está pausado |
| timer_duration_seconds | IntegerField (nullable) | integer | |
| created_at | DateTimeField(auto_now_add) | timestamptz | |
| closed_at | DateTimeField (nullable) | timestamptz | |

### retrospectives_milestone *(app: retrospectives)*

| Campo | Tipo Django | Tipo SQL | Descrição |
|---|---|---|---|
| id | UUIDField (PK) | uuid | |
| retrospective | ForeignKey(Retrospective) | uuid FK | |
| author | ForeignKey(User) | uuid FK | Sempre o facilitador |
| category | CharField(choices) | varchar(20) | `achievement\|challenge\|change\|recognition\|other` |
| description | TextField | text | Máx. 500 caracteres |
| created_at | DateTimeField(auto_now_add) | timestamptz | |

### retrospectives_participant *(app: retrospectives)*

| Campo | Tipo Django | Tipo SQL | Descrição |
|---|---|---|---|
| id | UUIDField (PK) | uuid | |
| retrospective | ForeignKey(Retrospective) | uuid FK | |
| user | ForeignKey(User) | uuid FK | |
| votes_remaining | IntegerField | integer | Decrementado a cada `vote.cast` |
| joined_at | DateTimeField(auto_now_add) | timestamptz | |

`unique_together: (retrospective, user)`

### retrospectives_accesslog *(app: retrospectives)*

| Campo | Tipo Django | Tipo SQL | Descrição |
|---|---|---|---|
| id | UUIDField (PK) | uuid | |
| retrospective | ForeignKey(Retrospective) | uuid FK | |
| action | CharField(choices) | varchar(20) | `opened\|closed\|participant_joined` |
| triggered_by | ForeignKey(User, nullable) | uuid FK | Facilitador ou null (sistema) |
| participant | ForeignKey(User, nullable) | uuid FK | Preenchido quando `participant_joined` |
| timestamp | DateTimeField(auto_now_add) | timestamptz | |

### cards_card *(app: cards)*

| Campo | Tipo Django | Tipo SQL | Descrição |
|---|---|---|---|
| id | UUIDField (PK) | uuid | |
| retrospective | ForeignKey(Retrospective) | uuid FK | |
| author | ForeignKey(User) | uuid FK | |
| column | CharField(choices) | varchar(20) | `loved\|loathed\|longed\|learned` |
| content | TextField | text | Máx. 500 caracteres |
| group | ForeignKey('self', nullable) | uuid FK | Card pai do grupo |
| position | IntegerField (default=0) | integer | |
| created_at | DateTimeField(auto_now_add) | timestamptz | |

### cards_cardvote *(app: cards)*

| Campo | Tipo Django | Tipo SQL | Descrição |
|---|---|---|---|
| id | UUIDField (PK) | uuid | |
| card | ForeignKey(Card) | uuid FK | |
| voter | ForeignKey(User) | uuid FK | |
| created_at | DateTimeField(auto_now_add) | timestamptz | |

`unique_together: (card, voter)` — garante máximo 1 voto por card por participante.

### actions_actionitem *(app: actions)*

| Campo | Tipo Django | Tipo SQL | Descrição |
|---|---|---|---|
| id | UUIDField (PK) | uuid | |
| retrospective | ForeignKey(Retrospective) | uuid FK | |
| card | ForeignKey(Card, nullable) | uuid FK | Card de origem |
| description | TextField | text | |
| assignee | ForeignKey(User) | uuid FK | |
| due_date | DateField (nullable) | date | |
| status | CharField(choices) | varchar(20) | `pending\|in_progress\|done` |
| created_at | DateTimeField(auto_now_add) | timestamptz | |

---

## 9. Eventos WebSocket

Canal: `retro_{retrospective_id}` (Django Channels Group)

Autenticação: middleware customizado valida JWT antes de aceitar conexão. Conexões sem token válido recusadas com código 4001.

**Conexão inicial e reconexão:**
- Ao conectar, novo participante (sem registro em `Participant`) recebe `session.snapshot` com estado completo da sessão.
- Participante existente em reconexão recebe `session.snapshot` para ressincronizar.
- Reconexão é sempre permitida independentemente do status do link de convite.

| Evento | Direção | Payload mínimo | Descrição |
|---|---|---|---|
| `session.snapshot` | Server → Client | `{phase, timer, cards[], votes[], milestones[], participants[], action_items[]}` | Snapshot completo para novo participante ou reconexão |
| `card.created` | Server → Clients | `{card}` | Novo card criado |
| `card.updated` | Server → Clients | `{card_id, content}` | Card editado |
| `card.deleted` | Server → Clients | `{card_id}` | Card removido |
| `card.grouped` | Server → Clients | `{card_id, group_id}` | Cards agrupados |
| `card.ungrouped` | Server → Clients | `{card_id, previous_group_id}` | Card desagrupado |
| `vote.cast` | Server → Clients | `{card_id, voter_id, votes_remaining}` | Voto registrado |
| `vote.revoked` | Server → Clients | `{card_id, voter_id, votes_remaining}` | Voto desfeito |
| `milestone.created` | Server → Clients | `{milestone}` | Marco registrado |
| `action.check_updated` | Server → Clients | `{action_id, status}` | Status de ação anterior atualizado |
| `phase.changed` | Server → Clients | `{phase, timer_duration_seconds}` | Facilitador avançou fase |
| `timer.sync` | Server → Clients | `{seconds_remaining}` | Segundos restantes (a cada 5s) |
| `timer.paused` | Server → Clients | `{seconds_remaining}` | Cronômetro pausado |
| `timer.resumed` | Server → Clients | `{seconds_remaining}` | Cronômetro retomado |
| `timer.expired` | Server → Clients | `{phase}` | Cronômetro zerou |
| `participant.joined` | Server → Clients | `{user_id, name, avatar_url}` | Novo participante (durante lobby) |
| `participant.joined_late` | Server → Clients | `{user_id, name, avatar_url}` | Novo participante entrou após lobby |
| `participant.left` | Server → Clients | `{user_id}` | Participante saiu |

---

## 10. Requisitos Funcionais

| # | Módulo | US | Descrição | Prioridade |
|---|---|---|---|---|
| RF-01 | Autenticação | — | Auth local (e-mail + senha) via `django-allauth`; OAuth opcional (Google, GitHub); lista de domínios permitidos configurável via `ALLOWED_EMAIL_DOMAINS` | Must Have |
| RF-02 | Sessão | US-01 | Facilitador cria sessão com `team_key` e nome da sprint; sessão inicia em `setup` | Must Have |
| RF-03 | Sessão | US-02, US-02b | Participante acessa via link de convite; link bloqueado após lobby; facilitador pode reabrir temporariamente | Must Have |
| RF-04 | Fases | US-03 | Facilitador avança fases manualmente; pausa e retoma cronômetro | Must Have |
| RF-05 | Cronômetro | — | Cronômetro no servidor via Celery Beat; sincronizado via `timer.sync` a cada 5s; suporte a pausa | Must Have |
| RF-06 | Marcos | US-07a, US-07c | Facilitador prepara marcos offline; apresenta marcos no início da sessão (fase `presentation`) | Must Have |
| RF-07 | Marcos | US-07b | Marcos visíveis como contexto durante toda a sessão (barra colapsável) | Must Have |
| RF-08 | Check | US-06 | Fase opcional de revisão de action items da retro anterior do mesmo `team_key` | Must Have |
| RF-09 | Board 4L | US-08 | Board com 4 colunas em tempo real; cards com limite de 500 caracteres | Must Have |
| RF-10 | Cards | US-08 | CRUD de cards; somente o autor pode editar/excluir o próprio card | Must Have |
| RF-11 | Agrupamento | US-09 | Facilitador agrupa cards da mesma coluna via seleção múltipla | Must Have |
| RF-12 | Votação | US-04, US-10 | Dot voting restrito às colunas "Loathed" e "Longed For"; limite de 1 voto por card por participante | Must Have |
| RF-13 | Debate | US-12 | Fase de debate com cards ordenados por votos e controle de "card em foco" pelo facilitador | Must Have |
| RF-14 | Ações | US-11 | Registrar itens de ação com descrição, responsável e prazo | Must Have |
| RF-15 | Histórico | US-05 | Sessões encerradas no dashboard com status dos action items | Must Have |
| RF-16 | Presença | — | Lista de participantes online visível em tempo real; painel de controle de entrada | Should Have |
| RF-17 | Som | — | Alerta sonoro ao final do cronômetro (Web Audio API) | Should Have |

---

## 11. Requisitos Não Funcionais

### 11.1 Performance
- Latência WebSocket: < 200ms em rede interna.
- Operações de leitura crítica da API REST: < 300ms.
- `timer.sync` emitido a cada 5s. Frontend deve interpolar contagem regressiva localmente a cada 1s e corrigir com `timer.sync`.
- `session.snapshot` para novos participantes enviado em < 1s.

### 11.2 Segurança
- Conexões WebSocket autenticadas via JWT (`AuthMiddlewareStack`).
- Link de convite UUID v4; revogável manualmente; bloqueado automaticamente após lobby.
- Lista de domínios permitidos opcional via variável de ambiente `ALLOWED_EMAIL_DOMAINS`. Se vazia, todos os domínios são aceitos.
- Votos do próprio autor bloqueados na camada de aplicação.
- Ações de agrupamento e avanço de fase verificam `request.user == retrospective.facilitator`.
- Nenhum endpoint acessível sem autenticação (`IsAuthenticated` como permissão global padrão).
- Senhas armazenadas com hashing PBKDF2 padrão do Django.

### 11.3 Disponibilidade
- MVP para uso de times pequenos; sem SLA formal.
- **Cold starts:** Aplicação pode hibernar após inatividade no tier gratuito. Facilitadores devem acessar a aplicação minutos antes da retro para "aquecer" o serviço. Tempo de cold start típico: 2–5 segundos.

### 11.4 Escalabilidade
- Django Channels + Redis Channel Layer (Upstash) suporta múltiplas instâncias horizontais.
- Celery workers escalam independentemente.
- Até 30 participantes simultâneos por sessão no MVP.

### 11.5 Qualidade de código
- Cobertura de testes: mínimo 80% nas apps `retrospectives`, `cards` e `actions`.
- Linting: `ruff` para Python, `eslint` + `prettier` para frontend Nuxt.
- Cada sprint passa em `python manage.py test` sem falhas antes do handoff.

### 11.6 Acessibilidade e UI
- Todos os componentes devem respeitar `:focus-visible` com `focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-black`.
- Contraste mínimo AA entre texto e background.
- Animações limitadas a `color`, `background` e `opacity` com `duration-150`. Sem bounces ou transforms de layout.
- Alerta sonoro do cronômetro usa Web Audio API com tons senoidais.

---

## 12. Modelo de Sprints e Documento de Handoff

### 12.1 Por que o handoff é crítico

O agente de IA não retém memória entre sessões. O handoff é o único mecanismo que conecta sprints. Um handoff vago produz código inconsistente. Um handoff preciso produz continuidade previsível.

**Regra:** se uma decisão técnica não está no handoff, ela não existe para a próxima sessão.

### 12.2 Estrutura obrigatória do documento de handoff

```markdown
# Sprint N — Handoff

## Estado do repositório
- Branch: main (ou feature/sprint-N)
- Último commit: <hash> — <mensagem>
- Migrations pendentes: sim/não

## O que foi implementado e está funcionando
- [lista precisa, com referência a arquivos e funções]

## O que foi iniciado e não concluído
- [lista com motivo e ponto exato de parada]

## Decisões técnicas tomadas nesta sprint
- [decisão] → [motivo] → [arquivo afetado]

## Padrões estabelecidos que devem ser seguidos
- [ex: "Todos os consumers herdam de BaseRetroConsumer em realtime/base.py"]

## Próxima sprint: o que deve ser feito
- [lista ordenada, sem ambiguidade, com critério de done]

## Comandos para retomar
- docker-compose up -d
- python manage.py migrate
- python manage.py test
```

### 12.3 Planejamento de sprints

| Sprint | Foco | Entregáveis | Handoff |
|---|---|---|---|
| 1 | Fundação | Estrutura do projeto, Docker, PostgreSQL, migrations iniciais (inclui `team_key`, `timer_paused_at`, `Milestone`, `AccessLog`, status choices expandidos), auth local + OAuth opcional (`django-allauth`), criação de sessão com `team_key` | `SPRINT_1_HANDOFF.md` |
| 2 | Core Real-time | Django Channels + ASGI (Daphne), consumers WebSocket (inclui `session.snapshot`, `timer.paused`, `timer.resumed`, `card.ungrouped`), máquina de estados de fases (10 estados), cronômetro com pausa via Celery Beat, distinção entre nova entrada e reconexão | `SPRINT_2_HANDOFF.md` |
| 3 | Board 4L + Marcos | CRUD de cards com broadcast, modelo `Milestone`, preparação de marcos, apresentação de marcos, `MilestoneBar`, board em tempo real com marcos visíveis | `SPRINT_3_HANDOFF.md` |
| 4 | Agrupamento + Votação | Agrupamento por seleção múltipla (facilitador), dot voting restrito a `loathed`/`longed`, regra de 1 voto/card/pessoa, `vote.revoked` | `SPRINT_4_HANDOFF.md` |
| 5 | Fechamento do ciclo | Check de ações anteriores (por `team_key`), action items com status, fase de Debate com card em foco, encerramento, dashboard de histórico | `SPRINT_5_HANDOFF.md` |
| 6 | Frontend | Setup Nuxt 3 + Tailwind CSS, implementação de todas as telas e componentes seguindo seção 7 do PRD, alerta sonoro do cronômetro | `SPRINT_6_HANDOFF.md` |
| 7 | Polish + Qualidade | Painel de controle de entrada (bloqueio/reativação pós-lobby), presença em tempo real, testes E2E, cobertura ≥ 80%, acessibilidade | `SPRINT_7_HANDOFF.md` |
| 8 | Integrações (futuro) | Exportação para rastreadores externos (Linear, GitHub Issues), PDF/CSV, analytics | — |

> **Premissa de tempo:** cada sprint é uma sessão do agente de IA sem limite de tempo de programação. O Tech Lead reserva 2–4h por sprint para revisão, validação e assinatura do handoff.

### 12.4 Prompt de inicialização de sprint

```
Você é o desenvolvedor do RetroApp 4L, uma plataforma open source de retrospectivas ágeis.

Leia o arquivo SPRINT_N_HANDOFF.md na raiz do repositório.
Ele contém o estado atual do projeto e exatamente o que deve ser feito nesta sprint.

Siga os padrões estabelecidos nas sprints anteriores.
Para o frontend, aplique rigorosamente o design system descrito na seção 7 do PRD:
classes utilitárias do Tailwind CSS, fonte Inter, tokens de cor do tailwind.config.ts,
escala de espaçamento 4px, componentes definidos.

Ao finalizar, gere o rascunho do SPRINT_(N+1)_HANDOFF.md seguindo a estrutura definida no PRD.
Não tome decisões arquiteturais ou visuais não previstas no PRD sem registrar explicitamente
no handoff para validação do Tech Lead.
```

---

## 13. Decisões Registradas e Trade-offs

### 13.1 Django + PostgreSQL vs. outras opções
Python/Django escolhido pela alta cobertura nos dados de treinamento de agentes de IA para padrões DRF + Django Channels. PostgreSQL por UUID nativo e comportamento previsível com o ORM Django.

### 13.2 Django Channels vs. solução gerenciada
Self-hosted, sem custo adicional. Redis já necessário para Celery — não adiciona nova peça de infra.

**Trade-off:** configuração ASGI (Daphne + Channels) mais complexa que WSGI tradicional. Sprint 2 é o maior risco técnico.

### 13.3 Celery Beat para cronômetro vs. asyncio no consumer
Celery Beat é explícito, testável e auditável entre sessões do agente de IA. Asyncio acoplado ao consumer é difícil de testar isoladamente e de rastrear entre sessões.

**Trade-off:** adiciona worker Celery e Beat scheduler no docker-compose e na VM de produção.

### 13.4 Nuxt 3 + Tailwind CSS para o frontend
Nuxt 3 mantido como framework Vue 3 moderno e amplamente suportado. Tailwind CSS substitui o design system proprietário anterior — licença MIT, excelente documentação e alta cobertura nos dados de treinamento de agentes de IA, reduzindo o risco do agente inventar padrões inexistentes.

**Trade-off:** sem biblioteca de componentes (como Radix ou Headless UI), mais trabalho de acessibilidade de baixo nível em componentes interativos (dropdowns, modais). Tech Lead pode adicionar `@headlessui/vue` se isso se tornar um gargalo na Sprint 6.

### 13.5 Auth local + OAuth opcional
Tornar a auth local o método primário remove a dependência de qualquer provedor OAuth, tornando o projeto genuinamente portátil para qualquer time. Lista de domínios permitidos configurável via variável de ambiente `ALLOWED_EMAIL_DOMAINS` substitui a restrição de domínio hard-coded.

### 13.6 `team_key` como string vs. entidade Team completa
String simples permite agrupamento imediato no MVP sem adicionar entidade de time, convites de membros ou permissões complexas. Suficiente para o check de ações e dashboard de histórico. Evolução futura pode migrar para entidade `Team` com chave estrangeira.

### 13.7 Milestone separado de Card
Marcos têm propósito distinto (aquecimento e contexto, criados offline pelo facilitador) e ciclo de vida diferente (não votados, não agrupados). Modelo separado evita condicionais `if card.is_milestone` e previne bugs de domínio.

### 13.8 Agrupamento restrito ao facilitador
Elimina conflitos de concorrência em tempo real (dois participantes agrupando o mesmo card). Seleção múltipla mantém agilidade para o facilitador. Drag-and-drop colaborativo fica para fase 2.

### 13.9 Votação restrita a "Loathed" e "Longed For"
Foca priorização nas colunas que geram ações de melhoria. As colunas "Liked" e "Learned" são para celebração e registro de conhecimento — não precisam de priorização forçada. Reduz dispersão de votos e torna a fase mais objetiva.

### 13.10 1 voto por card por participante
Força distribuição de votos e evita que um único card concentre todos os votos de um participante — o que derrotaria o propósito de priorização do dot voting. Regra fixa, sem toggle, para manter simplicidade.

### 13.11 Bloqueio de entrada pós-lobby
Preserva integridade do processo (todos compartilham mesmo histórico). Facilitador pode reabrir temporariamente para exceções. Reconexão de participante existente é sempre permitida.

### 13.12 Infraestrutura gratuita (Fly.io + Neon + Upstash + Vercel)
Permite MVP operar com R$ 0,00 de custo durante os 60 dias de avaliação. Trade-offs: cold starts (mitigado com aquecimento), limites de armazenamento e memória (folgados para o volume de uso esperado). Tech Lead pode migrar para Oracle Cloud Free se limites se mostrarem insuficientes.

### 13.13 Handoff como artefato de primeiro nível
Ausência ou imprecisão do handoff equivale a bug crítico — impede a sprint seguinte ou produz regressão silenciosa.

---

*RetroApp 4L PRD v7.0 — Projeto Open Source — Licença MIT*
*Contribuições são bem-vindas. Veja CONTRIBUTING.md para diretrizes.*
