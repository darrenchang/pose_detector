<script setup lang="ts">
import { NLayoutContent, NButton } from 'naive-ui'
import { TresCanvas } from '@tresjs/core'
import { ref, shallowRef } from 'vue'
import PoseScene from '@/components/PoseScene.vue'
import { getInfo } from '@/composables/restApiService'

const paused = ref(false)
const sceneRef = shallowRef()

function pauseView() {
  paused.value = !paused.value
}

function saveLandmarks() {
  const landmarks_pose = sceneRef.value?.getPoseLandmarks() ?? []
  console.log(landmarks_pose)
  getInfo().then((res) => {
    console.log(res)
  })
}
</script>

<template>
  <n-layout-content>
    <div class="viewer-overlay">
      <div class="hud">
        <n-button @click="pauseView" class="view-control-button" type="primary">{{ paused ? 'Start' : 'Pause'}}</n-button>
        <n-button @click="saveLandmarks" class="view-control-button" type="primary">Save Landmarks</n-button>
      </div>
    </div>
    <n-layout-content>
      <!-- render-mode="on-demand": PoseScene only invalidates while the
           landmarks are still moving, so a still or absent subject draws no
           frames. -->
      <TresCanvas render-mode="on-demand">
        <PoseScene ref="sceneRef" :paused="paused" />
      </TresCanvas>
    </n-layout-content>
  </n-layout-content>
</template>

<style scoped>
.n-layout-content {
  background: #82DBC5;
}
.viewer-overlay {
  position: absolute;
  z-index: 256;
}
.hud {
  margin: 15px;
}
.hud .view-control-button:not(:first-child):not(:last-child) {
  margin: 0 15px;
}
.hud .view-control-button:nth-child(2) {
  margin-left: 15px;
}
</style>
