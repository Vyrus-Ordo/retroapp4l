<template>
  <form class="action-editor flex flex-col gap-3 rounded-lg border border-white/10 p-4" style="background: rgba(255,255,255,0.04)" @submit.prevent="$emit('save', { ...form })">
    <input v-model="form.title" required class="input-primary" placeholder="Action title" />
    <textarea v-model="form.description" class="input-primary" placeholder="Description (optional)" rows="2" />
    <div class="flex gap-2">
      <input v-model="form.responsible" class="input-primary flex-1" placeholder="Responsible" />
      <input v-model="form.dueDate" type="date" class="input-primary w-36" />
    </div>
    <div class="flex gap-2 justify-end mt-2">
      <button type="button" class="button-tertiary" @click="$emit('cancel')">Cancel</button>
      <button type="submit" class="button-primary">Save</button>
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
  border: 1px solid rgba(255,255,255,0.1);
  border-radius: 0.5rem;
  padding: 0.5rem 0.75rem;
  font-size: 1rem;
  color: #e4e4e7;
  background: rgba(255,255,255,0.04);
}
.input-primary:focus {
  outline: none;
  border-color: rgba(0,242,255,0.35);
  background: rgba(255,255,255,0.04);
}
</style>
