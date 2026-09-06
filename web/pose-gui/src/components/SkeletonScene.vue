<script setup lang="ts">
import { shallowRef } from 'vue'
import { useLoop } from '@tresjs/core'
import { poseLandmarks } from '@/interface/poseLandmarksInterface'

const canvas_factor = 2

// MediaPipe pose topology: pairs of landmark names that form a bone.
// https://ai.google.dev/edge/mediapipe/solutions/vision/pose_landmarker
const POSE_CONNECTIONS: [string, string][] = [
  // face
  ['nose', 'leftEyeInner'], ['leftEyeInner', 'leftEye'], ['leftEye', 'leftEyeOuter'], ['leftEyeOuter', 'leftEar'],
  ['nose', 'rightEyeInner'], ['rightEyeInner', 'rightEye'], ['rightEye', 'rightEyeOuter'], ['rightEyeOuter', 'rightEar'],
  ['mouthLeft', 'mouthRight'],
  // torso
  ['leftShoulder', 'rightShoulder'], ['leftShoulder', 'leftHip'], ['rightShoulder', 'rightHip'], ['leftHip', 'rightHip'],
  // left arm
  ['leftShoulder', 'leftElbow'], ['leftElbow', 'leftWrist'], ['leftWrist', 'leftIndex'], ['leftWrist', 'leftThumb'], ['leftWrist', 'leftPinky'],
  // right arm
  ['rightShoulder', 'rightElbow'], ['rightElbow', 'rightWrist'], ['rightWrist', 'rightIndex'], ['rightWrist', 'rightThumb'], ['rightWrist', 'rightPinky'],
  // left leg
  ['leftHip', 'leftKnee'], ['leftKnee', 'leftAnkle'], ['leftAnkle', 'leftHeel'], ['leftHeel', 'leftFootIndex'], ['leftAnkle', 'leftFootIndex'],
  // right leg
  ['rightHip', 'rightKnee'], ['rightKnee', 'rightAnkle'], ['rightAnkle', 'rightHeel'], ['rightHeel', 'rightFootIndex'], ['rightAnkle', 'rightFootIndex'],
]

const jointNames = Object.keys(poseLandmarks)

// Joint sphere radius by role, so the figure reads as a person and not a
// uniform point cloud.
const bigJoints = new Set([
  'leftShoulder', 'rightShoulder', 'leftHip', 'rightHip',
  'leftElbow', 'rightElbow', 'leftKnee', 'rightKnee',
  'leftWrist', 'rightWrist', 'leftAnkle', 'rightAnkle',
])
function jointRadius(name: string) {
  if (name === 'nose') return 0.14 // head
  if (bigJoints.has(name)) return 0.05
  return 0.025
}

const jointsGroupRef = shallowRef()
const bonesGroupRef = shallowRef()

// Latest smoothed joint positions in canvas space, keyed by name.
type Vec3 = { x: number; y: number; z: number }
const jointPos: Record<string, Vec3> = {}
jointNames.forEach(n => { jointPos[n] = { x: 0, y: 0, z: 0 } })

// A joint counts as "settled" once it is within this distance of its target,
// at which point we stop requesting new frames.
const SETTLED_EPS = 5e-4
let lastPresent = false
let firstFrame = true

function poseToCanvasCoord(coord: number, factor: number) {
  return 1 - coord * factor
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

// on-demand render mode: this callback runs every animation frame (it is cheap
// JS), but the actual WebGL draw only happens on frames we invalidate(). We
// invalidate only while the skeleton is still moving toward newly received
// landmarks, so a still or absent subject costs zero draws.
const { onBeforeRender } = useLoop()
onBeforeRender(({ delta, invalidate }) => {
  if (!jointsGroupRef.value || !bonesGroupRef.value) {
    invalidate() // scene not ready yet; try again next frame
    return
  }
  const present = poseLandmarks['leftShoulder'].exist
  let dirty = firstFrame || present !== lastPresent
  firstFrame = false
  lastPresent = present

  // 1. Move joint spheres toward their targets; note if anything moved.
  const jointMeshes: any[] = jointsGroupRef.value.children
  jointMeshes.forEach(item => {
    const lm = poseLandmarks[item.name]
    const targetX = poseToCanvasCoord(lm.position[0], canvas_factor)
    const targetY = poseToCanvasCoord(lm.position[1], canvas_factor)
    const targetZ = poseToCanvasCoord(lm.position[2], canvas_factor)
    const dx = targetX - item.position.x
    const dy = targetY - item.position.y
    const dz = targetZ - item.position.z
    if (dx * dx + dy * dy + dz * dz > SETTLED_EPS * SETTLED_EPS) {
      item.position.x = smoothing(item.position.x, targetX, delta)
      item.position.y = smoothing(item.position.y, targetY, delta)
      item.position.z = smoothing(item.position.z, targetZ, delta)
      dirty = true
    }
    item.visible = present
    const cache = jointPos[item.name]
    cache.x = item.position.x
    cache.y = item.position.y
    cache.z = item.position.z
  })

  // 2. Stretch each bone cylinder between its two joints. A three.js cylinder
  // has base height 1, is centered at the origin and points along +Y, so we
  // position it at the bone midpoint, scale Y to the bone length, and rotate
  // +Y onto the bone direction.
  const boneMeshes: any[] = bonesGroupRef.value.children
  boneMeshes.forEach((bone, i) => {
    const [a, b] = POSE_CONNECTIONS[i]
    const pa = jointPos[a]
    const pb = jointPos[b]
    const dx = pb.x - pa.x
    const dy = pb.y - pa.y
    const dz = pb.z - pa.z
    const len = Math.sqrt(dx * dx + dy * dy + dz * dz)
    if (!present || len < 1e-4) {
      bone.visible = false
      return
    }
    bone.visible = true
    bone.position.set(pa.x + dx * 0.5, pa.y + dy * 0.5, pa.z + dz * 0.5)
    // Quaternion rotating unit +Y onto the normalized direction n.
    // axis = cross((0,1,0), n) = (n.z, 0, -n.x); w = 1 + dot((0,1,0), n) = 1 + n.y
    const nx = dx / len
    const ny = dy / len
    const nz = dz / len
    let qx = nz
    let qy = 0
    let qz = -nx
    let qw = 1 + ny
    if (qw < 1e-6) {
      // n points straight down; rotate 180° about the X axis.
      qx = 1; qy = 0; qz = 0; qw = 0
    }
    const inv = 1 / Math.sqrt(qx * qx + qy * qy + qz * qz + qw * qw)
    bone.quaternion.set(qx * inv, qy * inv, qz * inv, qw * inv)
    bone.scale.set(1, len, 1)
  })

  // Request a draw only if something actually changed this frame.
  if (dirty) {
    invalidate()
  }
})
</script>

<template>
  <TresPerspectiveCamera :position="[0, 0, 4.5]" :fov="45" :look-at="[0, 0, 0]" />
  <TresAmbientLight :intensity="0.9" />
  <TresDirectionalLight :position="[2, 4, 5]" :intensity="1.6" />
  <TresDirectionalLight :position="[-3, 1, 2]" :intensity="0.6" />

  <!-- Bones: one cylinder per connection, transformed each frame -->
  <TresGroup ref="bonesGroupRef">
    <TresMesh v-for="(bone, i) in POSE_CONNECTIONS" :key="`bone-${i}`" :visible="false">
      <TresCylinderGeometry :args="[0.035, 0.035, 1, 12]" />
      <TresMeshStandardMaterial color="#3ddc97" :roughness="0.5" :metalness="0.1" />
    </TresMesh>
  </TresGroup>

  <!-- Joints: one sphere per landmark -->
  <TresGroup ref="jointsGroupRef">
    <TresMesh
      v-for="(landmark, key) in poseLandmarks"
      :name="key"
      :key="key"
      :position="[-1, -1, -1]"
      :visible="false"
    >
      <TresSphereGeometry :args="[jointRadius(key as string), 16, 16]" />
      <TresMeshStandardMaterial color="#f4a259" :roughness="0.4" :metalness="0.1" />
    </TresMesh>
  </TresGroup>
</template>
