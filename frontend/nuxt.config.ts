// https://nuxt.com/docs/api/configuration/nuxt-config
export default defineNuxtConfig({
  ssr: false, // SPA only
  compatibilityDate: "2025-07-15",
  devtools: { enabled: true },
  experimental: {
    appManifest: false,
  },
  components: [
    { path: "~/components/layout", pathPrefix: false },
    { path: "~/components/retro", pathPrefix: false, ignore: ["FocusCard.vue", "board/**"] },
    { path: "~/components/board", pathPrefix: false },
    { path: "~/components/participants", pathPrefix: false },
    { path: "~/components/forms", pathPrefix: false },
    { path: "~/components", pathPrefix: false, pattern: "*.vue" },
  ],
  modules: ["@nuxtjs/tailwindcss", "@pinia/nuxt", "@nuxtjs/turnstile"],
  turnstile: {
    siteKey: process.env.NUXT_PUBLIC_TURNSTILE_SITE_KEY || "1x00000000000000000000AA",
  },
  css: ["~/assets/css/tokens.css", "~/assets/css/tailwind.css"],
  app: {
    head: {
      title: "RetroApp 4L",
      meta: [
        { name: "viewport", content: "width=device-width, initial-scale=1" },
        {
          name: "description",
          content: "RetroApp 4L frontend for agile retrospectives.",
        },
      ],
    },
  },
  runtimeConfig: {
    public: {
      apiBase: process.env.NUXT_PUBLIC_API_BASE || "http://localhost:8000/api",
      wsBase: process.env.NUXT_PUBLIC_WS_BASE || "ws://localhost:8000/ws",
    },
  },
  tailwindcss: {
    cssPath: "~/assets/css/tailwind.css",
    viewer: false,
  },
  vite: {
    server: {
      hmr: {
        port: 24678,
        host: '127.0.0.1',
      },
    },
  },
})
