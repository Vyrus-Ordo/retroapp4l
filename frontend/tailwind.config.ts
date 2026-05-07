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
        // Neon accent
        neon: {
          cyan: "#00f2ff",
        },
        // Brand agora é cyan neon
        brand: {
          50: "rgba(0,242,255,0.05)",
          100: "rgba(0,242,255,0.10)",
          200: "rgba(0,242,255,0.20)",
          300: "rgba(0,242,255,0.35)",
          400: "rgba(0,242,255,0.55)",
          500: "#00f2ff",
          600: "rgba(0,242,255,0.80)",
          700: "rgba(0,242,255,0.60)",
          800: "rgba(0,242,255,0.40)",
          900: "rgba(0,242,255,0.20)",
        },
        // Semântica colunas
        col: {
          loved:   "#22c55e",
          loathed: "#ef4444",
          longed:  "#60a5fa",
          learned: "#a1a1aa",
        },
        success: {
          500: "#22c55e",
          600: "#16a34a",
          700: "#15803d",
        },
        warning: {
          500: "#f59e0b",
          600: "#d97706",
        },
        danger: {
          500: "#ef4444",
          600: "#dc2626",
        },
        gray: {
          50:  "rgba(255,255,255,0.03)",
          100: "rgba(255,255,255,0.06)",
          200: "rgba(255,255,255,0.10)",
          300: "#71717a",
          400: "#a1a1aa",
          500: "#d4d4d8",
          600: "#e4e4e7",
          700: "#3f3f46",
          800: "#27272a",
          900: "#18181b",
          950: "#09090b",
        },
      },
      fontFamily: {
        sans: ["Poppins", "sans-serif"],
        mono: ['"JetBrains Mono"', "monospace"],
      },
      boxShadow: {
        card: "0 0 0 1px rgba(0,242,255,0.08)",
        "card-md": "0 0 16px rgba(0,242,255,0.12)",
        glow: "0 0 16px rgba(0,242,255,0.25)",
        "glow-lg": "0 0 32px rgba(0,242,255,0.40)",
      },
    },
  },
} satisfies Config