<script setup lang="ts">
import { CheckCircleIcon, ExclamationCircleIcon, ExclamationTriangleIcon, InformationCircleIcon, XMarkIcon } from "@heroicons/vue/24/solid"

import { useToastStore } from "~/stores/toast"

const toastStore = useToastStore()

const iconMap = {
  success: CheckCircleIcon,
  warning: ExclamationTriangleIcon,
  error: ExclamationCircleIcon,
  info: InformationCircleIcon,
}

const colorMap = {
  success: "bg-success-50 border-success-500 text-success-600",
  warning: "bg-warning-50 border-warning-500 text-warning-600",
  error: "bg-danger-50 border-danger-500 text-danger-600",
  info: "bg-brand-50 border-brand-500 text-brand-600",
}

const iconColorMap = {
  success: "text-success-500",
  warning: "text-warning-500",
  error: "text-danger-500",
  info: "text-brand-500",
}
</script>

<template>
  <Teleport to="body">
    <div
      aria-live="polite"
      aria-label="Notifications"
      class="pointer-events-none fixed bottom-6 right-6 z-50 flex flex-col gap-3"
    >
      <TransitionGroup
        name="toast"
        tag="div"
        class="flex flex-col gap-3"
      >
        <div
          v-for="toast in toastStore.toasts"
          :key="toast.id"
          role="alert"
          class="pointer-events-auto flex w-80 items-start gap-3 rounded-xl border p-4 shadow-lg"
          :class="colorMap[toast.type]"
        >
          <component :is="iconMap[toast.type]" class="h-5 w-5 flex-shrink-0" :class="iconColorMap[toast.type]" aria-hidden="true" />
          <p class="flex-1 text-sm font-medium">{{ toast.message }}</p>
          <button
            type="button"
            class="flex-shrink-0 rounded p-0.5 hover:bg-black/10 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-black"
            :aria-label="`Dismiss notification: ${toast.message}`"
            @click="toastStore.remove(toast.id)"
          >
            <XMarkIcon class="h-4 w-4" aria-hidden="true" />
          </button>
        </div>
      </TransitionGroup>
    </div>
  </Teleport>
</template>

<style scoped>
.toast-enter-active,
.toast-leave-active {
  transition: all 0.25s ease;
}
.toast-enter-from {
  opacity: 0;
  transform: translateX(1.5rem);
}
.toast-leave-to {
  opacity: 0;
  transform: translateX(1.5rem);
}
.toast-move {
  transition: transform 0.25s ease;
}
</style>
