/**
 * E2E — Actions Review (`/actions`).
 *
 * O endpoint `GET /api/actions/` pode ainda não existir no backend enquanto a
 * feature é implementada, então os testes MOCKAM `**\/api/actions/**` com
 * `page.route` (que tem precedência sobre a ponte de API registrada no
 * contexto por `helpers.ts`). O login continua real: a ponte do helper apenas
 * reescreve a origem da API para o serviço `backend`.
 *
 * Run: docker compose -f docker-compose.dev.yml exec frontend npx playwright test e2e/actions-review.spec.ts
 */
import { TEST_FACILITATOR, expect, loginAs, test } from "./helpers"
import type {
  ActionReviewAssigneeOption,
  ActionReviewItem,
  ActionReviewRetrospective,
  ActionStatus,
} from "../utils/types"

const CLOSED_RETRO: ActionReviewRetrospective = {
  id: "11111111-1111-1111-1111-111111111111",
  title: "Sprint 12",
  sprint_name: "S12",
  team_key: "platform",
  status: "closed",
  closed_at: "2026-11-01T18:00:00Z",
}

const ACTIVE_RETRO: ActionReviewRetrospective = {
  id: "22222222-2222-2222-2222-222222222222",
  title: "Sprint 13",
  sprint_name: "S13",
  team_key: "platform",
  status: "discussion",
  closed_at: null,
}

const EDITABLE_ITEM_ID = "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa"

const REVIEW_ITEMS: ActionReviewItem[] = [
  {
    id: EDITABLE_ITEM_ID,
    description: "Write the deploy runbook",
    status: "in_progress",
    status_updated_at: "2026-11-14T10:00:00Z",
    due_date: "2026-11-20",
    is_overdue: false,
    external_tracker_url: "",
    assignee_name: "Maria",
    assignee_user_id: "u-maria",
    assignee_participant_id: "p-maria",
    retrospective: CLOSED_RETRO,
    can_edit: true,
  },
  {
    id: "bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb",
    description: "Schedule the retro warm-up",
    status: "not_started",
    status_updated_at: "2026-11-13T09:00:00Z",
    due_date: "2026-11-30",
    is_overdue: false,
    external_tracker_url: "",
    assignee_name: "Joao",
    assignee_user_id: "u-joao",
    assignee_participant_id: "p-joao",
    retrospective: ACTIVE_RETRO,
    can_edit: false,
  },
]

const ASSIGNEE_OPTIONS = [
  { participant_id: "p-maria", name: "Maria" },
  { participant_id: "p-joao", name: "Joao" },
]

const TEAMS = [{ team_key: "platform", pending: 2, total: 5, can_edit: true }]

/**
 * Cenário de homônimos: dois participantes com o MESMO nome e ids distintos.
 * O responsável atual do item é o segundo (`p-maria-2`) — pré-selecionar por
 * `assignee_name` escolheria o primeiro, que é o bug que o
 * `assignee_participant_id` resolve (spec 3.1).
 */
const HOMONYM_OPTIONS: ActionReviewAssigneeOption[] = [
  { participant_id: "p-maria-1", name: "Maria" },
  { participant_id: "p-maria-2", name: "Maria" },
]

const HOMONYM_ITEM_ID = "cccccccc-cccc-cccc-cccc-cccccccccccc"

const HOMONYM_ITEM: ActionReviewItem = {
  ...REVIEW_ITEMS[0],
  id: HOMONYM_ITEM_ID,
  assignee_user_id: "u-maria-2",
  assignee_participant_id: "p-maria-2",
}

interface RecordedRequest {
  method: string
  path: string
  search: string
  body: Record<string, unknown> | null
}

function applyPatch(
  item: ActionReviewItem,
  patch: Record<string, unknown>,
  assigneeOptions: ActionReviewAssigneeOption[] = ASSIGNEE_OPTIONS,
): ActionReviewItem {
  const assignee = assigneeOptions.find((option) => option.participant_id === patch.assignee_id)

  return {
    ...item,
    description: typeof patch.description === "string" ? patch.description : item.description,
    status: typeof patch.status === "string" ? (patch.status as ActionStatus) : item.status,
    due_date: patch.due_date === null ? null : typeof patch.due_date === "string" ? patch.due_date : item.due_date,
    external_tracker_url:
      typeof patch.external_tracker_url === "string" ? patch.external_tracker_url : item.external_tracker_url,
    assignee_name: assignee ? assignee.name : item.assignee_name,
    assignee_participant_id: assignee ? assignee.participant_id : item.assignee_participant_id,
    status_updated_at: new Date().toISOString(),
  }
}

/**
 * Instala os mocks de `/api/actions/**` e devolve o log de requisições vistas.
 */
async function installActionsMock(
  page: import("@playwright/test").Page,
  items: ActionReviewItem[],
  assigneeOptions: ActionReviewAssigneeOption[] = ASSIGNEE_OPTIONS,
) {
  const requests: RecordedRequest[] = []
  const state = { items: items.map((item) => ({ ...item })) }

  await page.route(/\/api\/actions/, async (route) => {
    const request = route.request()
    const url = new URL(request.url())
    const method = request.method()
    const postData = request.postData()

    requests.push({
      method,
      path: url.pathname,
      search: url.search,
      body: postData ? (JSON.parse(postData) as Record<string, unknown>) : null,
    })

    if (url.pathname.endsWith("/teams/")) {
      return route.fulfill({ status: 200, json: TEAMS })
    }

    const detailMatch = url.pathname.match(/\/api\/actions\/([^/]+)\/$/)
    if (detailMatch) {
      const id = detailMatch[1]
      const item = state.items.find((candidate) => candidate.id === id)
      if (!item) {
        return route.fulfill({ status: 404, json: { detail: "Not found." } })
      }
      if (method === "PATCH") {
        const updated = applyPatch(
          item,
          postData ? (JSON.parse(postData) as Record<string, unknown>) : {},
          assigneeOptions,
        )
        state.items = state.items.map((candidate) => (candidate.id === id ? updated : candidate))
        return route.fulfill({ status: 200, json: { ...updated, assignee_options: assigneeOptions } })
      }
      return route.fulfill({ status: 200, json: { ...item, assignee_options: assigneeOptions } })
    }

    return route.fulfill({
      status: 200,
      json: { count: state.items.length, next: null, previous: null, results: state.items },
    })
  })

  return { requests }
}

test.describe("Actions Review", () => {
  test("anonymous user is redirected to the login page", async ({ page }) => {
    await page.goto("/actions")

    await expect(page).toHaveURL(/\/auth\/login\?redirect=(\/actions|%2Factions)$/)
    await expect(page.getByLabel(/email/i)).toBeVisible()
  })

  test("authenticated user sees the page, the menu link and the empty state", async ({ page }) => {
    await installActionsMock(page, [])

    await loginAs(page, TEST_FACILITATOR)

    const menuLink = page.getByRole("link", { name: "Actions Review" })
    await expect(menuLink).toBeVisible()
    await menuLink.click()

    await expect(page).toHaveURL(/\/actions$/)
    await expect(page.getByRole("heading", { name: "Actions Review" })).toBeVisible()
    await expect(page.getByTestId("actions-empty")).toHaveText("No actions match these filters.")
  })

  test("lists mocked actions with the default status filter", async ({ page }) => {
    const { requests } = await installActionsMock(page, REVIEW_ITEMS)

    await loginAs(page, TEST_FACILITATOR)
    await page.goto("/actions")

    // A tela não tem mais tabela — nada de `columnheader` clicável.
    await expect(page.getByRole("columnheader")).toHaveCount(0)
    await expect(page.getByTestId("actions-summary")).toHaveText("2 actions match the filters")

    // Cada ação é um item de largura total: descrição em destaque + linha de
    // metadados (time · retro · responsável · prazo · atualização).
    await expect(page.getByTestId("action-row")).toHaveCount(2)

    const closedRow = page.getByTestId("action-row").filter({ hasText: "Write the deploy runbook" })
    await expect(closedRow.getByTestId("action-description")).toHaveText("Write the deploy runbook")
    await expect(closedRow.getByTestId("action-team")).toHaveText("platform")
    await expect(closedRow.getByTestId("action-retro")).toContainText("Sprint 12")
    await expect(closedRow.getByTestId("action-retro")).toContainText("S12")
    await expect(closedRow.getByRole("link", { name: "Sprint 12" })).toHaveAttribute(
      "href",
      `/history/${CLOSED_RETRO.id}`,
    )
    await expect(closedRow.getByTestId("action-assignee")).toHaveText("Maria")
    await expect(closedRow.getByTestId("action-due-date")).toHaveText("20 Nov 2026")
    await expect(closedRow.getByTestId("action-status")).toHaveText("In progress")
    await expect(closedRow.getByTestId("action-updated")).toContainText("Updated")
    await expect(closedRow.getByTestId("action-overdue")).toHaveCount(0)

    const activeRow = page.getByTestId("action-row").filter({ hasText: "Schedule the retro warm-up" })
    await expect(activeRow.getByTestId("action-description")).toHaveText("Schedule the retro warm-up")
    await expect(activeRow.getByTestId("action-team")).toHaveText("platform")
    await expect(activeRow.getByTestId("action-retro")).toContainText("Sprint 13")
    // Retro ainda aberta: título em texto puro, sem link para o histórico.
    await expect(activeRow.getByRole("link", { name: "Sprint 13" })).toHaveCount(0)
    await expect(activeRow.getByTestId("action-assignee")).toHaveText("Joao")
    await expect(activeRow.getByTestId("action-due-date")).toHaveText("30 Nov 2026")
    await expect(activeRow.getByTestId("action-status")).toHaveText("Not started")

    // O padrão da tela envia os dois status como parâmetros repetidos.
    const listRequest = requests.find((request) => request.method === "GET" && request.path === "/api/actions/")
    expect(listRequest, "GET /api/actions/ was not requested").toBeTruthy()
    const params = new URLSearchParams(listRequest?.search ?? "")
    expect(params.getAll("status")).toEqual(["not_started", "in_progress"])
    expect(params.toString()).not.toContain("status=not_started,in_progress")

    const editableRow = page.getByTestId("action-row").filter({ hasText: "Write the deploy runbook" })
    await expect(editableRow.getByRole("button", { name: /^edit/i })).toBeVisible()

    const readOnlyRow = page.getByTestId("action-row").filter({ hasText: "Schedule the retro warm-up" })
    await expect(readOnlyRow.getByRole("button", { name: /^edit/i })).toHaveCount(0)
    await expect(readOnlyRow.getByText("Retro in progress")).toBeVisible()
  })

  test("edits an action through the modal and updates the row", async ({ page }) => {
    const { requests } = await installActionsMock(page, REVIEW_ITEMS)

    await loginAs(page, TEST_FACILITATOR)
    await page.goto("/actions")

    const row = page.getByTestId("action-row").filter({ hasText: "Write the deploy runbook" })
    await row.getByRole("button", { name: /^edit/i }).click()

    const dialog = page.getByRole("dialog", { name: "Edit action" })
    await expect(dialog).toBeVisible()
    await expect(dialog.getByLabel("Description")).toHaveValue("Write the deploy runbook")
    await expect(dialog.getByLabel("Assignee")).toHaveValue("p-maria")

    await dialog.getByLabel("Description").fill("Write the rollback runbook")
    await dialog.getByLabel("Status").selectOption("done")
    await dialog.getByLabel("Due date").fill("2026-12-01")
    // Troca explícita de responsável: aqui o `assignee_id` DEVE ir no PATCH.
    await dialog.getByLabel("Assignee").selectOption("p-joao")
    await dialog.getByRole("button", { name: /save changes/i }).click()

    await expect(dialog).toBeHidden()

    const patch = requests.find((request) => request.method === "PATCH")
    expect(patch, "PATCH /api/actions/{id}/ was not requested").toBeTruthy()
    expect(patch?.path).toBe(`/api/actions/${EDITABLE_ITEM_ID}/`)
    expect(patch?.body).toMatchObject({
      description: "Write the rollback runbook",
      status: "done",
      due_date: "2026-12-01",
      assignee_id: "p-joao",
    })

    await expect(page.getByTestId("action-row").filter({ hasText: "Write the rollback runbook" })).toBeVisible()
    await expect(page.getByTestId("action-row").filter({ hasText: "Write the deploy runbook" })).toHaveCount(0)
  })

  test("preselects the assignee by participant id with homonyms and omits assignee_id when unchanged", async ({
    page,
  }) => {
    const { requests } = await installActionsMock(page, [HOMONYM_ITEM], HOMONYM_OPTIONS)

    await loginAs(page, TEST_FACILITATOR)
    await page.goto("/actions")

    const row = page.getByTestId("action-row").filter({ hasText: "Write the deploy runbook" })
    await row.getByRole("button", { name: /^edit/i }).click()

    const dialog = page.getByRole("dialog", { name: "Edit action" })
    await expect(dialog).toBeVisible()

    // Duas opções com o mesmo rótulo e ids distintos...
    const homonyms = dialog.getByLabel("Assignee").locator("option[value^='p-maria']")
    await expect(homonyms).toHaveCount(2)
    await expect(homonyms).toHaveText(["Maria", "Maria"])

    // ...e o select pré-seleciona o participante atual (p-maria-2), não o
    // primeiro homônimo nem um casamento por nome.
    await expect(dialog.getByLabel("Assignee")).toHaveValue("p-maria-2")

    await dialog.getByLabel("Description").fill("Write the rollback runbook")
    await dialog.getByRole("button", { name: /save changes/i }).click()
    await expect(dialog).toBeHidden()

    const patch = requests.find((request) => request.method === "PATCH")
    expect(patch, "PATCH /api/actions/{id}/ was not requested").toBeTruthy()
    expect(patch?.path).toBe(`/api/actions/${HOMONYM_ITEM_ID}/`)
    expect(patch?.body).toMatchObject({ description: "Write the rollback runbook" })
    // Sem troca no select, o PATCH não carrega assignee_id (backend preserva).
    expect(patch?.body).not.toHaveProperty("assignee_id")

    await expect(page.getByTestId("action-row").filter({ hasText: "Write the rollback runbook" })).toBeVisible()
  })
})
