<script setup lang="ts">
import { NLayoutContent } from 'naive-ui'
import { TresCanvas, useRenderLoop } from '@tresjs/core'
import { socket } from '@/socket'
import { shallowRef } from 'vue'

const { onLoop } = useRenderLoop()

interface poseLandmarksInterface {
  [key: string]: number[];
}
const factor = 2
let poseLandmarks: poseLandmarksInterface = {
  nose: [0, 0, 0],
  leftEyeInner: [0, 0, 0],
  leftEye: [0, 0, 0],
  leftEyeOuter: [0, 0, 0],
  rightEyeInner: [0, 0, 0],
  rightEye: [0, 0, 0],
  rightEyeOuter: [0, 0, 0],
  leftEar: [0, 0, 0],
  rightEar: [0, 0, 0],
  mouthLeft: [0, 0, 0],
  mouthRight: [0, 0, 0],
  leftShoulder: [0, 0, 0],
  rightShoulder: [0, 0, 0],
  leftElbow: [0, 0, 0],
  rightElbow: [0, 0, 0],
  leftWrist: [0, 0, 0],
  rightWrist: [0, 0, 0],
  leftPinky: [0, 0, 0],
  rightPinky: [0, 0, 0],
  leftIndex: [0, 0, 0],
  rightIndex: [0, 0, 0],
  leftThumb: [0, 0, 0],
  rightThumb: [0, 0, 0],
  leftHip: [0, 0, 0],
  rightHip: [0, 0, 0],
  leftKnee: [0, 0, 0],
  rightKnee: [0, 0, 0],
  leftAnkle: [0, 0, 0],
  rightAnkle: [0, 0, 0],
  leftHeel: [0, 0, 0],
  rightHeel: [0, 0, 0],
  leftFootIndex: [0, 0, 0],
  rightFootIndex: [0, 0, 0],
}

socket.on('pose_landmarks', message => {
  if (message.length <= 0) {
    return
  }
  Object.keys(poseLandmarks).forEach((key, index) => {
    const position = [message[index]['x'] * factor, message[index]['y'] * factor, message[index]['z'] * factor];
    poseLandmarks[key] = position;
  });
})

function lerp(start: number, end: number, delta: number) {
  const smoothingFactor = 10
  const threshold = 0.3;
  if (Math.abs(end - start) > threshold) {
    return end;
  } else {
    return start + (end - start) * delta * smoothingFactor;
  }
}

const landmarksGroupRef = shallowRef()
onLoop(({ delta, elapsed }) => {
  if (!landmarksGroupRef.value) {
    return
  }
  const landmarks: any[] = landmarksGroupRef.value.children;
  landmarks.forEach((item, _) => {
    const newX = 1 - poseLandmarks[item.name][0];
    item.position.x = lerp(item.position.x, newX, delta);
    const newY = 1 - poseLandmarks[item.name][1];
    item.position.y = lerp(item.position.y, newY, delta);
    const newZ = 1 - poseLandmarks[item.name][2];
    item.position.z = lerp(item.position.z, newZ, delta);
  })
})
</script>

<template>
  <n-layout-content>
    <TresCanvas clear-color="#82DBC5">
      <TresPerspectiveCamera :position="[0, 0, 6]" :fov="45" :look-at="[0, 0, 0]" />
      <TresGroup ref="landmarksGroupRef" :position="[0,0,0]">
        <TresMesh v-for="(landmark, key) in poseLandmarks" :name="key" :key="key" :position="[-1, -1, -1]">
          <TresBoxGeometry :args="[0.1, 0.1, 0.1]" />
          <TresMeshNormalMaterial color="orange" />
        </TresMesh>
      </TresGroup>
      <TresAmbientLight :intensity="1" />
    </TresCanvas>
  </n-layout-content>
</template>
