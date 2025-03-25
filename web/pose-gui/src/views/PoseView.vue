<template>
  <n-layout-content>
    <n-layout has-sider>
      <n-layout-sider class="n-layout-sider--left-placement" bordered collapse-mode="width" :width="240"
        :native-scrollbar="false" show-trigger>
        <n-menu
          :options="menuOptionsLandmarkSource"
          :default-value="defaultLandmarkSource"
          @update:value="handleUpdateKeys"
        />
      </n-layout-sider>
      <n-layout-content>
        <PoseViewer />
      </n-layout-content>
      <n-layout-sider class="n-layout-sider--right-placement" bordered collapse-mode="width" :width="240"
        :native-scrollbar="false" show-trigger>
        <span></span>
      </n-layout-sider>
    </n-layout>
  </n-layout-content>
</template>

<script setup lang="ts">
import PoseViewer from '@/components/PoseViewer.vue'
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
