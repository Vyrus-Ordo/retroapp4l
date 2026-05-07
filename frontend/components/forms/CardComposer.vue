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
  if (column.value === "loved") return "bg-success-600 text-white border-success-600 focus:border-success-600 focus:ring-success-600"
  if (column.value === "loathed") return "bg-warning-500 text-white border-warning-500 focus:border-warning-500 focus:ring-warning-500"
  if (column.value === "longed") return "bg-brand-500 text-white border-brand-500 focus:border-brand-500 focus:ring-brand-500"
  return "bg-slate-600 text-white border-slate-600 focus:border-slate-600 focus:ring-slate-600"
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
  <div v-if="modelValue" class="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/40 px-4">
    <div class="w-full max-w-xl rounded-xl bg-white p-6 shadow-lg">
      <h2 class="text-lg font-semibold text-slate-900">{{ initialCard ? 'Edit card' : 'Add card' }}</h2>
      <div class="mt-4 space-y-4">
        <select v-model="column" class="field-input font-medium transition-colors disabled:opacity-60 disabled:cursor-not-allowed" :class="selectColorClass" :disabled="!initialCard && !!initialColumn">
          <option value="loved" class="bg-white text-slate-900 font-normal">Liked</option>
          <option value="loathed" class="bg-white text-slate-900 font-normal">Loathed</option>
          <option value="longed" class="bg-white text-slate-900 font-normal">Longed for</option>
          <option value="learned" class="bg-white text-slate-900 font-normal">Learned</option>
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