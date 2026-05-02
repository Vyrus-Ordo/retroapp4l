<script setup lang="ts">
const route = useRoute()

await navigateTo(
  {
    path: "/auth/login",
    query: route.query,
    hash: route.hash,
  },
  {
    replace: true,
  },
)
</script>

<template>
  <div />
</template>