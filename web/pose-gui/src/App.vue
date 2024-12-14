<template>
  <n-layout>
    <n-layout-header>Pose</n-layout-header>
    <RouterView />
  </n-layout>
</template>

<script setup lang="ts">
import { RouterView } from 'vue-router'
import {
  NLayout,
  NLayoutHeader,
} from 'naive-ui'

</script>

<style>
.n-layout-sider {
  background: rgba(128, 128, 128, 0.3);
}

.n-layout-content {
  background: rgba(255, 128, 128, 0.4);
  height: calc(100vh - var(--header-height));
}
</style>
