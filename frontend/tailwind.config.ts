import type { Config } from "tailwindcss"

export default {
  content: [
    "./app.vue",
    "./components/**/*.{vue,js,ts}",
    "./composables/**/*.{js,ts}",
    "./layouts/**/*.vue",
    "./middleware/**/*.{js,ts}",
    "./pages/**/*.vue",
    "./plugins/**/*.{js,ts}",
    "./stores/**/*.{js,ts}",
    "./utils/**/*.{js,ts}",
  ],
  theme: {
    extend: {
      colors: {
        brand: {
          50: "#eff6ff",
          100: "#dbeafe",
          500: "#3b82f6",
          600: "#2563eb",
          700: "#1d4ed8",
        },
        success: {
          50: "#f0fdf4",
          500: "#22c55e",
          600: "#16a34a",
        },
        warning: {
          50: "#fff7ed",
          500: "#f97316",
          600: "#ea580c",
        },
        danger: {
          50: "#fef2f2",
          500: "#ef4444",
          600: "#dc2626",
        },
      },
      fontFamily: {
        sans: ["Inter", "sans-serif"],
      },
      boxShadow: {
        DEFAULT: "0 1px 2px 0 rgb(15 23 42 / 0.08)",
      },
    },
  },
} satisfies Config