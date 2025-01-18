<script setup lang="ts">
import { NLayoutContent } from 'naive-ui'
import { TresCanvas, useRenderLoop } from '@tresjs/core'
import { socket } from '@/socket'
import { shallowRef } from 'vue'
import { examplePoseLandmarks } from '@/composables/poseLandmarksInterface'

const { onLoop } = useRenderLoop()

const factor = 2
const poseLandmarks = examplePoseLandmarks

socket.on('pose_landmarks', message => {
  if (message.pose_landmarks.length <= 0) {
    return
  }
  Object.keys(poseLandmarks).forEach((key, index) => {
    const position = [
      message.pose_landmarks[index]['x'] * factor,
      message.pose_landmarks[index]['y'] * factor,
      message.pose_landmarks[index]['z'] * factor,
    ]
    poseLandmarks[key].position = position
  })
})

function smoothing(start: number, end: number, delta: number) {
  const speed = Math.min(Math.max(end - start * 2, 7), 10)
  const alpha = 1 - Math.exp(-speed * delta)
  const threshold = 0.3
  if (Math.abs(end - start) > threshold) {
    return end
  } else {
    return start + (end - start) * alpha
  }
}

const landmarksGroupRef = shallowRef()
onLoop(({ delta, elapsed }) => {
  if (!landmarksGroupRef.value) {
    return
  }
  const landmarks: any[] = landmarksGroupRef.value.children
  landmarks.forEach((item, _) => {
    const newX = 1 - poseLandmarks[item.name].position[0]
    item.position.x = smoothing(item.position.x, newX, delta)
    const newY = 1 - poseLandmarks[item.name].position[1]
    item.position.y = smoothing(item.position.y, newY, delta)
    const newZ = 1 - poseLandmarks[item.name].position[2]
    item.position.z = smoothing(item.position.z, newZ, delta)
  })
})
</script>

<template>
  <n-layout-content>
    <TresCanvas clear-color="#82DBC5">
      <TresPerspectiveCamera :position="[0, 0, 6]" :fov="45" :look-at="[0, 0, 0]" />
      <TresGroup ref="landmarksGroupRef" :position="[0, 0, 0]">
        <TresMesh v-for="(landmark, key) in poseLandmarks" :name="key" :key="key" :position="[-1, -1, -1]">
          <TresBoxGeometry :args="landmark.cubeSize" />
          <TresMeshNormalMaterial :color="landmark.cubeColor" />
        </TresMesh>
      </TresGroup>
      <TresAmbientLight :intensity="1" />
    </TresCanvas>
  </n-layout-content>
</template>
