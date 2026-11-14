# E2E (Playwright)

Suíte de navegador do frontend. Toda execução é **dentro do container** (regra do
`AGENTS.md`).

```bash
docker compose -f docker-compose.dev.yml up -d          # sem --build
docker compose -f docker-compose.dev.yml exec frontend npx playwright test --output=/tmp/pw-results
```

Nunca grave resultados em `frontend/test-results/` — use sempre `--output=/tmp/pw-results`.

## Specs

| Arquivo | Cobre |
| --- | --- |
| `smoke.spec.ts` | renderização das páginas públicas, sem backend |
| `auth.spec.ts` | formulário de login/registro, erro de credencial inválida, guard de rota |
| `dashboard.spec.ts` | dashboard autenticado e validação do formulário de criação |
| `milestone-visuals.spec.ts` | mapeamento/contraste dos marcos (spec de unidade) |

## Usuário de teste

`ensureUser()` (`helpers.ts`) garante o usuário antes do login:

1. tenta `POST /api/auth/login/` com as credenciais de teste — se responder 200, o usuário existe;
2. senão, `POST /api/auth/register/` com as mesmas credenciais.

Isso funciona **sem mudar código de produção**: no ambiente dev o
`CLOUDFLARE_TURNSTILE_SECRET_KEY` está vazio em `backend/.env.dev` e
`apps/users/turnstile.py` libera o registro nesse caso (o widget Turnstile é só
da UI). Nenhum management command é necessário.

Credenciais são fictícias e vêm de variável de ambiente, com default de teste:

| Variável | Default |
| --- | --- |
| `E2E_FACILITATOR_EMAIL` | `e2e_facilitator@example.com` |
| `E2E_FACILITATOR_PASSWORD` | `E2eTestPass123!` |
| `E2E_PARTICIPANT_EMAIL` | `e2e_participant@example.com` |
| `E2E_PARTICIPANT_PASSWORD` | `E2eTestPass123!` |

Se a conta existir no banco com outra senha, o login falha e o registro retorna
400: remova o usuário do banco de dev ou aponte as variáveis para credenciais
novas.

## Origem da API vista pelo navegador

O SPA é servido de dentro do container `frontend` e chama
`NUXT_PUBLIC_API_BASE=http://localhost:8000/api`. Dentro desse container
`localhost` é o próprio container — o backend está em `http://backend:8000`.
Por isso o fixture automático `test` (`helpers.ts`) reescreve a origem da API via
`context.route()`, sem tocar no código do app:

| Variável | Default |
| --- | --- |
| `E2E_BROWSER_API_ORIGIN` | `http://localhost:8000` (origem que o SPA chama) |
| `E2E_INTERNAL_API_ORIGIN` | `http://backend:8000` (origem alcançável de dentro do container) |
| `E2E_API_BASE` | opcional; força a base usada pelo processo de teste para provisionar usuários |

Quando os dois valores são iguais (ex.: rodando no host), a reescrita é
desligada automaticamente.

## Convenções dos specs

- Seletores por papel/rótulo (`getByRole`, `getByLabel`), nunca por texto solto
  que muda com o layout.
- Specs que exercitam o backend importam `test` de `./helpers` (não de
  `@playwright/test`), para herdar a ponte de API.
