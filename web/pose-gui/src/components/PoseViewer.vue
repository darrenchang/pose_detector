<script setup lang="ts">
import { NLayoutContent } from 'naive-ui'
import { TresCanvas } from '@tresjs/core'
import SubComponent from './SubComponent.vue'
import { socket } from '@/socket'
import { usePostLandmarksStore } from '@/stores/poseLandmarks'

const poseLandmarksStore = usePostLandmarksStore()

let nose = [3, 3, 3]
socket.on('pose_landmarks', message => {
  if (message.length > 0) {
    let nose_l = message[0];
    nose = [3 + nose_l["x"], 3 + nose_l["y"], 3 + nose_l["z"]];
    poseLandmarksStore.updatePoseLandmarks(nose);
  }
  // console.log(poseLandmarksStore.getPoseLandmarks);
})
</script>

<template>
  <n-layout-content>
    <TresCanvas clear-color="#82DBC5">
      <TresPerspectiveCamera
        :position=nose
        :fov="45"
        :look-at="[0, 0, 0]"
      />
      <TresMesh ref="boxRef">
        <TresTorusGeometry :args="[1, 0.5, 16, 32]" />
        <TresMeshBasicMaterial color="orange" />
      </TresMesh>
      <TresAmbientLight :intensity="1" />
      <SubComponent />
    </TresCanvas>
  </n-layout-content>
</template>
