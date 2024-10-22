<script setup lang="ts">
import { NLayout, NLayoutSider, NLayoutContent } from 'naive-ui'
</script>

<template>
  <n-layout has-sider>
    <n-layout-sider
      content-style="
        padding: 24px;
      "
    >
      a_pose_name
    </n-layout-sider>
    <n-layout-content
      content-style="
        padding: 24px;
      "
    >
      hello
    </n-layout-content>
  </n-layout>
</template>
<style scoped>
.n-layout-sider {
  background: rgba(128, 128, 128, 0.3);
}

.n-layout-content {
  background: rgba(255, 128, 128, 0.4);
  min-height: calc(100vh - var(--header-height));
}
</style>
