export default defineNuxtRouteMiddleware((to) => {
  const authStore = useAuthStore()
  authStore.init()

  const publicPaths = ["/", "/auth/login", "/auth/register", "/join"]
  const isInvitePath = to.path.startsWith("/retro/invite/")
  const requiresAuth = !publicPaths.includes(to.path) && !isInvitePath

  if (requiresAuth && !authStore.isAuthenticated) {
    return navigateTo(`/auth/login?redirect=${encodeURIComponent(to.fullPath)}`)
  }

  if (authStore.isAuthenticated && ["/auth/login", "/auth/register"].includes(to.path)) {
    return navigateTo("/")
  }
})