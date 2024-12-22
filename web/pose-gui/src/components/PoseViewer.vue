<script setup lang="ts">
import { NLayoutContent } from 'naive-ui'
import { TresCanvas, useRenderLoop } from '@tresjs/core'
import { socket } from '@/socket'
import { shallowRef } from 'vue';

const { onLoop} = useRenderLoop()

let nose = [0, 0, 0]
let left = [0, 0, 0]
socket.on('pose_landmarks', message => {
  if (message.length <= 0) {
    return;
  }
  let nose_l = message[0];
  let left_l = message[15];
  let factor = 2;
  nose = [
    nose_l["x"] * factor,
    nose_l["y"] * factor,
    nose_l["z"] * factor,
  ];
  left = [
    left_l["x"] * factor,
    left_l["y"] * factor,
    left_l["z"] * factor,
  ];
})


const noseRef = shallowRef()
const leftRef = shallowRef()
onLoop(({ delta, elapsed }) => {
  if (!noseRef.value) {
    return;
  }
    noseRef.value.position.x = 1 - nose[0];
    noseRef.value.position.y = 1 - nose[1];
    leftRef.value.position.x = 1 - left[0];
    leftRef.value.position.y = 1 - left[1];
    leftRef.value.position.z = 1 - left[2];
})
</script>

<template>
  <n-layout-content>
    <TresCanvas clear-color="#82DBC5">
      <TresPerspectiveCamera
        :position="[0, 0, 6]"
        :fov="45"
        :look-at="[0, 0, 0]"
      />
      <TresMesh ref="noseRef" :position="[0, 0, 0]">
        <TresBoxGeometry :args="[0.1, 0.1, 0.1]" />
        <TresMeshNormalMaterial color="orange" />
      </TresMesh>
      <TresMesh ref="leftRef" :position="[0, 0, 0]">
        <TresBoxGeometry :args="[0.1, 0.1, 0.1]" />
        <TresMeshNormalMaterial color="orange" />
      </TresMesh>
      <TresAmbientLight :intensity="1" />
    </TresCanvas>
  </n-layout-content>
</template>
