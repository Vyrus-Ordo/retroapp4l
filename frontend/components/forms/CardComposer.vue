<script setup lang="ts">
import type { Card, CardColumn } from "~/utils/types"

const props = defineProps<{
  modelValue: boolean
  initialCard?: Card | null
  initialColumn?: CardColumn
}>()

const emit = defineEmits<{
  'update:modelValue': [value: boolean]
  submit: [payload: { id?: string; content: string; column: CardColumn }]
}>()

const content = ref(props.initialCard?.content || "")
const column = ref<CardColumn>(props.initialCard?.column || props.initialColumn || "loved")

watch(
  [() => props.initialCard, () => props.initialColumn],
  ([card, col]) => {
    content.value = card?.content || ""
    column.value = card?.column || col || "loved"
  },
  { immediate: true },
)

const selectColorClass = computed(() => {
  if (column.value === 'loved') return 'border-[#22c55e]/50 text-[#22c55e]'
  if (column.value === 'loathed') return 'border-[#ef4444]/50 text-[#ef4444]'
  if (column.value === 'longed') return 'border-[#60a5fa]/50 text-[#60a5fa]'
  return 'border-white/15 text-zinc-400'
})

function close() {
  emit("update:modelValue", false)
}

function handleSubmit() {
  emit("submit", {
    id: props.initialCard?.id,
    content: content.value,
    column: column.value,
  })
  close()
}
</script>

<template>
  <div v-if="modelValue" class="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-sm px-4">
    <div class="w-full max-w-xl rounded-xl border border-[#00f2ff]/15 p-6" style="background: rgba(10,10,10,0.95)">
      <h2 class="text-lg font-light text-white">{{ initialCard ? 'Edit card' : 'Add card' }}</h2>
      <div class="mt-4 space-y-4">
        <select v-model="column" class="field-input font-light transition-colors disabled:opacity-60 disabled:cursor-not-allowed" :class="selectColorClass" :disabled="!initialCard && !!initialColumn">
          <option value="loved" class="bg-[#0a0a0a] text-zinc-200 font-normal">Liked</option>
          <option value="loathed" class="bg-[#0a0a0a] text-zinc-200 font-normal">Loathed</option>
          <option value="longed" class="bg-[#0a0a0a] text-zinc-200 font-normal">Longed for</option>
          <option value="learned" class="bg-[#0a0a0a] text-zinc-200 font-normal">Learned</option>
        </select>
        <textarea v-model="content" class="field-input min-h-32" maxlength="500" placeholder="Write a concise card." />
      </div>
      <div class="mt-6 flex justify-end gap-3">
        <button class="button-secondary" type="button" @click="close">Cancel</button>
        <button class="button-primary" type="button" @click="handleSubmit">Save</button>
      </div>
    </div>
  </div>
</template>
