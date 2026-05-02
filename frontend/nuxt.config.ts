// https://nuxt.com/docs/api/configuration/nuxt-config
export default defineNuxtConfig({
  compatibilityDate: "2025-07-15",
  devtools: { enabled: true },
  ssr: false,
  modules: ["@nuxtjs/tailwindcss", "@pinia/nuxt"],
  css: ["~/assets/css/tailwind.css"],
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
})
