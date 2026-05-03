<script setup lang="ts">
import type { RetrospectiveSummary } from '~/utils/types'

defineProps<{
  retros: RetrospectiveSummary[]
}>()

function formatDate(dateStr: string): string {
  return new Intl.DateTimeFormat('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
  }).format(new Date(dateStr))
}

function actionsSummary(retro: RetrospectiveSummary & { actions_done?: number; actions_total?: number }): string {
  const done = retro.actions_done ?? 0
  const total = retro.actions_total ?? 0
  return `${done}/${total} action items completed`
}
</script>

<template>
  <section class="flex flex-col gap-4">
    <h2 class="text-lg font-semibold text-slate-900">History</h2>
    <div class="overflow-x-auto rounded-lg border border-slate-100 bg-white shadow-sm">
      <table class="min-w-full text-sm">
        <thead>
          <tr class="border-b border-slate-100 bg-slate-50">
            <th class="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wide text-slate-600">Sprint</th>
            <th class="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wide text-slate-600">Title</th>
            <th class="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wide text-slate-600">Date</th>
            <th class="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wide text-slate-600">Status</th>
            <th class="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wide text-slate-600">Actions</th>
            <th class="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wide text-slate-600">Link</th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="retro in retros"
            :key="retro.id"
            class="border-b border-slate-100 hover:bg-slate-50"
          >
            <td class="px-4 py-3 text-sm text-slate-900">{{ retro.sprint_name || '—' }}</td>
            <td class="px-4 py-3 text-sm font-medium text-slate-900">{{ retro.title }}</td>
            <td class="px-4 py-3 text-sm text-slate-600">{{ formatDate(retro.created_at) }}</td>
            <td class="px-4 py-3">
              <span class="rounded bg-slate-100 px-2 py-1 text-xs font-semibold text-slate-600">Closed</span>
            </td>
            <td class="px-4 py-3 text-sm text-slate-600">{{ actionsSummary(retro as any) }}</td>
            <td class="px-4 py-3">
              <NuxtLink
                :to="`/retro/${retro.id}`"
                class="text-sm font-medium text-brand-500 hover:text-brand-600 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-black"
              >
                View
              </NuxtLink>
            </td>
          </tr>
          <tr v-if="!retros.length">
            <td colspan="6" class="px-4 py-8 text-center text-sm text-slate-400">
              No closed retrospectives yet.
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </section>
</template>
