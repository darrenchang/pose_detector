<script setup lang="ts">
import { NLayoutContent, NButton } from 'naive-ui'
import { TresCanvas, useRenderLoop } from '@tresjs/core'
import { shallowRef, ref } from 'vue'
import { poseLandmarks } from '@/interface/poseLandmarksInterface'
import { leftHandLandmarks, rightHandLandmarks } from '@/interface/handLandmarksInterface'
import { getInfo } from '@/composables/restApiService'

const { onLoop } = useRenderLoop()

const canvas_factor = 2
let paused = ref(false);

function pauseView() {
  paused.value = !paused.value
}

function saveLandmarks() {
  const landmarks_canvas: any[] = poseLandmarksGroupRef.value.children
  let landmarks_pose = landmarks_canvas.reduce((accumulator, cur) => {
    accumulator.push({
      "x": CanvasToPoseCoord(cur.position.x, canvas_factor),
      "y": CanvasToPoseCoord(cur.position.y, canvas_factor),
      "z": CanvasToPoseCoord(cur.position.z, canvas_factor),
    })
    return accumulator
  }, [])
  console.log(landmarks_pose)
  getInfo().then((res) => {
    console.log(res)
  })
}

function poseToCanvasCoord(coord: number, factor: number) {
  // Convert landmarks from pose models coord to views canvas coord
  return 1 - coord * factor
}

function CanvasToPoseCoord(coord: number, factor: number) {
  // Convert landmarks from views canvas coord to models coord cord
  return (1 + coord) / factor
}

function getCenter(points: number[][]): {"x": number, "y": number, "z": number} {
  const pointSum = points.reduce((acc, cur) => {
    acc["x_sum"] += cur[0]
    acc["y_sum"] += cur[1]
    acc["z_sum"] += cur[2]
    return acc
  }, {"x_sum": 0, "y_sum": 0, "z_sum": 0})
  const center = {
    x: pointSum["x_sum"] / points.length,
    y: pointSum["y_sum"] / points.length,
    z: pointSum["z_sum"] / points.length,
  }
  return center
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

const poseLandmarksGroupRef = shallowRef()
const leftHandLandmarksGroupRef = shallowRef()
const rightHandLandmarksGroupRef = shallowRef()
onLoop(({ delta, elapsed }) => {
  if (paused.value) {
    return
  }
  if (!poseLandmarksGroupRef.value || !leftHandLandmarksGroupRef.value) {
    return
  }
  // Pose landmarks
  const poseLandmarksAnimate: any[] = poseLandmarksGroupRef.value.children
  poseLandmarksAnimate.forEach((item, _) => {
    const newX = poseToCanvasCoord(poseLandmarks[item.name].position[0], canvas_factor)
    const newY = poseToCanvasCoord(poseLandmarks[item.name].position[1], canvas_factor)
    const newZ = poseToCanvasCoord(poseLandmarks[item.name].position[2], canvas_factor)
    item.position.x = smoothing(item.position.x, newX, delta)
    item.position.y = smoothing(item.position.y, newY, delta)
    item.position.z = smoothing(item.position.z, newZ, delta)
  })
  // Hand landmarks
  // left hand
  const leftPalm = getCenter([
    poseLandmarks["leftWrist"].position,
    poseLandmarks["leftPinky"].position,
    poseLandmarks["leftIndex"].position,
    poseLandmarks["leftThumb"].position,
  ])
  const leftHandLandmarksAnimate: any[] = leftHandLandmarksGroupRef.value.children
  leftHandLandmarksAnimate.forEach((item, _) => {
    const newX = poseToCanvasCoord(leftPalm.x + leftHandLandmarks[item.name].position[0], canvas_factor)
    const newY = poseToCanvasCoord(leftPalm.y + leftHandLandmarks[item.name].position[1], canvas_factor)
    const newZ = poseToCanvasCoord(leftPalm.z + leftHandLandmarks[item.name].position[2], canvas_factor)
    item.position.x = smoothing(item.position.x, newX, delta)
    item.position.y = smoothing(item.position.y, newY, delta)
    item.position.z = smoothing(item.position.z, newZ, delta)
  })
  // right hand
  const rightPalm = getCenter([
    poseLandmarks["rightWrist"].position,
    poseLandmarks["rightPinky"].position,
    poseLandmarks["rightIndex"].position,
    poseLandmarks["rightThumb"].position,
  ])
  const rightHandLandmarksAnimate: any[] = rightHandLandmarksGroupRef.value.children
  rightHandLandmarksAnimate.forEach((item, _) => {
    const newX = poseToCanvasCoord(rightPalm.x + rightHandLandmarks[item.name].position[0], canvas_factor)
    const newY = poseToCanvasCoord(rightPalm.y + rightHandLandmarks[item.name].position[1], canvas_factor)
    const newZ = poseToCanvasCoord(rightPalm.z + rightHandLandmarks[item.name].position[2], canvas_factor)
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
      <TresCanvas>
        <TresPerspectiveCamera :position="[0, 0, 6]" :fov="45" :look-at="[0, 0, 0]" />
        <TresGroup ref="poseLandmarksGroupRef" :position="[0, 0, 0]">
          <TresMesh v-for="(landmark, key) in poseLandmarks" :name="key" :key="key" :position="[-1, -1, -1]">
            <TresBoxGeometry :args="landmark.cubeSize" />
            <TresMeshNormalMaterial :color="landmark.cubeColor" />
          </TresMesh>
        </TresGroup>
        <TresGroup ref="leftHandLandmarksGroupRef" :position="[0, 0, 0]">
          <TresMesh v-for="(landmark, key) in leftHandLandmarks" :name="key" :key="key" :position="[-1, -1, -1]">
            <TresBoxGeometry :args="landmark.cubeSize" />
            <TresMeshNormalMaterial :color="landmark.cubeColor" />
          </TresMesh>
        </TresGroup>
        <TresGroup ref="rightHandLandmarksGroupRef" :position="[0, 0, 0]">
          <TresMesh v-for="(landmark, key) in rightHandLandmarks" :name="key" :key="key" :position="[-1, -1, -1]">
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
