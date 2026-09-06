<script setup lang="ts">
import { shallowRef, watch } from 'vue'
import { useLoop, useTresContext } from '@tresjs/core'
import { poseLandmarks } from '@/interface/poseLandmarksInterface'
import { leftHandLandmarks, rightHandLandmarks } from '@/interface/handLandmarksInterface'

const props = withDefaults(defineProps<{ paused?: boolean }>(), { paused: false })

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
  return (1 + coord) / factor
}

function getCenter(points: number[][]): { x: number; y: number; z: number } {
  const pointSum = points.reduce(
    (acc, cur) => {
      acc.x_sum += cur[0]
      acc.y_sum += cur[1]
      acc.z_sum += cur[2]
      return acc
    },
    { x_sum: 0, y_sum: 0, z_sum: 0 },
  )
  return {
    x: pointSum.x_sum / points.length,
    y: pointSum.y_sum / points.length,
    z: pointSum.z_sum / points.length,
  }
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

// Moves each mesh toward its target and returns true if anything moved this
// frame (i.e. a redraw is needed).
function updateGroup(
  groupRef: any,
  landmarks: Record<string, { position: number[] }>,
  delta: number,
  offset: { x: number; y: number; z: number } = { x: 0, y: 0, z: 0 },
): boolean {
  let moved = false
  const children: any[] = groupRef.value.children
  children.forEach(item => {
    const lm = landmarks[item.name].position
    const targetX = poseToCanvasCoord(offset.x + lm[0], canvas_factor)
    const targetY = poseToCanvasCoord(offset.y + lm[1], canvas_factor)
    const targetZ = poseToCanvasCoord(offset.z + lm[2], canvas_factor)
    const dx = targetX - item.position.x
    const dy = targetY - item.position.y
    const dz = targetZ - item.position.z
    if (dx * dx + dy * dy + dz * dz > SETTLED_EPS * SETTLED_EPS) {
      item.position.x = smoothing(item.position.x, targetX, delta)
      item.position.y = smoothing(item.position.y, targetY, delta)
      item.position.z = smoothing(item.position.z, targetZ, delta)
      moved = true
    }
  })
  return moved
}

const { invalidate } = useTresContext()
const { onBeforeRender } = useLoop()

onBeforeRender(({ delta }) => {
  if (props.paused) {
    return
  }
  if (
    !poseLandmarksGroupRef.value ||
    !leftHandLandmarksGroupRef.value ||
    !rightHandLandmarksGroupRef.value
  ) {
    invalidate() // scene not ready yet; try again next frame
    return
  }

  const movedPose = updateGroup(poseLandmarksGroupRef, poseLandmarks, delta)

  const leftPalm = getCenter([
    poseLandmarks['leftWrist'].position,
    poseLandmarks['leftPinky'].position,
    poseLandmarks['leftIndex'].position,
    poseLandmarks['leftThumb'].position,
  ])
  const movedLeft = updateGroup(leftHandLandmarksGroupRef, leftHandLandmarks, delta, leftPalm)

  const rightPalm = getCenter([
    poseLandmarks['rightWrist'].position,
    poseLandmarks['rightPinky'].position,
    poseLandmarks['rightIndex'].position,
    poseLandmarks['rightThumb'].position,
  ])
  const movedRight = updateGroup(rightHandLandmarksGroupRef, rightHandLandmarks, delta, rightPalm)

  if (firstFrame || movedPose || movedLeft || movedRight) {
    firstFrame = false
    invalidate()
  }
})

// Resume drawing when unpaused.
watch(
  () => props.paused,
  paused => {
    if (!paused) {
      invalidate()
    }
  },
)

// Exposed for the "Save Landmarks" button in the parent.
function getPoseLandmarks() {
  if (!poseLandmarksGroupRef.value) {
    return []
  }
  return (poseLandmarksGroupRef.value.children as any[]).map(cur => ({
    x: canvasToPoseCoord(cur.position.x, canvas_factor),
    y: canvasToPoseCoord(cur.position.y, canvas_factor),
    z: canvasToPoseCoord(cur.position.z, canvas_factor),
  }))
}

defineExpose({ getPoseLandmarks })
</script>

<template>
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
</template>
