import { createConfigForNuxt } from "@nuxt/eslint-config/flat"
import prettier from "eslint-config-prettier"

export default createConfigForNuxt({
  features: {
    stylistic: false,
  },
}).append(
  prettier,
  {
    rules: {
      "vue/multi-word-component-names": "off",
      "vue/no-multiple-template-root": "off",
      "no-console": ["warn", { allow: ["warn", "error"] }],
    },
  },
  {
    ignores: [".nuxt/", ".output/", "node_modules/"],
  },
)
