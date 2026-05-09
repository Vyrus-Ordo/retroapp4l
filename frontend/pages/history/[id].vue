<script setup lang="ts">
import MilestoneCard from "~/components/retro/MilestoneCard.vue"
import RetroCard from "~/components/retro/RetroCard.vue"
import type { Card } from "~/utils/types"

const route = useRoute()
const retroStore = useRetroStore()
const authStore = useAuthStore()
const pageError = ref<string | null>(null)

onMounted(async () => {
  try {
    await retroStore.fetchHistoryDetail(String(route.params.id))
  } catch (error) {
    pageError.value = error instanceof Error ? error.message : "Unable to load retrospective history."

    if (pageError.value === "Session expired. Please sign in again.") {
      await navigateTo(`/auth/login?redirect=${encodeURIComponent(route.fullPath)}`)
    }
  }
})

const detail = computed(() => retroStore.historyDetail)

const rootHistoryCards = computed<Card[]>(() => {
  if (!detail.value?.cards) return []
  return detail.value.cards.filter((c) => !c.group_parent_id && !c.group)
})

const historyChildrenByParentId = computed<Record<string, Card[]>>(() => {
  if (!detail.value?.cards) return {}
  const map: Record<string, Card[]> = {}
  for (const card of detail.value.cards) {
    const parentId = card.group_parent_id || card.group
    if (parentId) {
      if (!map[parentId]) map[parentId] = []
      map[parentId].push(card)
    }
  }
  return map
})

const isFacilitator = computed(() => {
  return detail.value?.facilitator === authStore.user?.id
})

const showExportModal = ref(false)

const { exportMarkdown } = useExportMarkdown({
  retro: detail,
  participants: computed(() => detail.value?.participants || []),
  cards: computed(() => detail.value?.cards || []),
  actionItems: computed(() => detail.value?.action_items || [])
})

const handleExport = (layout: 'table' | 'sections') => {
  exportMarkdown(layout)
  showExportModal.value = false
}
</script>

<template>
  <AppShell>
    <section v-if="pageError" class="panel p-6 lg:p-8">
      <p class="text-xs font-light text-[#00f2ff]/70">History detail</p>
      <h1 class="mt-3 text-2xl font-light text-white">Unable to load retrospective</h1>
      <p class="mt-2 text-sm text-zinc-500">{{ pageError }}</p>
    </section>

    <section v-else-if="detail" class="space-y-6">
      <div class="panel p-6 lg:p-8 flex flex-col sm:flex-row sm:items-start justify-between gap-4">
        <div>
          <p class="text-xs font-light text-[#00f2ff]/70">History detail</p>
          <h1 class="mt-3 text-2xl font-light text-white">{{ detail.title }}</h1>
          <p class="mt-2 text-sm text-zinc-500">{{ detail.sprint_name || 'No sprint' }} · {{ detail.team_key }} · {{ detail.facilitator_name }}</p>
        </div>
        <button
          v-if="isFacilitator"
          @click="showExportModal = true"
          class="button-secondary text-sm shrink-0"
        >
          Exportar
        </button>
      </div>

      <section v-if="detail.milestones.length" class="panel p-6 lg:p-8">
        <h2 class="text-lg font-light text-white">Milestones</h2>
        <div class="mt-4 grid gap-4 md:grid-cols-2 xl:grid-cols-3">
          <MilestoneCard v-for="milestone in detail.milestones" :key="milestone.id" :milestone="milestone" />
        </div>
      </section>

      <section class="panel p-6 lg:p-8">
        <h2 class="text-lg font-light text-white">Cards and action items</h2>
        <div class="mt-6 grid gap-6 xl:grid-cols-2">
          <div class="space-y-4">
            <RetroCard
              v-for="card in rootHistoryCards"
              :key="card.id"
              :card="card"
              :grouped-cards="historyChildrenByParentId[card.id] || []"
              :show-vote-badge="true"
            />
          </div>
          <div class="space-y-3 rounded-xl border border-white/8 p-4" style="background: rgba(255,255,255,0.03)">
            <div v-for="item in detail.action_items" :key="item.id" class="rounded-lg border border-white/8 p-4" style="background: rgba(255,255,255,0.04)">
              <p class="text-sm font-light text-zinc-200">{{ item.description }}</p>
              <p class="mt-2 text-xs text-zinc-600">{{ item.assignee_name || 'Unassigned' }} · {{ item.status }}</p>
            </div>
          </div>
        </div>
      </section>
    </section>

    <section v-else class="panel p-6 lg:p-8">
      <p class="text-xs font-light text-[#00f2ff]/70">History detail</p>
      <p class="mt-3 text-sm text-zinc-500">Loading retrospective...</p>
    </section>
    <Teleport to="body">
      <div v-if="showExportModal" class="fixed inset-0 z-[100] flex items-center justify-center bg-black/60 backdrop-blur-sm p-4">
        <div class="panel w-full max-w-md p-6 relative">
          <button @click="showExportModal = false" class="absolute top-4 right-4 text-zinc-400 hover:text-white transition-colors">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
          
          <h2 class="text-xl font-light text-white mb-6">Exportar retrospectiva</h2>
          
          <div class="space-y-4">
            <button @click="handleExport('sections')" class="w-full text-left p-4 rounded-xl border border-white/8 hover:bg-white/5 transition-colors group">
              <div class="font-medium text-white group-hover:text-[#00f2ff] transition-colors">Seções</div>
              <div class="text-xs text-zinc-400 mt-1">Cada coluna como bloco separado. Melhor para textos longos.</div>
            </button>
            
            <button @click="handleExport('table')" class="w-full text-left p-4 rounded-xl border border-white/8 hover:bg-white/5 transition-colors group">
              <div class="font-medium text-white group-hover:text-[#00f2ff] transition-colors">Tabela</div>
              <div class="text-xs text-zinc-400 mt-1">Colunas lado a lado. Melhor para visão compacta.</div>
            </button>
          </div>
        </div>
      </div>
    </Teleport>
  </AppShell>
</template>