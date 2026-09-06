<script setup lang="ts">
import { shallowRef } from 'vue'
import { useLoop, useTresContext } from '@tresjs/core'
import { poseLandmarks } from '@/interface/poseLandmarksInterface'
import { leftHandLandmarks, rightHandLandmarks } from '@/interface/handLandmarksInterface'

const canvas_factor = 2

// A mesh counts as "settled" once within this distance of its target; when
// everything is settled we stop requesting frames.
const SETTLED_EPS = 5e-4
let firstFrame = true

const poseLandmarksGroupRef = shallowRef()
const leftHandLandmarksGroupRef = shallowRef()
const rightHandLandmarksGroupRef = shallowRef()

function poseToCanvasCoord(coord: number, factor: number) {
  return 1 - coord * factor
}

function canvasToPoseCoord(coord: number, factor: number) {
  return ((coord - 1) * -1) / factor
}

function smoothing(start: number, end: number, delta: number, speed_override = -1) {
  let speed = 10
  if (speed_override === -1) {
    speed = Math.min(Math.max(end - start * 2, 7), 10)
  } else {
    speed = speed_override
  }
  const alpha = 1 - Math.exp(-speed * delta)
  const threshold = 0.3
  if (Math.abs(end - start) > threshold) {
    return end
  } else {
    return start + (end - start) * alpha
  }
}

// Moves each mesh toward its target and updates visibility; returns true if
// anything changed this frame (so a redraw is needed).
function updateLandmarks(
  groupRef: any,
  landmarks: Record<string, { position: number[]; exist: boolean; display: boolean }>,
  delta: number,
  smooth_speed = -1,
  offsetPosition: { x: number; y: number; z: number } = { x: 0, y: 0, z: 0 },
): boolean {
  let moved = false
  const children: any[] = groupRef.value.children
  children.forEach(item => {
    const landmark = landmarks[item.name].position
    const targetX = poseToCanvasCoord(offsetPosition.x + landmark[0], canvas_factor)
    const targetY = poseToCanvasCoord(offsetPosition.y + landmark[1], canvas_factor)
    const targetZ = poseToCanvasCoord(offsetPosition.z + landmark[2], canvas_factor)
    const dx = targetX - item.position.x
    const dy = targetY - item.position.y
    const dz = targetZ - item.position.z
    if (dx * dx + dy * dy + dz * dz > SETTLED_EPS * SETTLED_EPS) {
      item.position.x = smoothing(item.position.x, targetX, delta, smooth_speed)
      item.position.y = smoothing(item.position.y, targetY, delta, smooth_speed)
      item.position.z = smoothing(item.position.z, targetZ, delta, smooth_speed)
      moved = true
    }
    const visible = landmarks[item.name].exist && landmarks[item.name].display
    if (item.visible !== visible) {
      item.visible = visible
      moved = true
    }
  })
  return moved
}

const { invalidate } = useTresContext()
const { onBeforeRender } = useLoop()

onBeforeRender(({ delta }) => {
  if (
    !poseLandmarksGroupRef.value ||
    !leftHandLandmarksGroupRef.value ||
    !rightHandLandmarksGroupRef.value
  ) {
    invalidate() // scene not ready yet; try again next frame
    return
  }

  let moved = updateLandmarks(poseLandmarksGroupRef, poseLandmarks, delta, -1)

  const leftWrist = (poseLandmarksGroupRef.value.children as any[]).find(c => c.name === 'leftWrist')
  const leftPalmOffset = {
    x: canvasToPoseCoord(leftWrist.position.x, canvas_factor),
    y: canvasToPoseCoord(leftWrist.position.y, canvas_factor),
    z: canvasToPoseCoord(leftWrist.position.z, canvas_factor),
  }
  moved = updateLandmarks(leftHandLandmarksGroupRef, leftHandLandmarks, delta, 50, leftPalmOffset) || moved

  const rightWrist = (poseLandmarksGroupRef.value.children as any[]).find(c => c.name === 'rightWrist')
  const rightPalmOffset = {
    x: canvasToPoseCoord(rightWrist.position.x, canvas_factor),
    y: canvasToPoseCoord(rightWrist.position.y, canvas_factor),
    z: canvasToPoseCoord(rightWrist.position.z, canvas_factor),
  }
  moved = updateLandmarks(rightHandLandmarksGroupRef, rightHandLandmarks, delta, 50, rightPalmOffset) || moved

  if (firstFrame || moved) {
    firstFrame = false
    invalidate()
  }
})
</script>

<template>
  <TresPerspectiveCamera :position="[0, 0, 6]" :fov="30" :look-at="[0, 0, 0]" />
  <TresGroup ref="poseLandmarksGroupRef" :position="[0, 0, 0]" :visible="false">
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
</template>
