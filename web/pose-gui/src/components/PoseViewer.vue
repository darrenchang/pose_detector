<script setup lang="ts">
import { NLayoutContent } from 'naive-ui'
import { TresCanvas, useRenderLoop } from '@tresjs/core'
import { socket } from '@/socket'
import { usePostLandmarksStore } from '@/stores/poseLandmarks'
import { shallowRef } from 'vue';

const { onLoop} = useRenderLoop()
const poseLandmarksStore = usePostLandmarksStore()

let nose = [3, 3, 3]
socket.on('pose_landmarks', message => {
  if (message.length <= 0) {
    return;
  }
  let nose_l = message[0];
  console.log(nose_l);
  let factor = 2
  nose = [
    nose_l["x"] * factor,
    nose_l["y"] * factor,
    nose_l["z"] * factor,
  ];
  poseLandmarksStore.updatePoseLandmarks(nose);
})


const cubeRef = shallowRef()
onLoop(({ delta, elapsed }) => {
  if (!cubeRef.value) {
    return;
  }
    cubeRef.value.position.x = 1 - nose[0];
    cubeRef.value.position.y = 1 - nose[1];
})
</script>

<template>
  <n-layout-content>
    <TresCanvas clear-color="#82DBC5">
      <TresPerspectiveCamera
        :position="[0, 0, -6]"
        :fov="45"
        :look-at="[0, 0, 0]"
      />
      <TresMesh ref="cubeRef" :position="[0, 0, 0]">
        <TresBoxGeometry />
        <TresMeshNormalMaterial color="orange" />
      </TresMesh>
      <TresAmbientLight :intensity="1" />
    </TresCanvas>
  </n-layout-content>
</template>
