export function useAuth() {
  const authStore = useAuthStore()

  onMounted(() => {
    authStore.init()
  })

  return {
    authStore,
    user: computed(() => authStore.user),
    isAuthenticated: computed(() => authStore.isAuthenticated),
  }
}