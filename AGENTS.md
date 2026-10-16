# Regras para agentes (CEO, Dev, Revisor)

## Execução de comandos — regra obrigatória: nunca local, sempre Docker Compose

Qualquer build, lint, typecheck ou teste (frontend ou backend) deve rodar **dentro
dos containers do `docker-compose`**, nunca diretamente no host (nunca `npm run ...`,
`pytest`, `python manage.py ...`, `ruff ...` executados fora de container, mesmo que
funcionem localmente).

- Suba o ambiente com `docker compose -f docker-compose.dev.yml up --build -d`
  (ou o compose file já em uso no projeto) antes de rodar qualquer check.
- Rode os comandos através de `docker compose exec <serviço> <comando>`, por exemplo:
  - `docker compose exec frontend npm run build`
  - `docker compose exec frontend npm run lint`
  - `docker compose exec frontend npm run test:e2e`
  - `docker compose exec backend pytest`
- Se o Docker não subir, ou faltar um serviço no compose para rodar algum check
  necessário: **pare e reporte o motivo na tarefa/PR** — isso é um bloqueio legítimo
  que o Board resolve, não um convite a rodar localmente "só dessa vez".
- Esta regra vale para os três agentes, independente do adapter/modelo configurado
  em cada um (Claude Code, OpenCode, ou qualquer outro).

Os comandos "nus" (`npm run build`, `pytest` etc.) descritos no resto deste arquivo
e no `CLAUDE.md` servem só para identificar QUAL comando rodar — sempre prefixado
por `docker compose exec <serviço>` na execução real.

---

@CLAUDE.md