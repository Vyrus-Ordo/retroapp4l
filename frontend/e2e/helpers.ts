/**
 * E2E helpers shared across test files.
 *
 * Requires a running stack (`docker compose -f docker-compose.dev.yml up -d`).
 * Pre-conditions, environment variables and the reason for the API bridge are
 * documented in e2e/README.md.
 */
import { type BrowserContext, type Page, expect, test as base } from "@playwright/test"

export { expect }

const DEFAULT_TEST_PASSWORD = "E2eTestPass123!"

export interface TestUser {
  name: string
  email: string
  password: string
}

/**
 * Credentials are obviously fictitious on purpose and can be overridden by env
 * vars so the suite never depends on a real account.
 */
export const TEST_FACILITATOR: TestUser = {
  name: "E2E Facilitator",
  email: process.env.E2E_FACILITATOR_EMAIL ?? "e2e_facilitator@example.com",
  password: process.env.E2E_FACILITATOR_PASSWORD ?? DEFAULT_TEST_PASSWORD,
}

export const TEST_PARTICIPANT: TestUser = {
  name: "E2E Participant",
  email: process.env.E2E_PARTICIPANT_EMAIL ?? "e2e_participant@example.com",
  password: process.env.E2E_PARTICIPANT_PASSWORD ?? DEFAULT_TEST_PASSWORD,
}

/**
 * Origin the SPA calls for the API (NUXT_PUBLIC_API_BASE minus the /api path).
 * Inside the frontend container that origin is the container loopback, not the
 * backend, so the browser reaches the backend through the compose service name.
 */
const BROWSER_API_ORIGIN = process.env.E2E_BROWSER_API_ORIGIN ?? "http://localhost:8000"
const INTERNAL_API_ORIGIN = process.env.E2E_INTERNAL_API_ORIGIN ?? "http://backend:8000"

async function isReachable(url: string): Promise<boolean> {
  try {
    // Any HTTP response (even 401) proves the route works.
    await fetch(url, { method: "GET" })
    return true
  } catch {
    return false
  }
}

let apiBasePromise: Promise<string> | undefined

/** Resolves the API base reachable from the test process (not from the browser). */
export function resolveApiBase(): Promise<string> {
  apiBasePromise ??= (async () => {
    const candidates = [
      process.env.E2E_API_BASE,
      `${INTERNAL_API_ORIGIN}/api`,
      `${BROWSER_API_ORIGIN}/api`,
    ].filter((value): value is string => Boolean(value))

    for (const candidate of candidates) {
      if (await isReachable(`${candidate}/retrospectives/`)) {
        return candidate
      }
    }

    throw new Error(
      `[e2e] Backend API unreachable from the test process. Tried: ${candidates.join(", ")}. ` +
        "Is the stack up (docker compose -f docker-compose.dev.yml up -d)?",
    )
  })()

  return apiBasePromise
}

async function apiFetch(path: string, init: RequestInit = {}): Promise<Response> {
  const base = await resolveApiBase()
  return fetch(`${base}${path}`, {
    ...init,
    headers: { "Content-Type": "application/json", ...(init.headers ?? {}) },
  })
}

/**
 * Guarantees the test user exists in the environment database.
 *
 * The dev stack runs with an empty CLOUDFLARE_TURNSTILE_SECRET_KEY, so the
 * public register endpoint accepts requests without a Turnstile token
 * (apps/users/turnstile.py bypasses the check in that case). No backend code
 * change and no management command are needed.
 */
export async function ensureUser(user: TestUser): Promise<void> {
  const login = await apiFetch("/auth/login/", {
    method: "POST",
    body: JSON.stringify({ email: user.email, password: user.password }),
  })
  if (login.ok) {
    return
  }

  const register = await apiFetch("/auth/register/", {
    method: "POST",
    body: JSON.stringify({ name: user.name, email: user.email, password: user.password }),
  })
  if (register.ok) {
    return
  }

  throw new Error(
    `[e2e] Could not provision test user ${user.email} (register ${register.status}): ` +
      `${await register.text()}. If the account exists with another password, remove it from ` +
      "the dev database or point E2E_FACILITATOR_* to fresh credentials. See e2e/README.md.",
  )
}

/**
 * The browser runs inside the frontend container while the SPA is configured to
 * call http://localhost:8000 — inside that container localhost is the container
 * itself. Rewriting the API origin keeps the app untouched and lets the real
 * login flow run against the backend service.
 */
export async function bridgeApiToBackend(context: BrowserContext): Promise<void> {
  if (BROWSER_API_ORIGIN === INTERNAL_API_ORIGIN) {
    return
  }

  await context.route(`${BROWSER_API_ORIGIN}/**`, (route) =>
    route.continue({
      url: route.request().url().replace(BROWSER_API_ORIGIN, INTERNAL_API_ORIGIN),
    }),
  )
}

/**
 * Playwright `test` with the API bridge already applied, for every spec that
 * exercises the backend through the UI.
 */
export const test = base.extend<{ apiBridge: boolean }>({
  apiBridge: [
    async ({ context }, use) => {
      await bridgeApiToBackend(context)
      await use(true)
    },
    { auto: true },
  ],
})

export async function loginAs(page: Page, user: TestUser): Promise<void> {
  await ensureUser(user)

  await page.goto("/auth/login")
  await page.getByLabel(/email/i).fill(user.email)
  await page.getByLabel(/password/i).fill(user.password)
  await page.getByRole("button", { name: /^sign in$/i }).click()

  // The authenticated shell only renders once the session is stored.
  await expect(page).not.toHaveURL(/\/auth\/login/)
  await expect(page.getByRole("button", { name: /logout/i })).toBeVisible()
}
