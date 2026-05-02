<template>
  <div
    class="avatar-circle flex items-center justify-center rounded-full font-semibold select-none"
    :style="{
      width: sizePx,
      height: sizePx,
      background: color ? `var(--ds-${color}-500)` : 'var(--ds-gray-200)',
      color: '#fff',
      fontSize: fontSize,
    }"
    :title="name"
  >
    <span>{{ initials }}</span>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps<{
  name: string
  size?: 28 | 32 | 36 | 48
  color?: 'brand' | 'success' | 'warning' | 'danger' | 'gray'
}>()

const sizePx = computed(() => `${props.size || 36}px`)
const fontSize = computed(() => {
  if ((props.size || 36) >= 48) return '1.5rem'
  if ((props.size || 36) >= 36) return '1.15rem'
  return '1rem'
})
const initials = computed(() => {
  if (!props.name) return ''
  const parts = props.name.trim().split(' ')
  if (parts.length === 1) return parts[0].slice(0, 2).toUpperCase()
  return (parts[0][0] + parts[parts.length - 1][0]).toUpperCase()
})
</script>

<style scoped>
.avatar-circle {
  box-shadow: 0 1px 2px rgba(15,23,42,.06);
  transition: background 0.2s;
}
</style>
