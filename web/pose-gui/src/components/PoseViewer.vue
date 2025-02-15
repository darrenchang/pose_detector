<script setup lang="ts">
import { NLayoutContent, NButton } from 'naive-ui'
import { TresCanvas, useRenderLoop } from '@tresjs/core'
import { socket } from '@/socket'
import { shallowRef, ref } from 'vue'
import { examplePoseLandmarks } from '@/composables/poseLandmarksInterface'

const { onLoop } = useRenderLoop()

const canvas_factor = 2
const poseLandmarks = examplePoseLandmarks
let paused = ref(false);


socket.on('pose_landmarks', message => {
  if (message.pose_landmarks.length <= 0) {
    return
  }
  Object.keys(poseLandmarks).forEach((key, index) => {
    const position = [
      message.pose_landmarks[index]['x'],
      message.pose_landmarks[index]['y'],
      message.pose_landmarks[index]['z'],
    ]
    poseLandmarks[key].position = position
  })
})

function pauseView() {
  paused.value = !paused.value
}

function saveLandmarks() {
  const landmarks_canvas: any[] = landmarksGroupRef.value.children
  let landmarks_pose = landmarks_canvas.reduce((accumulator, cur) => {
    accumulator.push({
      "x": CanvasToPoseCoord(cur.position.x, canvas_factor),
      "y": CanvasToPoseCoord(cur.position.y, canvas_factor),
      "z": CanvasToPoseCoord(cur.position.z, canvas_factor),
    })
    return accumulator
  }, [])
  console.log(landmarks_pose)
}

function poseToCanvasCoord(coord: number, factor: number) {
  // Convert landmarks from pose models coord to views canvas coord
  return 1 - coord * factor
}

function CanvasToPoseCoord(coord: number, factor: number) {
  // Convert landmarks from views canvas coord to models coord cord
  return (1 + coord) / factor
}

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
  if (paused.value) {
    return
  }
  if (!landmarksGroupRef.value) {
    return
  }
  const landmarks: any[] = landmarksGroupRef.value.children
  landmarks.forEach((item, _) => {
    const newX = poseToCanvasCoord(poseLandmarks[item.name].position[0], canvas_factor)
    const newY = poseToCanvasCoord(poseLandmarks[item.name].position[1], canvas_factor)
    const newZ = poseToCanvasCoord(poseLandmarks[item.name].position[2], canvas_factor)
    item.position.x = smoothing(item.position.x, newX, delta)
    item.position.y = smoothing(item.position.y, newY, delta)
    item.position.z = smoothing(item.position.z, newZ, delta)
  })
})
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
  </n-layout-content>
</template>

<style scoped>
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
