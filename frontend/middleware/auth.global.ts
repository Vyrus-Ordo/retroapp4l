export default defineNuxtRouteMiddleware((to) => {
  const authStore = useAuthStore()
  authStore.init()

  const publicPaths = ["/auth/login", "/auth/register", "/join"]
  const isInvitePath = to.path.startsWith("/retro/invite/")
  const requiresAuth = !publicPaths.includes(to.path) && !isInvitePath
  const isGuestSession = authStore.isGuestSession

  if (requiresAuth && !authStore.isAuthenticated) {
    return navigateTo(`/auth/login?redirect=${encodeURIComponent(to.fullPath)}`)
  }

  if (isGuestSession) {
    const guestAllowed = to.path.startsWith("/retro/") && to.path !== "/retro/create"
    if (!publicPaths.includes(to.path) && !isInvitePath && !guestAllowed) {
      return navigateTo("/join")
    }
  }

  if (authStore.isAuthenticated && !isGuestSession && ["/auth/login", "/auth/register"].includes(to.path)) {
    return navigateTo("/")
  }
})