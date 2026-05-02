# Sprint 2 — Handoff

## Estado do repositório
- Branch: N/A — workspace atual sem repositório Git inicializado
- Último commit: N/A — workspace atual sem histórico Git disponível
- Migrations pendentes: não, após executar python manage.py makemigrations e python manage.py migrate

## O que foi implementado e está funcionando
- Backend Django estruturado conforme a árvore imutável da Sprint 1, com settings split em [backend/config/settings/base.py](backend/config/settings/base.py), [backend/config/settings/local.py](backend/config/settings/local.py) e [backend/config/settings/production.py](backend/config/settings/production.py)
- Custom User com UUID, email único, suporte a campos OAuth e admin configurado em [backend/apps/users/models.py](backend/apps/users/models.py) e [backend/apps/users/admin.py](backend/apps/users/admin.py)
- Auth local por API com registro, login JWT e logout com blacklist em [backend/apps/users/views.py](backend/apps/users/views.py) e [backend/apps/users/serializers.py](backend/apps/users/serializers.py)
- Modelos iniciais de retrospectiva, participante, milestone, access log, card, voto e action item implementados em [backend/apps/retrospectives/models.py](backend/apps/retrospectives/models.py), [backend/apps/cards/models.py](backend/apps/cards/models.py) e [backend/apps/actions/models.py](backend/apps/actions/models.py)
- Endpoint POST/GET de retrospectivas, detalhe por id e sugestões de team_key implementados em [backend/apps/retrospectives/views.py](backend/apps/retrospectives/views.py) e [backend/apps/retrospectives/urls.py](backend/apps/retrospectives/urls.py)
- Esqueleto inicial de ASGI/Channels e consumer WebSocket criado em [backend/config/asgi.py](backend/config/asgi.py) e [backend/apps/realtime/consumers.py](backend/apps/realtime/consumers.py)
- Infra local de desenvolvimento adicionada com [docker-compose.yml](docker-compose.yml), [backend/Dockerfile](backend/Dockerfile), [backend/Dockerfile.worker](backend/Dockerfile.worker), [backend/.env.example](backend/.env.example) e [backend/requirements.txt](backend/requirements.txt)
- Testes mínimos da Sprint 1 cobrindo auth e retrospectives implementados em [backend/tests/users/test_api.py](backend/tests/users/test_api.py) e [backend/tests/retrospectives/test_api.py](backend/tests/retrospectives/test_api.py)

## O que foi iniciado e não concluído
- Integração completa de OAuth social via provedores específicos do allauth não foi concluída; a base do allauth está configurada, mas credenciais/apps de provedores ainda não foram adicionadas porque dependem do ambiente e do provedor escolhido
- Frontend Nuxt 3 permanece não iniciado; isso está alinhado ao planejamento, já que a Sprint 1 é backend-first

## Decisões técnicas tomadas nesta sprint
- Fallback para SQLite no ambiente local sem variáveis de PostgreSQL → mantém python manage.py test e validações locais executáveis sem depender de containers → [backend/config/settings/base.py](backend/config/settings/base.py)
- JWT via djangorestframework-simplejwt → fecha o critério de done de login com token sem introduzir auth proprietária → [backend/apps/users/views.py](backend/apps/users/views.py)
- Inclusão do campo description em Retrospective → compatibiliza o payload exigido pelo endpoint de criação com o modelo persistido → [backend/apps/retrospectives/models.py](backend/apps/retrospectives/models.py)
- Consumer WebSocket apenas como esqueleto com session.snapshot inicial → suficiente para preparar a Sprint 2 sem antecipar a máquina de estados ou eventos fora do escopo → [backend/apps/realtime/consumers.py](backend/apps/realtime/consumers.py)

## Padrões estabelecidos que devem ser seguidos
- Todos os apps Django vivem sob o pacote apps.* e usam label curta estável para AUTH_USER_MODEL e migrations
- Os settings sempre entram por config.settings, com seleção de ambiente em [backend/config/settings/__init__.py](backend/config/settings/__init__.py)
- Endpoints REST usam DRF class-based views e serializers por app, sem lógica de validação espalhada nas views
- O facilitador é automaticamente incluído como Participant ao criar uma retrospectiva, preservando votes_remaining igual a max_votes_per_user
- Os textos de API permanecem em inglês, alinhados ao PRD

## Próxima sprint: o que deve ser feito
- Implementar Django Channels com fluxo real de sala por retrospectiva, incluindo session.snapshot completo e eventos timer.paused, timer.resumed e card.ungrouped, com critério de done: conexão WebSocket funcional por retrospectiva e broadcast entre clientes
- Criar a máquina de estados das 10 fases da retrospectiva no domínio de retrospectives, com transições válidas e testes cobrindo avanço/bloqueio de fase
- Implementar cronômetro com pausa e retomada usando Celery/Beat e sincronização por WebSocket, com critério de done: backend consegue iniciar, pausar, retomar e sincronizar timer
- Diferenciar nova entrada de reconexão na camada realtime/acesso, com atualização de presença e logs coerentes
- Adicionar testes automatizados da Sprint 2 para consumers, transições de fase e timer

## Comandos para retomar
- docker-compose up -d
- cd backend && python manage.py migrate
- cd backend && python manage.py test