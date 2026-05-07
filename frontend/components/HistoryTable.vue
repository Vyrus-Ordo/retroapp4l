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
    <h2 class="text-lg font-light tracking-wide text-white">History</h2>
    <div class="overflow-x-auto rounded-lg border border-white/8" style="background: rgba(255,255,255,0.03)">
      <table class="min-w-full text-sm">
        <thead>
          <tr class="border-b border-white/8" style="background: rgba(255,255,255,0.03)">
            <th class="px-4 py-3 text-left text-xs font-light uppercase tracking-wide text-zinc-600">Sprint</th>
            <th class="px-4 py-3 text-left text-xs font-light uppercase tracking-wide text-zinc-600">Title</th>
            <th class="px-4 py-3 text-left text-xs font-light uppercase tracking-wide text-zinc-600">Date</th>
            <th class="px-4 py-3 text-left text-xs font-light uppercase tracking-wide text-zinc-600">Status</th>
            <th class="px-4 py-3 text-left text-xs font-light uppercase tracking-wide text-zinc-600">Actions</th>
            <th class="px-4 py-3 text-left text-xs font-light uppercase tracking-wide text-zinc-600">Link</th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="retro in retros"
            :key="retro.id"
            class="border-b border-white/5 transition-colors hover:bg-white/[0.03]"
          >
            <td class="px-4 py-3 text-sm text-zinc-400">{{ retro.sprint_name || '—' }}</td>
            <td class="px-4 py-3 text-sm font-light text-white">{{ retro.title }}</td>
            <td class="px-4 py-3 text-sm text-zinc-500">{{ formatDate(retro.created_at) }}</td>
            <td class="px-4 py-3">
              <span class="rounded border border-white/10 px-2 py-1 text-xs font-light text-zinc-500">Closed</span>
            </td>
            <td class="px-4 py-3 text-sm text-zinc-500">{{ actionsSummary(retro as any) }}</td>
            <td class="px-4 py-3">
              <NuxtLink
                :to="`/retro/${retro.id}`"
                class="text-sm font-light text-[#00f2ff]/70 transition-colors hover:text-[#00f2ff]"
              >
                View
              </NuxtLink>
            </td>
          </tr>
          <tr v-if="!retros.length">
            <td colspan="6" class="px-4 py-8 text-center text-sm text-zinc-600">
              No closed retrospectives yet.
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </section>
</template>
