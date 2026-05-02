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
  () => props.initialCard,
  (card) => {
    content.value = card?.content || ""
    column.value = card?.column || props.initialColumn || "loved"
  },
  { immediate: true },
)

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
        <select v-model="column" class="field-input">
          <option value="loved">Liked</option>
          <option value="loathed">Loathed</option>
          <option value="longed">Longed for</option>
          <option value="learned">Learned</option>
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