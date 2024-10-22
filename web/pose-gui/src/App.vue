<script setup lang="ts">
import { RouterView } from 'vue-router'
import { NLayout, NLayoutHeader, NLayoutContent } from 'naive-ui'
</script>

<template>
  <n-layout>
    <n-layout-header>Pose</n-layout-header>
    <n-layout-content>
      <RouterView />
    </n-layout-content>
  </n-layout>
</template>

<style scoped>
.n-layout-content {
  background: rgba(128, 128, 128, 0.4);
}
</style>
