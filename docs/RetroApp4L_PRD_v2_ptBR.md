# RetroApp4L — Documento de Requisitos do Produto (PRD)

**Versão:** 2.0 — MVP (Infraestrutura Zero-Cost)
**Data:** Maio 2026
**Licença:** MIT
**Status:** Reescrita open-source — consolidado após revisão de arquitetura
**Audiência:** Mantenedores (revisão/infra/deploy), Agentes IA (execução de desenvolvimento), Contribuidores

> **Changelog v2.0:**
> - Reescrito como projeto open-source sob licença MIT
> - Removidas todas as referências proprietárias e integrações vendor-specific
> - Design system migrado de framework proprietário para **Tailwind CSS**
> - Autenticação alterada para **local (email/senha) + provedores OAuth opcionais**
> - Stack frontend simplificada para **Nuxt 3 + Tailwind CSS** (sem dependência de Quasar)
> - Campo de rastreador externo generalizado de vendor único para qualquer URL
> - Modelo de desenvolvedor generalizado para **qualquer agente IA de código** (Claude Code, Cursor, Copilot, etc.)
> - Infraestrutura permanece **zero-cost** usando tiers gratuitos de plataformas cloud

---

## 1. Visão Geral

O RetroApp4L é uma plataforma web open-source para conduzir retrospectivas de sprint estruturadas na metodologia dos 4 Ls (Liked, Loathed, Longed for, Learned — Gostei, Não Gostei, Aguardei, Aprendi). O produto combina colaboração em tempo real, cronômetro sincronizado e rastreabilidade de itens de ação, fechando o ciclo entre o que é decidido na retro e o que é executado na sprint seguinte.

### 1.1 Problema

- Retrospectivas conduzidas em ferramentas genéricas (Miro, EasyRetro, FigJam) não estão integradas ao fluxo de trabalho do time.
- Itens de ação decididos nas retros raramente se tornam tarefas rastreáveis na ferramenta de gestão de projetos do time.
- Não há mecanismo para verificar, na retro seguinte, se as ações da sprint anterior foram cumpridas.
- Não há histórico centralizado de retrospectivas para acompanhar a evolução do time ciclo a ciclo.

### 1.2 Objetivos do MVP

- Conduzir retrospectivas 4L com colaboração em tempo real (board compartilhado + cronômetro sincronizado).
- Autenticar usuários via credenciais locais (email/senha) com provedores OAuth opcionais (Google, GitHub).
- Permitir ao facilitador convidar membros via link privado.
- Verificar ações da sprint anterior antes de iniciar a reflexão.
- Registrar itens de ação com responsável e prazo, prontos para exportação a qualquer rastreador externo.
- Salvar automaticamente todas as retrospectivas para consulta futura.
- **MVP operar com custo zero de infraestrutura** utilizando tiers gratuitos de plataformas cloud.

### 1.3 Critérios de Sucesso do MVP

O MVP será considerado bem-sucedido se, após 60 dias de uso, os seguintes indicadores forem atingidos:

| Indicador | Meta |
|---|---|
| Adoção | ≥ 80% das retrospectivas do time conduzidas no RetroApp4L |
| Rastreabilidade | ≥ 70% dos itens de ação registrados com responsável e prazo preenchidos |
| Reabertura | ≥ 50% das sessões incluem a verificação de ações da sprint anterior |
| Estabilidade | Zero incidentes de dessincronização de board em produção |
| Satisfação | NPS interno ≥ 7 após pesquisa com facilitadores (mínimo 5 respostas) |
| Custo | Custo total de infraestrutura = R$ 0,00 durante o período MVP |

### 1.4 Fora do Escopo do MVP

- Integração com APIs externas de gestão de projetos (campo reservado no schema; sem integração em runtime).
- Exportação em PDF, CSV ou DOCX.
- Mascaramento de cards durante a fase de escrita.
- Funcionalidades de relatório e analytics de tendências entre sprints.
- Drag-and-drop para agrupamento de cards (fase 2).

---

## 2. Premissas de Desenvolvimento

### 2.1 Modelo de Execução

- **O desenvolvedor é qualquer agente IA de código** (Claude Code, Cursor, Copilot Workspace, Aider, etc.) rodando autonomamente por sessão.
- **O mantenedor (humano)** é responsável por: revisão de código, decisões de infra, configuração de ambiente, deploy, escrita e validação do documento de handoff ao final de cada sprint.
- Agentes IA **não retêm memória entre sessões**. Todo contexto necessário deve estar no documento de handoff. Se não está no handoff, não existe para a próxima sessão.

### 2.2 Consequências Arquiteturais

- **Convenção sobre configuração:** código deve seguir padrões idiomáticos do Django e a abordagem utility-first do Tailwind CSS.
- **Estrutura de arquivos previsível:** definida na Sprint 1 e nunca alterada sem atualização explícita no handoff.
- **Testes como documentação viva:** cada sprint produz testes que descrevem o comportamento implementado.
- **Sem "magia" implícita:** evitar padrões que dependem de estado global ou comportamento implícito difícil de rastrear.

### 2.3 Responsabilidades por Papel

| Responsabilidade | Agente IA | Mantenedor |
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
- Ao acessar o link, o participante deve estar autenticado antes de entrar.
- Após o facilitador iniciar a sessão (status diferente de `lobby`), o link é automaticamente bloqueado para novas entradas.
- Tentativas de entrada com link bloqueado exibem mensagem informativa.

---

**US-02b — Gerenciar entrada de participantes após o início**
> Como facilitador, quero liberar temporariamente o acesso a participantes que não conseguiram entrar antes do início da sessão, para garantir que ninguém seja excluído por atraso.

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
> Como facilitador, quero registrar marcos da sprint antes de iniciar a retrospectiva, para chegar na sessão com contexto organizado e garantir que eventos importantes não sejam esquecidos.

**Critérios de aceite:**
- Disponível na tela de preparação (`setup`), antes de ativar o lobby.
- Categorias: Conquista, Desafio, Mudança, Reconhecimento, Outro.
- Campo de texto livre para descrição (máx. 500 caracteres).
- Facilitador pode adicionar, editar e excluir marcos durante a preparação.
- Marcos são salvos e ficam disponíveis para apresentação.

---

**US-07c — Apresentar marcos no início da sessão**
> Como facilitador, quero apresentar os marcos da sprint que preparei antes da sessão, para alinhar o time sobre eventos importantes antes de revisar as ações pendentes.

**Critérios de aceite:**
- Tela de apresentação dedicada (fase `presentation`) exibindo marcos registrados na preparação.
- Participantes visualizam em tempo real, somente leitura.
- Facilitador controla a navegação entre marcos e pode comentar verbalmente.
- Botão "Avançar para Check de Ações" disponível apenas para o facilitador.
- Se não houver marcos, fase é automaticamente pulada.
- Marcos permanecem visíveis como contexto (barra lateral/topo) durante fases seguintes.

---

**US-09 — Agrupar cards (Facilitador)**
> Como facilitador, quero agrupar cards similares de forma ágil, para eliminar duplicidades antes da votação e focar a discussão.

**Critérios de aceite:**
- Apenas o facilitador vê os controles de agrupamento.
- Agrupamento via seleção múltipla: facilitador marca checkboxes nos cards e usa ação "Agrupar selecionados".
- Cards só podem ser agrupados com outros da **mesma coluna**.
- Cards agrupados são exibidos aninhados sob o card pai.
- Facilitador pode desagrupar cards.
- Fase sem cronômetro: facilitador avança manualmente quando terminar.
- Evento `card.grouped` e `card.ungrouped` transmitidos para todos em tempo real.

---

**US-12 — Conduzir debate focado (Facilitador)**
> Como facilitador, quero conduzir uma discussão estruturada sobre os cards mais votados, para que o time entenda o contexto e gere ideias de ação antes de registrá-las.

**Critérios de aceite:**
- Tela exibe cards ordenados por número de votos (decrescente).
- Destaque visual para os 3–5 mais votados.
- Facilitador clica em um card para "colocar em foco", expandindo-o e sinalizando para todos os participantes qual ponto está sendo discutido.
- Apenas o facilitador controla a navegação entre cards em foco.
- Nenhum CRUD ou votação é permitido nesta fase (somente leitura).
- Cronômetro visível com controles de pausa/estender/avançar.
- Facilitador pode encerrar o debate e avançar para a fase de Ações.

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
- Quatro colunas disponíveis: Gostei, Não Gostei, Aguardei, Aprendi.
- Card criado aparece para todos em tempo real (evento `card.created`).
- Somente o autor pode editar ou excluir o próprio card.
- Limite de 500 caracteres por card.

---

**US-10 — Votar em cards prioritários**
> Como participante, quero distribuir meus votos entre os cards das colunas "Não Gostei" e "Aguardei", para destacar os pontos que mais precisam ser discutidos e resolvidos.

**Critérios de aceite:**
- Apenas cards das colunas `loathed` e `longed` são votáveis. Cards `loved` e `learned` não exibem opção de voto.
- Número de votos por participante definido pelo facilitador (padrão: 3, intervalo: 1–10).
- **Máximo de 1 voto por card por participante.**
- Contador de votos restantes visível e atualizado em tempo real.
- Voto pode ser desfeito enquanto a fase de votação estiver aberta.
- Não é possível votar no próprio card.
- Evento `vote.cast` e `vote.revoked` transmitidos para todos em tempo real.
- Se um participante tiver votos restantes mas não houver cards votáveis disponíveis (ex.: todos os cards restantes são do próprio autor), exibir mensagem informativa e permitir que o facilitador avance de fase.

---

**US-11 — Registrar item de ação**
> Como participante, quero registrar um item de ação vinculado a um card, para que o que foi decidido na retro vire uma tarefa rastreável.

**Critérios de aceite:**
- Campos obrigatórios: descrição e responsável (dropdown de participantes).
- Campo opcional: prazo (date picker).
- Ação pode ser vinculada a um card específico ou criada de forma independente.
- Campo `external_tracker_url` visível como input de URL opcional (para vincular a GitHub Issues, Linear, Trello, etc.).

---

## 5. Fluxo da Sessão de Retrospectiva

| Fase | Duração padrão | Quem pode editar | Descrição |
|---|---|---|---|
| Preparação (offline) | — | Facilitador | Facilitador cria sessão, define `team_key`, registra marcos da sprint. Sessão em `setup`. |
| Lobby | — | Facilitador (controle) | Facilitador gera link de convite. Participantes chegam e são autenticados. |
| Apresentação | — (sem timer) | Facilitador (fala) / Todos (veem) | Facilitador apresenta marcos registrados na preparação. Contexto compartilhado antes da revisão de ações. Se não houver marcos, fase é pulada. |
| Check de ações | 5 min | Todos | Revisão dos itens de ação da última retro do mesmo `team_key`. Participantes marcam status. Fase opcional. |
| Board 4L | 10 min | Todos | Reflexão 4 colunas (Gostei, Não Gostei, Aguardei, Aprendi) com marcos visíveis como contexto. |
| Agrupamento | Flexível (sem timer) | **Facilitador** | Facilitador agrupa cards duplicados da mesma coluna via seleção múltipla. |
| Votação | 5 min | Todos | Dot voting **apenas nas colunas "Não Gostei" e "Aguardei"**. Máx. 1 voto por card por participante. |
| Debate | 10 min | Todos (leitura) / Facilitador (controle) | Discussão focada nos cards mais votados. Facilitador coloca cards "em foco" para guiar a conversa. |
| Ações | 10 min | Todos | Registro de itens de ação com descrição, responsável e prazo. |
| Encerrado | — | Facilitador | Sessão salva no histórico. |

---

## 6. Stack Tecnológica

### 6.1 Stack de Desenvolvimento

| Camada | Tecnologia | Versão | Justificativa |
|---|---|---|---|
| **Backend** | Python + Django | 3.12 / 5.x | Ecossistema maduro; altamente idiomático para agentes IA de código |
| **API REST** | Django REST Framework | 3.15+ | Padrão de mercado para APIs Django |
| **WebSocket** | Django Channels + ASGI | 4.x | Solução oficial Django para WebSocket |
| **Servidor ASGI** | Daphne | 4.x | Servidor de referência para Django Channels |
| **Tarefas assíncronas** | Celery + Celery Beat | 5.x | Cronômetro no servidor e tarefas futuras |
| **Channel Layer / Broker** | Redis | 7.x | Backend obrigatório para Django Channels + Celery broker |
| **Banco de dados** | PostgreSQL | 16 | UUID nativo; comportamento previsível com Django ORM |
| **Autenticação** | django-allauth | 0.6x+ | Auth local (email/senha) + provedores OAuth opcionais (Google, GitHub) |
| **Frontend** | Nuxt 3 (Vue 3) | 3.x | Framework Vue 3 moderno para SPA/SSR |
| **CSS Framework** | Tailwind CSS | 3.x | Utility-first, zero runtime, totalmente customizável via config |
| **Ícones** | Lucide Icons (Vue) | latest | Open-source, tree-shakeable, licença MIT |
| **Dev local** | Docker + docker-compose | — | Ambiente local reproduzível (apenas desenvolvimento) |

### 6.2 Infraestrutura (MVP Zero-Cost)

| Serviço | Plataforma | Tier gratuito | O que hospeda |
|---|---|---|---|
| **Backend Django + Daphne** | [Fly.io](https://fly.io) | Até 3 VMs compartilhadas (256 MB RAM cada), 3 GB armazenamento | Aplicação Django com ASGI (Daphne) |
| **Worker Celery + Beat** | Fly.io (segunda VM) | Mesmo tier gratuito | Processamento assíncrono do cronômetro |
| **PostgreSQL** | [Neon](https://neon.tech) | 0.5 GB armazenamento, conexões ilimitadas | Banco de dados principal |
| **Redis** | [Upstash](https://upstash.com) | Até 256 MB, 1000 conexões simultâneas | Channel Layer (WebSocket) + Celery broker/result backend |
| **Frontend SPA** | [Vercel](https://vercel.com) | 100 GB banda, builds ilimitados | Nuxt 3 static/SPA |
| **OAuth (opcional)** | Google Cloud Console / GitHub | Gratuito (credenciais OAuth) | SSO opcional via django-allauth |

### 6.3 Arquitetura de Deployment

```
[Frontend Nuxt SPA] (Vercel)
        |
[Fly.io App (Django + Daphne)] --> [Neon PostgreSQL]
        |                           [Upstash Redis]
[Fly.io Worker (Celery + Celery Beat)]

Ambiente de desenvolvimento: docker-compose com PostgreSQL local e Redis local
```

**Daphne** como servidor ASGI no mesmo processo Django (configuração padrão). Fly.io permite expor portas HTTP e WebSocket.

**Celery Worker** e **Beat** executam como segunda VM no Fly.io rodando o mesmo código, com comando de worker/beat. Se a memória for apertada, worker pode ser executado no mesmo container que a app durante o MVP.

**Neon** e **Upstash** são serviços externos acessíveis via internet. Latência aceitável para aplicações internas.

### 6.4 Limitações do Tier Gratuito e Mitigação

| Limitação | Impacto | Mitigação |
|---|---|---|
| **Fly.io: 256 MB RAM por VM** | Memória pode ser apertada com 30 conexões simultâneas | Executar worker no mesmo container; monitorar uso. Se necessário, migrar para Oracle Cloud Free (24 GB RAM) |
| **Cold start após inatividade (Fly.io e Vercel)** | Primeiro acesso pode levar 2-5 segundos | Facilitador acessa a aplicação minutos antes da retro ("aquecimento"); aplicação de uso programado, não contínuo |
| **Neon: 0.5 GB armazenamento** | Histórico de várias retros pode consumir espaço | Estimativa: 100 cards/retro × 500 bytes + participantes + ações ≈ 100 KB/retro. Em 60 dias (~24 retros), consumo < 5 MB. Sobra espaço |
| **Upstash: 256 MB Redis** | Mensagens WebSocket e tarefas Celery compartilham memória | Volume baixo de mensagens (timer a cada 5s, eventos de card). Time de 30 pessoas gera tráfego baixo. Configurar TTL de chaves expiradas |

### 6.5 Estrutura de Repositórios

```
retroapp4l-backend/       # Django — API REST + WebSocket
retroapp4l-frontend/      # Nuxt 3 + Tailwind CSS — SPA
```

### 6.6 Estrutura de Apps Django (imutável após Sprint 1)

```
retroapp/
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

## 7. Design System (Tailwind CSS)

> **Instrução para agentes IA:** esta seção é a fonte de verdade para todas as decisões visuais do frontend. Nenhuma cor, fonte, espaçamento ou componente deve ser inventado. Se não está aqui, consulte o mantenedor antes de prosseguir.

### 7.1 Visão Geral

O RetroApp4L usa **Tailwind CSS** como fundação de design, estendido via `tailwind.config.js` com tokens semânticos para as necessidades específicas da aplicação. Nenhum framework UI proprietário é necessário — todos os componentes são construídos com utilitários Tailwind e CSS customizado quando necessário.

**Setup:** Instalar Tailwind CSS via módulo `@nuxtjs/tailwindcss`. Todos os tokens customizados são definidos em `tailwind.config.js`.

### 7.2 Tipografia

- **Fonte:** Inter exclusivamente (carregada via `@fontsource/inter` ou Google Fonts). Pesos: 300, 400, 500, 600, 700.
- **Letter-spacing:** `tracking-tight` (-0.01em) em todo texto exceto captions (tracking normal).
- **Headings:** sempre `font-semibold` (600).
- **Tom de voz:** pt-BR, segunda pessoa informal ("você"). Sem emoji em superfícies de produto. Erros são factuais, não dramáticos. Preparado para i18n.

**Escala de tipo — classes Tailwind a usar no frontend:**

| Nome semântico | Classes Tailwind | Equivalente | Uso no RetroApp4L |
|---|---|---|---|
| `heading-lg` | `text-2xl font-semibold leading-8` | 24px/32px/600 | Título da retrospectiva, nome da sprint |
| `heading-md` | `text-xl font-semibold leading-7` | 20px/28px/600 | Título de coluna do board (Gostei, Não Gostei...) |
| `heading-sm` | `text-lg font-semibold leading-6` | 18px/24px/600 | Título de seção (Apresentação, Debate) |
| `body-md` | `text-base font-normal leading-6` | 16px/24px/400 | Corpo de texto, descrições |
| `body-sm-medium` | `text-sm font-medium leading-5` | 14px/20px/500 | Labels de campos, texto de card |
| `body-sm` | `text-sm font-normal leading-5` | 14px/20px/400 | Texto secundário, metadados de card |
| `label-sm-semibold` | `text-xs font-semibold leading-4` | 12px/16px/600 | Chips de fase, badges de votação |
| `label-sm` | `text-xs font-normal leading-4` | 12px/16px/400 | Timestamps, texto terciário |
| `caption` | `text-[10px] font-normal leading-3 tracking-normal` | 10px/12px/400 | Contadores |

### 7.3 Paleta de Cores

Definir em `tailwind.config.js` em `theme.extend.colors`:

```js
// tailwind.config.js
module.exports = {
  theme: {
    extend: {
      colors: {
        brand: {
          50:  '#eff8ff',
          500: '#009EFB',
          600: '#007BD4',
          700: '#0062AB',
        },
        success: {
          50:  '#ecfdf5',
          600: '#00a46e',
        },
        warning: {
          50:  '#fff7ed',
          500: '#ed7713',
        },
        danger: {
          500: '#f34f4f',
        },
      }
    }
  }
}
```

**Mapeamento semântico de cores (usar estes, não os primitivos diretamente):**

| Token semântico | Classe Tailwind | Valor | Uso |
|---|---|---|---|
| Foreground primário | `text-gray-950` | `#252527` | Todo texto primário |
| Foreground secundário | `text-gray-700` | `#4c4c52` | Texto de suporte |
| Foreground terciário | `text-gray-500` | `#696a71` | Metadados, timestamps |
| Foreground brand | `text-brand-500` | `#009EFB` | Destaques, links |
| Background primário | `bg-white` | `#ffffff` | Background de página e cards |
| Background secundário | `bg-gray-50` | `#f5f5f6` | Background do board, colunas |
| Background terciário | `bg-gray-100` | `#e6e6e7` | Headers de coluna |
| Borda primária | `border-gray-300` | `#adadb3` | Bordas de inputs e cards |
| Borda secundária | `border-gray-200` | `#e5e5e5` | Divisores internos |

**Mapeamento de cores por coluna do board 4L:**

| Coluna | Cor do header | Cor do badge | Justificativa |
|---|---|---|---|
| Gostei (Loved) | `bg-success-600 text-white` | `bg-success-50 text-success-600` | Verde = positivo |
| Não Gostei (Loathed) | `bg-warning-500 text-white` | `bg-warning-50 text-warning-500` | Laranja = atenção |
| Aguardei (Longed for) | `bg-brand-500 text-white` | `bg-brand-50 text-brand-500` | Azul = desejo/expectativa |
| Aprendi (Learned) | `bg-gray-700 text-white` | `bg-gray-50 text-gray-700` | Neutro = conhecimento |

### 7.4 Espaçamento

Escala 4-pt estrita. Usar os tokens de espaçamento nativos do Tailwind:

| Tailwind | Valor | Uso típico no RetroApp4L |
|---|---|---|
| `gap-2` / `p-2` | 8px | Gap entre ícone e label; padding interno de chip |
| `gap-3` / `p-3` | 12px | Gap interno de campo de formulário |
| `gap-4` / `p-4` | 16px | Padding de card; gap entre cards na coluna |
| `gap-6` / `p-6` | 24px | Separador entre seções; padding mobile |
| `gap-8` / `p-8` | 32px | Padding horizontal desktop |
| `gap-10` / `p-10` | 40px | Padding vertical de seção desktop |

### 7.5 Bordas, Raios e Sombras

**Border radius:**

| Tailwind | Valor | Uso no RetroApp4L |
|---|---|---|
| `rounded` | 4px | Chips de fase, badges de voto |
| `rounded-lg` | 8px | Inputs, cards de retro |
| `rounded-xl` | 12px | Modais |
| `rounded-2xl` | 16px | Cards maiores, painéis |
| `rounded-3xl` | 24px | Containers principais |
| `rounded-full` | 999px | Avatar, pills de participante |

**Sombras:**

| Tailwind | Uso no RetroApp4L |
|---|---|
| `shadow-sm` | Cards de retro flutuantes |
| `shadow-md` | Coluna do board em hover |
| `shadow-lg` | Modal de agrupamento |
| `shadow-xl` | Dropdown de responsável em action items |
| `ring-2 ring-brand-500/20` | Campos de formulário com foco |

### 7.6 Estados de Interação

Seguir rigorosamente — não inventar hover/focus customizados:

| Estado | Regra |
|---|---|
| **Hover (botão sólido)** | Step para `-600` (ex: `bg-brand-500` → `hover:bg-brand-600`) |
| **Pressed (botão sólido)** | Step para `-700` (`active:bg-brand-700`) |
| **Hover (flat/outline)** | `hover:bg-brand-50` texto para `-600` |
| **Disabled** | `bg-gray-300` ou `bg-gray-100`; texto `text-gray-300`; `cursor-not-allowed opacity-50` |
| **Focus** | `focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-black` |

### 7.7 Iconografia

- **Biblioteca:** Lucide Icons para Vue (`lucide-vue-next`) — licença MIT, tree-shakeable.
- **Estilo:** variante outline (stroke) por padrão, tamanho consistente de 24px.
- **Posição em botões:** ícone à esquerda com `gap-2`; ícone à direita com `gap-2`.

**Ícones definidos para o RetroApp4L:**

| Elemento | Ícone Lucide |
|---|---|
| Criar retrospectiva | `PlusCircle` |
| Copiar link de convite | `Link` |
| Avançar fase | `ArrowRightCircle` |
| Cronômetro | `Timer` |
| Pausar cronômetro | `PauseCircle` |
| Retomar cronômetro | `PlayCircle` |
| Card — Gostei | `ThumbsUp` |
| Card — Não Gostei | `ThumbsDown` |
| Card — Aguardei | `Clock` |
| Card — Aprendi | `Lightbulb` |
| Marco | `Flag` |
| Votação | `Circle` (ponto pequeno) |
| Item de ação | `CheckCircle` |
| Participante online | `Circle` (preenchido verde, 8px) |
| Editar card | `Pencil` |
| Excluir card | `Trash2` |
| Agrupar card | `GitMerge` |
| Desagrupar card | `GitBranch` |
| Card em foco (debate) | `Focus` |
| Encerrar sessão | `Lock` |
| Permitir entrada | `UserPlus` |
| Link bloqueado | `LinkOff` |
| Rastreador externo (opcional) | `ExternalLink` |

### 7.8 Componentes UI Específicos do RetroApp4L

#### RetroCard (card do board)

```
┌─────────────────────────────────┐
│  [avatar 24px] Nome · timestamp │  ← text-xs text-gray-500
│                                 │
│  Conteúdo do card               │  ← text-sm font-medium text-gray-950
│                                 │
│  [✎] [🗑] · [● 3 votos]         │  ← ícones Lucide, text-xs
│  [☐] (checkbox agrupamento)    │  ← visível apenas para facilitador
└─────────────────────────────────┘
```
- Background: `bg-white`
- Border: `border border-gray-200`
- Border-radius: `rounded-lg` (8px)
- Padding: `p-4` (16px)
- Shadow: `shadow-sm`
- Hover: `shadow-md`
- Checkbox visível apenas na fase de agrupamento e apenas para facilitador
- Ícone de voto visível apenas para cards `loathed` e `longed` na fase de votação
- Indicador "Seu card — não votável" em cards do próprio autor durante votação

#### MilestoneCard (card de marco)

```
┌─────────────────────────────────┐
│  🏆 Conquista                   │  ← text-xs font-semibold, cor da categoria
│                                 │
│  Deploy sem incidentes na sexta │  ← text-sm font-medium text-gray-950
│                                 │
│  Facilitador · timestamp        │  ← text-[10px] text-gray-500
└─────────────────────────────────┘
```

#### PhaseChip (chip de fase ativa)

```
[ ● Fase atual  10:00 ]
```
- Background: `bg-brand-50`
- Texto: `text-brand-500`
- Font: `text-xs font-semibold`
- Border-radius: `rounded` (4px)
- Padding: `px-2 py-1`

#### VoteBadge (contador de votos no card)

```
[ ● 5 ]
```
- Cor do dot: `text-brand-500`
- Font: `text-xs font-semibold`
- Votos próprios: destaque com `bg-brand-50`

#### TimerDisplay (cronômetro)

```
[ ⏱ 08:42 ]  [ ⏸ ]  [ ▶ ]
```
- Font: `text-xl font-semibold` quando > 1min
- Cor normal: `text-gray-950`
- Cor de alerta (< 60s): `text-warning-500`
- Cor crítica (< 30s): `text-danger-500`
- Transição: `transition-colors duration-150`
- Botões de pausa/retomar visíveis apenas para facilitador

#### ParticipantPanel (painel de participantes)

```
┌─────────────────────────────────────────────────┐
│  Participantes (3 online)                        │
│                                                 │
│  ● Ana (online)                                 │
│  ● Bruno (online)                               │
│  ● Carol (online)                               │
│                                                 │
│  ─────────────────────────────────────────────  │
│  🔒 Link de convite: BLOQUEADO                  │
│  A sessão já foi iniciada.                      │
│                                                 │
│  [Permitir nova entrada]                        │
│                                                 │
│  Histórico de acessos:                          │
│  • Ana entrou às 14:02                          │
│  • Bruno entrou às 14:03                        │
│  • Carol entrou às 14:04                        │
│  • Link reaberto às 14:12                       │
│  • Daniel entrou às 14:13                       │
│  • Link bloqueado automaticamente às 14:13      │
└─────────────────────────────────────────────────┘
```
- Seção de administração visível apenas para facilitador
- Status do link atualizado em tempo real

#### MilestoneBar (barra de marcos)

```
┌──────────────────────────────────────────────────┐
│  🏆 Deploy sem incidentes  ⚡ Bug na API         │
│  🙌 Ana cobriu oncall                           │  ← colapsável
└──────────────────────────────────────────────────┘
```
- Visível durante Board, Agrupamento, Votação, Debate e Ações
- Ordenado por `created_at`

#### ColumnHeader (cabeçalho de coluna do board)

```
┌────────────────────────────────────┐
│  [ícone]  GOSTEI          [3 cards]│
└────────────────────────────────────┘
```
- Background: cor semântica da coluna (ver 7.3)
- Font título: `text-sm font-semibold uppercase tracking-wide`
- Font contador: `text-xs font-normal`
- Border-radius: `rounded-lg rounded-b-none`
- Padding: `px-4 py-2`

#### FocusCard (card em foco no debate)

```
┌───────────────────────────────────────────────┐
│  ⭐ EM FOCO                                   │
│                                               │
│  Não Gostei — "API instável na Black Friday"  │
│  ● 8 votos                                    │
│                                               │
│  ───────────────────────────────────────────  │
│  Próximos:                                    │
│  • Aguardei — "Dashboard de métricas" (5)     │
│  • Não Gostei — "Review lento" (4)            │
│  [Próximo card ▶]                             │
└───────────────────────────────────────────────┘
```
- Visível apenas durante fase de Debate
- Controles de navegação apenas para facilitador

### 7.9 Layout do Board

```
┌──────────────────────────────────────────────────────────────────┐
│  [RetroApp4L]  Sprint 42 — Retro  [Fase: Board 4L ⏱ 08:42]      │
│                                    [● Ana] [● Bruno] [● Carol]   │
├──────────────────────────────────────────────────────────────────┤
│  🏆 Deploy  ⚡ Bug API  🙌 Ana oncall              [colapsável] │
├──────────────┬──────────────┬──────────────┬────────────────────┤
│  👍 GOSTEI  │ 👎 NÃO GOSTEI│  ⏰ AGUARDEI │  💡 APRENDI        │
│  ─────────  │  ─────────── │  ──────────  │  ──────────────    │
│  [card]     │  [card]      │  [card]      │  [card]            │
│  [card]     │              │              │  [card]            │
│             │              │              │                    │
│  [+ Adicionar card]                                            │
└──────────────┴──────────────┴──────────────┴────────────────────┘
```
- Barra de marcos entre header e board
- Padding horizontal: `px-8` (32px) desktop
- Gap entre colunas: `gap-4` (16px)
- Background do board: `bg-gray-50`

### 7.10 Regras de Voz e Conteúdo

- Todos os textos de interface em pt-BR por padrão. Preparado para localização via `@nuxtjs/i18n` ou equivalente.
- Segunda pessoa informal: "Adicionar card", "Seus votos restantes: 2".
- Sentence case em labels e botões: "Avançar fase", "Encerrar sessão".
- Erros: factuais e diretos. "Campo obrigatório." — não "Ops! Algo deu errado."
- Sem emoji em superfícies de produto. Ícones Lucide substituem emoji.
- Datas: formato brasileiro `DD/MM/AAAA` ou `dd DD MMM AA` para timestamps de card.
- Números de votos: sempre inteiros. Sem decimais.

---

## 8. Modelo de Dados

### users_user *(app: users)*

| Campo | Tipo Django | Tipo SQL | Descrição |
|---|---|---|---|
| id | UUIDField (PK) | uuid | |
| name | CharField(200) | varchar(200) | Nome completo |
| email | EmailField (unique) | varchar(254) | E-mail de login |
| password | CharField (hashed) | varchar(128) | Senha hasheada (auth local) |
| avatar_url | URLField (nullable) | varchar(200) | URL do avatar (OAuth ou Gravatar) |
| oauth_provider | CharField(50, nullable) | varchar(50) | `google`, `github`, ou null (local) |
| oauth_id | CharField(200, nullable) | varchar(200) | ID do provedor OAuth |
| is_active | BooleanField | boolean | Padrão Django |
| created_at | DateTimeField(auto_now_add) | timestamptz | |

### retrospectives_retrospective *(app: retrospectives)*

| Campo | Tipo Django | Tipo SQL | Descrição |
|---|---|---|---|
| id | UUIDField (PK) | uuid | |
| title | CharField(255) | varchar(255) | Título da retrospectiva |
| sprint_name | CharField(100, nullable) | varchar(100) | Nome da sprint |
| team_key | CharField(100) | varchar(100) | Identificador do time (slug). Obrigatório na criação. |
| facilitator | ForeignKey(User) | uuid FK | |
| status | CharField(choices) | varchar(20) | `setup\|lobby\|presentation\|check\|board\|grouping\|voting\|discussion\|actions\|closed` |
| invite_token | UUIDField (unique, nullable) | uuid | Token do link de convite |
| invite_revoked_at | DateTimeField (nullable) | timestamptz | |
| max_votes_per_user | IntegerField (default=3) | integer | |
| skip_check_phase | BooleanField (default=False) | boolean | |
| timer_started_at | DateTimeField (nullable) | timestamptz | |
| timer_paused_at | DateTimeField (nullable) | timestamptz | Se preenchido, cronômetro está pausado. |
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

> `unique_together: (card, voter)` — garante máximo 1 voto por card por participante.

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
| external_tracker_url | URLField(nullable) | varchar(200) | Link opcional para rastreador externo (GitHub Issues, Linear, etc.) |
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
| RF-01 | Autenticação | — | Login via credenciais locais (email/senha); provedores OAuth opcionais (Google, GitHub) via `django-allauth` | Must Have |
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
| RF-12 | Votação | US-04, US-10 | Dot voting restrito às colunas "Não Gostei" e "Aguardei"; limite de 1 voto por card por participante | Must Have |
| RF-13 | Debate | US-12 | Fase de debate com cards ordenados por votos e controle de "card em foco" pelo facilitador | Must Have |
| RF-14 | Ações | US-11 | Registrar itens de ação com descrição, responsável e prazo; URL de rastreador externo opcional | Must Have |
| RF-15 | Histórico | US-05 | Sessões encerradas no dashboard com status dos action items | Must Have |
| RF-16 | Presença | — | Lista de participantes online visível em tempo real; painel de controle de entrada | Should Have |
| RF-17 | Som | — | Alerta sonoro ao final do cronômetro (Web Audio API) | Should Have |

---

## 11. Requisitos Não Funcionais

### 11.1 Performance
- Latência WebSocket: < 200ms em rede interna.
- Operações de leitura crítica da API REST: < 300ms.
- `timer.sync` emitido a cada 5s; tolerância de ±1s no cliente. Cliente frontend deve interpolar contagem regressiva localmente a cada 1s e corrigir com `timer.sync`.
- `session.snapshot` para novos participantes deve ser enviado em < 1s.

### 11.2 Segurança
- Conexões WebSocket autenticadas via JWT (`AuthMiddlewareStack`).
- Link de convite UUID v4; revogável manualmente; bloqueado automaticamente após lobby.
- Votos do próprio autor bloqueados na camada de aplicação.
- Ações de agrupamento e avanço de fase verificam `request.user == retrospective.facilitator`.
- Nenhum endpoint acessível sem autenticação (`IsAuthenticated` como permissão global padrão).
- Senhas hasheadas com PBKDF2 padrão do Django (ou Argon2 se configurado).

### 11.3 Disponibilidade
- MVP para uso interno; sem SLA formal.
- Deploy em Fly.io com auto-scaling básico.
- **Cold starts:** Aplicação pode hibernar após inatividade no tier gratuito. Facilitadores devem acessar a aplicação minutos antes da retro para "aquecer" o serviço. Tempo de cold start típico: 2-5 segundos.

### 11.4 Escalabilidade
- Django Channels + Redis Channel Layer (Upstash) suporta múltiplas instâncias horizontais.
- Celery workers escalam independentemente.
- Até 30 participantes simultâneos por sessão no MVP.
- Tier gratuito do Fly.io (256 MB RAM) é suficiente para 30 conexões simultâneas com uso moderado.

### 11.5 Qualidade de Código
- Cobertura de testes: mínimo 80% nas apps `retrospectives`, `cards` e `actions`.
- Linting: `ruff` para Python, `eslint` + `prettier` para frontend Nuxt.
- Cada sprint passa em `python manage.py test` sem falhas antes do handoff.

### 11.6 Acessibilidade e UI
- Todos os componentes devem respeitar `:focus-visible` com `outline: 2px solid #000; outline-offset: 2px` (Tailwind: `focus-visible:outline-2 focus-visible:outline-black focus-visible:outline-offset-2`).
- Contraste mínimo AA entre texto e background.
- Animações limitadas a `color`, `background` e `opacity` com duração `150ms` (Tailwind: `transition-colors duration-150`). Sem bounces ou transforms de layout.
- Alerta sonoro do cronômetro usa Web Audio API com tons senoidais; não depende de interação prévia se contexto de áudio iniciado no primeiro clique.

---

## 12. Modelo de Sprints e Documento de Handoff

### 12.1 Por que o Handoff é Crítico

Agentes IA não retêm memória entre sessões. O handoff é o único mecanismo que conecta sprints. Um handoff vago produz código inconsistente. Um handoff preciso produz continuidade previsível.

**Regra:** se uma decisão técnica não está no handoff, ela não existe para a próxima sessão.

### 12.2 Estrutura Obrigatória do Documento de Handoff

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

### 12.3 Planejamento de Sprints

| Sprint | Foco | Entregáveis | Handoff |
|---|---|---|---|
| 1 | Fundação | Estrutura do projeto, Docker, PostgreSQL, migrations iniciais (inclui `team_key`, `timer_paused_at`, `Milestone`, `AccessLog`, status choices expandidos), auth local + OAuth opcional (`django-allauth`), criação de sessão com `team_key` | `SPRINT_1_HANDOFF.md` |
| 2 | Core Real-time | Django Channels + ASGI (Daphne), consumers WebSocket (inclui `session.snapshot`, `timer.paused`, `timer.resumed`, `card.ungrouped`), máquina de estados de fases (10 estados), cronômetro com pausa via Celery Beat, distinção entre nova entrada e reconexão | `SPRINT_2_HANDOFF.md` |
| 3 | Board 4L + Marcos | CRUD de cards com broadcast, modelo `Milestone`, preparação de marcos, apresentação de marcos, `MilestoneBar`, board em tempo real com marcos visíveis | `SPRINT_3_HANDOFF.md` |
| 4 | Agrupamento + Votação | Agrupamento por seleção múltipla (facilitador), dot voting restrito a `loathed`/`longed`, regra de 1 voto/card/pessoa, `vote.revoked` | `SPRINT_4_HANDOFF.md` |
| 5 | Fechamento do ciclo | Check de ações anteriores (por `team_key`), action items com status, fase de Debate com card em foco, encerramento, dashboard de histórico | `SPRINT_5_HANDOFF.md` |
| 6 | Frontend | Setup Nuxt 3 + Tailwind CSS, implementação de todas as telas e componentes seguindo seção 7 do PRD, alerta sonoro do cronômetro | `SPRINT_6_HANDOFF.md` |
| 7 | Polish + Qualidade | Painel de controle de entrada (bloqueio/reativação pós-lobby), presença em tempo real, testes E2E, cobertura ≥ 80%, acessibilidade | `SPRINT_7_HANDOFF.md` |
| 8 | Integrações (futuro) | Vinculação a rastreador externo, exportação PDF/CSV, analytics | — |

> **Premissa de tempo:** cada sprint é uma sessão de agente IA sem limite de tempo de programação humana. O mantenedor reserva 2–4h por sprint para revisão, validação e assinatura do handoff.

### 12.4 Prompt de Inicialização de Sprint

```
Você é o desenvolvedor do RetroApp4L, uma plataforma open-source de retrospectivas ágeis.

Leia o arquivo SPRINT_N_HANDOFF.md na raiz do repositório.
Ele contém o estado atual do projeto e exatamente o que deve ser feito nesta sprint.

Siga os padrões estabelecidos nas sprints anteriores.
Para o frontend, aplique rigorosamente o design system Tailwind CSS descrito na seção 7 do PRD (cores customizadas no tailwind.config.js, tipografia Inter, paleta de cores, espaçamento 4-pt, componentes definidos).
Ao finalizar, gere o rascunho do SPRINT_(N+1)_HANDOFF.md seguindo a estrutura definida no PRD.
Não tome decisões arquiteturais ou visuais não previstas no PRD sem registrar explicitamente no handoff para validação do mantenedor.
```

---

## 13. Decisões Registradas e Trade-offs

### 13.1 Django + PostgreSQL vs. outras opções
Python/Django foi escolhido pela ampla cobertura de treinamento de agentes IA de código com DRF + Django Channels. PostgreSQL por UUID nativo e comportamento previsível com o ORM Django.

### 13.2 Django Channels vs. solução gerenciada
Self-hosted, sem custo adicional. Redis já necessário para Celery — não adiciona nova peça de infra.

**Trade-off:** configuração ASGI (Daphne + Channels) mais complexa que WSGI tradicional. Sprint 2 é o maior risco técnico.

### 13.3 Celery Beat para cronômetro vs. asyncio no consumer
Celery Beat é explícito, testável e auditável entre sessões de agentes IA. Asyncio acoplado ao consumer é difícil de testar isoladamente e de rastrear entre sessões.

**Trade-off:** adiciona worker Celery e Beat scheduler no docker-compose e na VM de produção.

### 13.4 Nuxt 3 + Tailwind CSS para o frontend
Nuxt 3 é o framework padrão Vue 3 para SPA/SSR. Tailwind CSS fornece estilização utility-first com zero custo de runtime, customização total via `tailwind.config.js` e sem vendor lock-in. Tree-shakeable, amplamente adotado e bem documentado para produtividade de agentes IA.

**Trade-off:** Tailwind exige disciplina no uso consistente de classes. O agente IA deve priorizar os tokens semânticos definidos na seção 7 sobre defaults arbitrários do Tailwind quando houver conflito de estilo.

### 13.5 Dois repositórios vs. monorepo
Agentes IA operam melhor com escopo delimitado por sessão. Backend em uma sessão, frontend em outra, sem risco de contaminação entre contextos.

### 13.6 `team_key` como string vs. entidade Team completa
String simples permite agrupamento imediato no MVP sem adicionar entidade de time, convites de membros, ou permissões complexas. Suficiente para o check de ações e dashboard de histórico. Evolução futura pode migrar para entidade `Team` com chave estrangeira.

### 13.7 Milestone separado de Card
Marcos têm propósito distinto (aquecimento e contexto, criados offline pelo facilitador) e ciclo de vida diferente (não votados, não agrupados). Modelo separado evita condicionais `if card.is_milestone` e previne bugs de domínio.

### 13.8 Agrupamento restrito ao facilitador
Elimina conflitos de concorrência em tempo real (dois participantes agrupando o mesmo card). Seleção múltipla mantém agilidade para o facilitador. Drag-and-drop colaborativo fica para fase 2.

### 13.9 Votação restrita a "Não Gostei" e "Aguardei"
Foca priorização nas colunas que geram ações de melhoria. As colunas "Gostei" e "Aprendi" são para celebração e registro de conhecimento — não precisam de priorização forçada. Reduz dispersão de votos e torna a fase mais objetiva.

### 13.10 1 voto por card por participante
Força distribuição de votos e evita que um único card concentre todos os votos de um participante — o que derrotaria o propósito de priorização do dot voting. Regra fixa, sem toggle, para manter simplicidade.

### 13.11 Bloqueio de entrada pós-lobby
Preserva integridade do processo (todos compartilham mesmo histórico). Facilitador pode reabrir temporariamente para exceções. Reconexão de participante existente é sempre permitida.

### 13.12 Infraestrutura gratuita (Fly.io + Neon + Upstash + Vercel)
Permite MVP operar com R$ 0,00 de custo durante os 60 dias de avaliação. Trade-offs: cold starts (mitigado com aquecimento), limites de armazenamento e memória (folgados para o volume de uso esperado). Mantenedor pode migrar para Oracle Cloud Free se limites se mostrarem insuficientes.

### 13.13 Handoff como artefato de primeiro nível
Ausência ou imprecisão do handoff equivale a bug crítico — impede a sprint seguinte ou produz regressão silenciosa.

### 13.14 Auth local como padrão, OAuth como opcional
Auth local (email/senha) elimina dependência de provedores OAuth externos para uso básico. Sem restrição de domínio — qualquer time pode fazer self-host e usar imediatamente. Provedores OAuth (Google, GitHub) podem ser habilitados via variáveis de ambiente para times que preferem SSO.

### 13.15 Lucide Icons em vez de Material Design Icons
Lucide tem licença MIT, é tree-shakeable e tem suporte de primeira classe para Vue 3. Sem dependência de CDN — ícones são bundled no build time. Estilo de stroke consistente em 24px sem necessidade de gerenciar variantes outline vs. filled.

### 13.16 pt-BR como idioma padrão
O projeto nasceu em contexto brasileiro e mantém pt-BR como idioma padrão da interface. Localização para outros idiomas é viável via `@nuxtjs/i18n` com chaves de string extraídas. O PRD é disponibilizado em pt-BR e en-US para maximizar alcance da comunidade.

---

## 14. Licença

O RetroApp4L é distribuído sob a **Licença MIT**.

```
MIT License

Copyright (c) 2026 RetroApp4L Contributors

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

---

## 15. Contribuindo

Contribuições são bem-vindas. Siga estas diretrizes:

- **Issues:** Use GitHub Issues para reports de bugs e feature requests. Inclua passos de reprodução para bugs.
- **Pull Requests:** Uma feature ou fix por PR. Inclua testes. Atualize o CHANGELOG.
- **Code style:** Execute `ruff` (backend) e `eslint` (frontend) antes de submeter.
- **Atualizações de handoff:** Se seu PR altera arquitetura ou padrões, atualize o `SPRINT_*_HANDOFF.md` relevante.
- **Design system:** Não introduza novas cores, fontes ou valores de espaçamento sem atualizar a seção 7 deste PRD.

---

*RetroApp4L PRD v2.0 — Open Source (Licença MIT)*
