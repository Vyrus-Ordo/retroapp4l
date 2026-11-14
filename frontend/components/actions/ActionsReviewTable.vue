<script setup lang="ts">
import type { ActionReviewItem, ActionStatus } from "~/utils/types"

/**
 * Lista (não tabela) de ações pendentes: cada ação ocupa a largura toda em
 * duas linhas — descrição longa em destaque e, abaixo, uma linha discreta com
 * time · retro · responsável · prazo · atualização. Badges de status/overdue e
 * a ação de edição ficam à direita. A ordenação vive só em
 * `ActionsReviewFilters`; não há coluna clicável.
 */
const props = defineProps<{
  items: ActionReviewItem[]
  count: number
  page: number
  pageSize: number
}>()

const emit = defineEmits<{
  edit: [item: ActionReviewItem]
  pageChange: [page: number]
}>()

const STATUS_LABELS: Record<ActionStatus, string> = {
  not_started: "Not started",
  in_progress: "In progress",
  done: "Done",
}

const STATUS_CLASSES: Record<ActionStatus, string> = {
  not_started: "border-white/10 text-zinc-400",
  in_progress: "border-[#00f2ff]/40 text-[#00f2ff]",
  done: "border-emerald-400/40 text-emerald-300",
}

const totalPages = computed(() => Math.max(1, Math.ceil(props.count / props.pageSize)))

/** `2026-11-20` → `20 Nov 2026` (locale fixo para não variar com o browser). */
function formatDueDate(value: string | null): string {
  if (!value) return "No due date"
  const parsed = /^\d{4}-\d{2}-\d{2}$/.test(value) ? new Date(`${value}T00:00:00`) : new Date(value)
  if (Number.isNaN(parsed.getTime())) return value
  return parsed.toLocaleDateString("en-GB", { day: "numeric", month: "short", year: "numeric" })
}

/** Tempo relativo curto; acima de 30 dias cai para a data absoluta. */
function formatUpdatedAt(value: string | null): string {
  if (!value) return "—"
  const parsed = new Date(value)
  if (Number.isNaN(parsed.getTime())) return value
  const minutes = Math.round((Date.now() - parsed.getTime()) / 60_000)
  if (minutes < 1) return "just now"
  if (minutes < 60) return `${minutes}m ago`
  const hours = Math.round(minutes / 60)
  if (hours < 24) return `${hours}h ago`
  const days = Math.round(hours / 24)
  if (days < 30) return `${days}d ago`
  return parsed.toLocaleDateString("en-GB", { day: "numeric", month: "short", year: "numeric" })
}
</script>

<template>
  <section class="panel mt-4 overflow-hidden" aria-label="Actions review list">
    <p v-if="!items.length" class="p-6 text-sm text-zinc-600" data-testid="actions-empty">
      No actions match these filters.
    </p>

    <template v-else>
      <div
        class="border-b border-white/10 px-4 py-3 text-xs font-light uppercase tracking-[0.12em] text-zinc-500 lg:px-6"
      >
        <span data-testid="actions-summary">{{ count }} action{{ count === 1 ? "" : "s" }} match the filters</span>
      </div>

      <ul class="divide-y divide-white/5">
        <li
          v-for="item in items"
          :key="item.id"
          class="p-4 transition-colors duration-150 hover:bg-white/[0.02] lg:px-6"
          data-testid="action-row"
        >
          <!-- Linha 1: descrição em destaque; status/overdue à direita -->
          <div class="flex flex-col gap-2 md:flex-row md:items-start md:justify-between md:gap-6">
            <div class="min-w-0 flex-1">
              <p
                class="break-words whitespace-pre-line text-lg leading-snug font-light text-white"
                data-testid="action-description"
              >
                {{ item.description }}
              </p>
              <a
                v-if="item.external_tracker_url"
                :href="item.external_tracker_url"
                class="mt-1 inline-block text-xs text-[#00f2ff]/80 hover:text-[#00f2ff]"
                target="_blank"
                rel="noopener noreferrer"
              >
                External tracker
              </a>
            </div>

            <div class="flex shrink-0 flex-wrap items-center gap-2 md:justify-end">
              <span
                class="rounded-full border px-2 py-0.5 text-[11px]"
                :class="STATUS_CLASSES[item.status]"
                data-testid="action-status"
              >
                {{ STATUS_LABELS[item.status] }}
              </span>
              <span
                v-if="item.is_overdue"
                class="rounded-full border border-red-400/50 px-2 py-0.5 text-[10px] tracking-[0.1em] text-red-300 uppercase"
                data-testid="action-overdue"
              >
                Overdue
              </span>
            </div>
          </div>

          <!-- Linha 2: metadados discretos; edição à direita -->
          <div class="mt-2 flex flex-col gap-2 md:flex-row md:items-center md:justify-between md:gap-4">
            <p class="flex flex-wrap items-center gap-x-2.5 gap-y-1 text-sm font-light text-zinc-500">
              <span data-testid="action-team">{{ item.retrospective.team_key }}</span>

              <span aria-hidden="true" class="text-zinc-600 select-none">·</span>
              <span class="inline-flex flex-wrap items-center gap-x-1" data-testid="action-retro">
                <NuxtLink
                  v-if="item.retrospective.status === 'closed'"
                  :to="`/history/${item.retrospective.id}`"
                  class="text-zinc-300 underline-offset-4 hover:text-white hover:underline"
                >
                  {{ item.retrospective.title }}
                </NuxtLink>
                <span v-else class="text-zinc-300">{{ item.retrospective.title }}</span>
                <span class="text-zinc-600">{{ item.retrospective.sprint_name || "No sprint" }}</span>
              </span>

              <span aria-hidden="true" class="text-zinc-600 select-none">·</span>
              <span data-testid="action-assignee">{{ item.assignee_name || "Unassigned" }}</span>

              <span aria-hidden="true" class="text-zinc-600 select-none">·</span>
              <span data-testid="action-due-date">{{ formatDueDate(item.due_date) }}</span>

              <span aria-hidden="true" class="text-zinc-600 select-none">·</span>
              <span data-testid="action-updated">Updated {{ formatUpdatedAt(item.status_updated_at) }}</span>
            </p>

            <div class="flex flex-wrap items-center gap-2 md:shrink-0 md:justify-end">
              <span
                v-if="item.retrospective.status !== 'closed'"
                class="rounded-full border border-amber-400/40 px-2 py-0.5 text-[10px] tracking-[0.1em] text-amber-300 uppercase"
              >
                Retro in progress
              </span>
              <button
                v-if="item.can_edit"
                type="button"
                class="button-secondary py-1.5 text-sm"
                @click="emit('edit', item)"
              >
                Edit
              </button>
            </div>
          </div>
        </li>
      </ul>

      <div
        class="flex flex-wrap items-center justify-between gap-3 border-t border-white/10 px-4 py-3 text-sm text-zinc-500 lg:px-6"
      >
        <span>{{ items.length }} shown</span>
        <div class="flex items-center gap-2">
          <button
            type="button"
            class="button-secondary py-1.5 text-sm"
            :disabled="page <= 1"
            @click="emit('pageChange', page - 1)"
          >
            Previous
          </button>
          <span>Page {{ page }} of {{ totalPages }}</span>
          <button
            type="button"
            class="button-secondary py-1.5 text-sm"
            :disabled="page >= totalPages"
            @click="emit('pageChange', page + 1)"
          >
            Next
          </button>
        </div>
      </div>
    </template>
  </section>
</template>
