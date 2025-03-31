<template>
  <n-layout-content>
    <PdfViewer />
  </n-layout-content>
</template>

<script setup lang="ts">
import PdfViewer from '@/components/PdfViewer.vue'
import { onMounted, onUnmounted } from 'vue'
import type { Component } from 'vue'
import { NIcon } from 'naive-ui'
import { h } from 'vue'
import { NLayout, NLayoutSider, NLayoutContent, NMenu } from 'naive-ui'
import { VideocamOutline } from '@vicons/ionicons5'
import { connect, sub, disconnect } from '@/composables/socketManager'

function renderIcon(icon: Component) {
  return () => h(NIcon, null, { default: () => h(icon) })
}

const defaultLandmarkSource = 'host_cam'
const menuOptionsLandmarkSource = [
  {
    label: 'Host Cam',
    key: 'host_cam',
    icon: renderIcon(VideocamOutline),
  },
]

onMounted(async () => {
  connect();
  sub(defaultLandmarkSource);
})

onUnmounted(async () => {
  disconnect();
})

function handleUpdateKeys(key: string) {
  connect();
  sub(key);
}
</script>
