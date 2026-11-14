<script setup lang="ts">
import ActionsReviewFilters from "~/components/actions/ActionsReviewFilters.vue"
import ActionsReviewTable from "~/components/actions/ActionsReviewTable.vue"
import ActionEditModal from "~/components/actions/ActionEditModal.vue"
import type { ActionReviewFilters as ActionReviewFilterState, ActionReviewPatch } from "~/stores/actionsReview"
import type { ActionReviewItem } from "~/utils/types"

const store = useActionsReviewStore()
const toastStore = useToastStore()

const modalOpen = ref(false)
const saving = ref(false)
const modalError = ref<string | null>(null)

onMounted(async () => {
  await Promise.all([store.fetchTeams(), store.fetchActions()])
})

async function applyFilters(patch: Partial<ActionReviewFilterState>) {
  store.filters = { ...store.filters, ...patch }
  store.page = 1
  await store.fetchActions()
}

async function handleResetFilters() {
  store.resetFilters()
  await store.fetchActions()
}

async function handlePageChange(page: number) {
  store.page = page
  await store.fetchActions()
}

async function handleRetry() {
  await store.fetchActions()
}

async function openEdit(item: ActionReviewItem) {
  modalError.value = null
  try {
    await store.fetchDetail(item.id)
    modalOpen.value = true
  } catch (error) {
    toastStore.error(error instanceof Error ? error.message : "Unable to load this action.")
  }
}

function closeModal() {
  if (saving.value) return
  modalOpen.value = false
  store.clearSelection()
}

async function submitEdit(patch: ActionReviewPatch) {
  if (!store.selected) return

  saving.value = true
  modalError.value = null
  try {
    await store.updateAction(store.selected.id, patch)
    toastStore.success("Action updated.")
    modalOpen.value = false
    store.clearSelection()
  } catch (error) {
    modalError.value = error instanceof Error ? error.message : "Unable to update this action."
  } finally {
    saving.value = false
  }
}
</script>

<template>
  <AppShell>
    <section class="panel p-6 lg:p-8">
      <div class="flex flex-wrap items-start justify-between gap-4">
        <div>
          <p class="text-xs font-light text-[#00f2ff]/70">Actions</p>
          <h1 class="mt-3 text-2xl font-light text-white">Actions Review</h1>
          <p class="mt-2 max-w-2xl text-sm text-zinc-500">
            Pending actions across all your teams. Facilitators can edit the ones from closed retrospectives.
          </p>
        </div>
      </div>

      <div class="mt-6">
        <ActionsReviewFilters :filters="store.filters" :teams="store.teams" @patch="applyFilters" @reset="handleResetFilters" />
      </div>

      <div v-if="store.error" class="mt-4 flex flex-wrap items-center justify-between gap-3 rounded-lg border border-red-400/40 p-4 text-sm text-red-300">
        <p>{{ store.error }}</p>
        <button type="button" class="button-secondary py-1.5 text-sm" @click="handleRetry">Retry</button>
      </div>

      <p v-else-if="store.loading" class="mt-6 text-sm text-zinc-500">Loading actions…</p>

      <ActionsReviewTable
        v-else
        :items="store.items"
        :count="store.count"
        :page="store.page"
        :page-size="store.pageSize"
        @edit="openEdit"
        @page-change="handlePageChange"
      />
    </section>

    <ActionEditModal
      v-if="modalOpen && store.selected"
      :action="store.selected"
      :saving="saving"
      :error="modalError"
      @close="closeModal"
      @submit="submitEdit"
    />
  </AppShell>
</template>
