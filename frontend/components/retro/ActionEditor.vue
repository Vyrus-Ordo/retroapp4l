<template>
  <form class="action-editor flex flex-col gap-3 bg-white rounded-lg border border-gray-200 p-4 shadow-sm" @submit.prevent="$emit('save', { ...form })">
    <input v-model="form.title" required class="input-primary" placeholder="Título da ação" />
    <textarea v-model="form.description" class="input-primary" placeholder="Descrição (opcional)" rows="2" />
    <div class="flex gap-2">
      <input v-model="form.responsible" class="input-primary flex-1" placeholder="Responsável" />
      <input v-model="form.dueDate" type="date" class="input-primary w-36" />
    </div>
    <div class="flex gap-2 justify-end mt-2">
      <button type="button" class="button-tertiary" @click="$emit('cancel')">Cancelar</button>
      <button type="submit" class="button-primary">Salvar</button>
    </div>
  </form>
</template>

<script setup lang="ts">
import { reactive, watchEffect } from 'vue'
const props = defineProps({
  action: Object
})
const emit = defineEmits(['save', 'cancel'])
const form = reactive({
  title: '',
  description: '',
  responsible: '',
  dueDate: ''
})
watchEffect(() => {
  if (props.action) Object.assign(form, props.action)
})
</script>

<style scoped>
.action-editor {
  min-width: 260px;
}
.input-primary {
  border: 1px solid var(--ds-border);
  border-radius: 0.5rem;
  padding: 0.5rem 0.75rem;
  font-size: 1rem;
  color: var(--ds-text);
  background: var(--ds-bg);
}
.input-primary:focus {
  outline: none;
  border-color: var(--ds-primary);
  background: var(--ds-bg);
}
</style>
