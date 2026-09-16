<template>
  <div class="panel p-6 flex flex-col gap-4">
    <h2 class="text-sm font-medium text-zinc-400 uppercase tracking-[0.2em]">Sprint Summary</h2>

    <div class="grid gap-4 sm:grid-cols-3">
      <div class="flex flex-col gap-1">
        <label for="ss-total" class="text-xs text-zinc-500">Total de histórias</label>
        <input id="ss-total" v-model.number="total" type="number" min="0" class="field-input" placeholder="0" />
      </div>
      <div class="flex flex-col gap-1">
        <label for="ss-completed" class="text-xs text-zinc-500">Concluídas</label>
        <input id="ss-completed" v-model.number="completed" type="number" min="0" class="field-input" placeholder="0" />
      </div>
      <div class="flex flex-col gap-1">
        <label for="ss-carryover" class="text-xs text-zinc-500">Carry-over</label>
        <input id="ss-carryover" v-model.number="carryover" type="number" min="0" class="field-input" placeholder="0" />
      </div>
    </div>

    <div class="flex items-center justify-between gap-4">
      <div class="flex flex-col gap-0.5">
        <span class="text-xs text-zinc-500 uppercase tracking-wide">Taxa de entrega</span>
        <span class="text-2xl font-light" :class="total > 0 ? 'text-[#00f2ff]' : 'text-zinc-600'">{{ deliveryRate }}</span>
      </div>
      <button class="button-primary" :disabled="saving" @click="save">
        {{ saving ? 'Saving...' : 'Save Sprint Summary' }}
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { SprintSummary } from '~/utils/types'

const props = defineProps<{
  retroId: string
  initialData?: SprintSummary | null
}>()

const emit = defineEmits<{
  saved: [SprintSummary]
}>()

const retroStore = useRetroStore()
const toastStore = useToastStore()

const total = ref(0)
const completed = ref(0)
const carryover = ref(0)
const saving = ref(false)

const deliveryRate = computed(() => {
  if (!total.value) return '--'
  return `${((completed.value / total.value) * 100).toFixed(1)}%`
})

watch(
  () => props.initialData,
  (data) => {
    if (data) {
      total.value = data.total_stories
      completed.value = data.completed
      carryover.value = data.carryover
    }
  },
  { immediate: true },
)

async function save() {
  saving.value = true
  try {
    await retroStore.saveSprintSummary(props.retroId, {
      total_stories: total.value,
      completed: completed.value,
      carryover: carryover.value,
    })
    toastStore.success('Sprint summary saved.')
    if (retroStore.sprintSummary) emit('saved', retroStore.sprintSummary)
  } catch {
    toastStore.error('Failed to save sprint summary.')
  } finally {
    saving.value = false
  }
}
</script>
