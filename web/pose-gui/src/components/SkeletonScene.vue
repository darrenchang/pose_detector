<script setup lang="ts">
import { shallowRef } from 'vue'
import { useLoop, useTresContext } from '@tresjs/core'
import { poseLandmarks } from '@/interface/poseLandmarksInterface'
import { leftHandLandmarks, rightHandLandmarks } from '@/interface/handLandmarksInterface'

const canvas_factor = 2

type Vec3 = { x: number; y: number; z: number }

// --- Body (pose) topology -------------------------------------------------
// The face landmarks (indices 0-10) are not drawn individually; the head is a
// single sphere (see below). The coarse pose hand points are not drawn either;
// fingers come from the dedicated hand landmarks.
const BODY_JOINTS = [
  'leftShoulder', 'rightShoulder', 'leftElbow', 'rightElbow', 'leftWrist', 'rightWrist',
  'leftHip', 'rightHip', 'leftKnee', 'rightKnee', 'leftAnkle', 'rightAnkle',
  'leftHeel', 'rightHeel', 'leftFootIndex', 'rightFootIndex',
]

const BODY_CONNECTIONS: [string, string][] = [
  // torso
  ['leftShoulder', 'rightShoulder'], ['leftShoulder', 'leftHip'], ['rightShoulder', 'rightHip'], ['leftHip', 'rightHip'],
  // arms
  ['leftShoulder', 'leftElbow'], ['leftElbow', 'leftWrist'],
  ['rightShoulder', 'rightElbow'], ['rightElbow', 'rightWrist'],
  // legs
  ['leftHip', 'leftKnee'], ['leftKnee', 'leftAnkle'], ['leftAnkle', 'leftHeel'], ['leftHeel', 'leftFootIndex'], ['leftAnkle', 'leftFootIndex'],
  ['rightHip', 'rightKnee'], ['rightKnee', 'rightAnkle'], ['rightAnkle', 'rightHeel'], ['rightHeel', 'rightFootIndex'], ['rightAnkle', 'rightFootIndex'],
]

function bodyJointRadius(name: string) {
  if (name === 'leftHeel' || name === 'rightHeel' || name === 'leftFootIndex' || name === 'rightFootIndex') {
    return 0.035
  }
  return 0.05
}

// --- Hand topology (21 landmarks per hand) --------------------------------
const HAND_JOINTS = Object.keys(leftHandLandmarks)
const HAND_CONNECTIONS: [string, string][] = [
  // thumb
  ['wrist', 'thumbCmc'], ['thumbCmc', 'thumbMcp'], ['thumbMcp', 'thumbIp'], ['thumbIp', 'thumbTip'],
  // index
  ['wrist', 'indexFingerMcp'], ['indexFingerMcp', 'indexFingerPip'], ['indexFingerPip', 'indexFingerDip'], ['indexFingerDip', 'indexFingerTip'],
  // middle
  ['indexFingerMcp', 'middleFingerMcp'], ['middleFingerMcp', 'middleFingerPip'], ['middleFingerPip', 'middleFingerDip'], ['middleFingerDip', 'middleFingerTip'],
  // ring
  ['middleFingerMcp', 'ringFingerMcp'], ['ringFingerMcp', 'ringFingerPip'], ['ringFingerPip', 'ringFingerDip'], ['ringFingerDip', 'ringFingerTip'],
  // pinky + palm edge
  ['ringFingerMcp', 'pinkyMcp'], ['wrist', 'pinkyMcp'], ['pinkyMcp', 'pinkyPip'], ['pinkyPip', 'pinkyDip'], ['pinkyDip', 'pinkyTip'],
]

// Refs
const headRef = shallowRef()
const neckBoneRef = shallowRef()
const bodyJointsGroupRef = shallowRef()
const bodyBonesGroupRef = shallowRef()
const leftHandJointsGroupRef = shallowRef()
const rightHandJointsGroupRef = shallowRef()
const leftHandBonesGroupRef = shallowRef()
const rightHandBonesGroupRef = shallowRef()

// Smoothed canvas-space position caches, keyed by name.
const bodyPos: Record<string, Vec3> = {}
BODY_JOINTS.forEach(n => { bodyPos[n] = { x: 0, y: 0, z: 0 } })
const leftHandPos: Record<string, Vec3> = {}
const rightHandPos: Record<string, Vec3> = {}
HAND_JOINTS.forEach(n => { leftHandPos[n] = { x: 0, y: 0, z: 0 }; rightHandPos[n] = { x: 0, y: 0, z: 0 } })

// A mesh counts as "settled" once within this distance of its target; when
// everything is settled we stop requesting frames.
const SETTLED_EPS = 5e-4
let lastPresent = false
let lastLeftHand = false
let lastRightHand = false
let firstFrame = true

function p2c(coord: number) {
  return 1 - coord * canvas_factor
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

// Smooth a mesh toward a target; returns true if it moved this frame.
function moveToward(item: any, tx: number, ty: number, tz: number, delta: number): boolean {
  const dx = tx - item.position.x
  const dy = ty - item.position.y
  const dz = tz - item.position.z
  if (dx * dx + dy * dy + dz * dz > SETTLED_EPS * SETTLED_EPS) {
    item.position.x = smoothing(item.position.x, tx, delta)
    item.position.y = smoothing(item.position.y, ty, delta)
    item.position.z = smoothing(item.position.z, tz, delta)
    return true
  }
  return false
}

// Orient a unit-height +Y cylinder so it spans from a to b.
function setBone(bone: any, a: Vec3, b: Vec3) {
  const dx = b.x - a.x
  const dy = b.y - a.y
  const dz = b.z - a.z
  const len = Math.sqrt(dx * dx + dy * dy + dz * dz)
  if (len < 1e-4) {
    bone.visible = false
    return
  }
  bone.visible = true
  bone.position.set(a.x + dx * 0.5, a.y + dy * 0.5, a.z + dz * 0.5)
  const nx = dx / len
  const ny = dy / len
  const nz = dz / len
  let qx = nz
  let qy = 0
  let qz = -nx
  let qw = 1 + ny
  if (qw < 1e-6) {
    qx = 1; qy = 0; qz = 0; qw = 0
  }
  const inv = 1 / Math.sqrt(qx * qx + qy * qy + qz * qz + qw * qw)
  bone.quaternion.set(qx * inv, qy * inv, qz * inv, qw * inv)
  bone.scale.set(1, len, 1)
}

function dist3(a: number[], b: number[]) {
  return Math.sqrt((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2 + (a[2] - b[2]) ** 2)
}

// Animate one hand's 21 joints and its finger bones. The hand landmarks are in
// metric world space, so they are scaled to the pose forearm length (keeping
// them proportional to the body) and the hand's own wrist is anchored onto the
// pose wrist so the fingers extend from where the arm actually ends.
function updateHand(
  jointsGroupRef: any,
  bonesGroupRef: any,
  handLandmarks: Record<string, { position: number[] }>,
  cache: Record<string, Vec3>,
  anchor: Vec3,
  forearmLen: number,
  handPresent: boolean,
  delta: number,
): boolean {
  let moved = false
  const handWrist = handLandmarks['wrist'].position
  // Scale so the hand (wrist -> middle fingertip) is ~0.85x the forearm.
  const handSpan = dist3(handWrist, handLandmarks['middleFingerTip'].position)
  const scale = handSpan > 1e-4 ? (0.85 * forearmLen) / handSpan : 1
  const joints: any[] = jointsGroupRef.value.children
  joints.forEach(item => {
    const lm = handLandmarks[item.name].position
    const tx = p2c(anchor.x + (lm[0] - handWrist[0]) * scale)
    const ty = p2c(anchor.y + (lm[1] - handWrist[1]) * scale)
    const tz = p2c(anchor.z + (lm[2] - handWrist[2]) * scale)
    if (moveToward(item, tx, ty, tz, delta)) {
      moved = true
    }
    item.visible = handPresent
    const c = cache[item.name]
    c.x = item.position.x; c.y = item.position.y; c.z = item.position.z
  })
  const bones: any[] = bonesGroupRef.value.children
  bones.forEach((bone, i) => {
    if (!handPresent) {
      bone.visible = false
      return
    }
    const [a, b] = HAND_CONNECTIONS[i]
    setBone(bone, cache[a], cache[b])
  })
  return moved
}

const { invalidate } = useTresContext()
const { onBeforeRender } = useLoop()

onBeforeRender(({ delta }) => {
  if (
    !headRef.value || !neckBoneRef.value ||
    !bodyJointsGroupRef.value || !bodyBonesGroupRef.value ||
    !leftHandJointsGroupRef.value || !rightHandJointsGroupRef.value ||
    !leftHandBonesGroupRef.value || !rightHandBonesGroupRef.value
  ) {
    invalidate() // scene not ready yet; try again next frame
    return
  }

  const present = poseLandmarks['leftShoulder'].exist
  const leftHandPresent = present && !!leftHandLandmarks['wrist']?.exist
  const rightHandPresent = present && !!rightHandLandmarks['wrist']?.exist
  let dirty =
    firstFrame ||
    present !== lastPresent ||
    leftHandPresent !== lastLeftHand ||
    rightHandPresent !== lastRightHand
  firstFrame = false
  lastPresent = present
  lastLeftHand = leftHandPresent
  lastRightHand = rightHandPresent

  // 1. Body joints
  const bodyJoints: any[] = bodyJointsGroupRef.value.children
  bodyJoints.forEach(item => {
    const lm = poseLandmarks[item.name].position
    if (moveToward(item, p2c(lm[0]), p2c(lm[1]), p2c(lm[2]), delta)) {
      dirty = true
    }
    item.visible = present
    const c = bodyPos[item.name]
    c.x = item.position.x; c.y = item.position.y; c.z = item.position.z
  })

  // 2. Head: a single sphere at the mid-point of the ears, sized to the
  // shoulder width so it stays proportional at any distance.
  const lEar = poseLandmarks['leftEar'].position
  const rEar = poseLandmarks['rightEar'].position
  const headTarget: Vec3 = {
    x: p2c((lEar[0] + rEar[0]) / 2),
    y: p2c((lEar[1] + rEar[1]) / 2),
    z: p2c((lEar[2] + rEar[2]) / 2),
  }
  if (moveToward(headRef.value, headTarget.x, headTarget.y, headTarget.z, delta)) {
    dirty = true
  }
  const shoulderWidth = Math.sqrt(
    (bodyPos['leftShoulder'].x - bodyPos['rightShoulder'].x) ** 2 +
    (bodyPos['leftShoulder'].y - bodyPos['rightShoulder'].y) ** 2 +
    (bodyPos['leftShoulder'].z - bodyPos['rightShoulder'].z) ** 2,
  )
  const headRadius = Math.min(Math.max(0.45 * shoulderWidth, 0.06), 0.2)
  const curRadius = headRef.value.scale.x
  if (Math.abs(headRadius - curRadius) > SETTLED_EPS) {
    headRef.value.scale.setScalar(smoothing(curRadius, headRadius, delta))
    dirty = true
  }
  headRef.value.visible = present

  // 3. Body bones
  const bodyBones: any[] = bodyBonesGroupRef.value.children
  bodyBones.forEach((bone, i) => {
    if (!present) {
      bone.visible = false
      return
    }
    const [a, b] = BODY_CONNECTIONS[i]
    setBone(bone, bodyPos[a], bodyPos[b])
  })

  // 4. Neck: head -> shoulder mid-point
  if (present) {
    const shoulderMid: Vec3 = {
      x: (bodyPos['leftShoulder'].x + bodyPos['rightShoulder'].x) / 2,
      y: (bodyPos['leftShoulder'].y + bodyPos['rightShoulder'].y) / 2,
      z: (bodyPos['leftShoulder'].z + bodyPos['rightShoulder'].z) / 2,
    }
    setBone(neckBoneRef.value, headRef.value.position, shoulderMid)
  } else {
    neckBoneRef.value.visible = false
  }

  // 5. Hands: full finger skeletons anchored at each pose wrist, scaled to the
  // matching forearm so they stay proportional to the body.
  const lw = poseLandmarks['leftWrist'].position
  const leftAnchor: Vec3 = { x: lw[0], y: lw[1], z: lw[2] }
  const leftForearm = dist3(poseLandmarks['leftElbow'].position, lw)
  if (updateHand(leftHandJointsGroupRef, leftHandBonesGroupRef, leftHandLandmarks, leftHandPos, leftAnchor, leftForearm, leftHandPresent, delta)) {
    dirty = true
  }

  const rw = poseLandmarks['rightWrist'].position
  const rightAnchor: Vec3 = { x: rw[0], y: rw[1], z: rw[2] }
  const rightForearm = dist3(poseLandmarks['rightElbow'].position, rw)
  if (updateHand(rightHandJointsGroupRef, rightHandBonesGroupRef, rightHandLandmarks, rightHandPos, rightAnchor, rightForearm, rightHandPresent, delta)) {
    dirty = true
  }

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

  <!-- Head (unit sphere; scaled to shoulder width each frame) -->
  <TresMesh ref="headRef" :scale="[0.12, 0.12, 0.12]" :visible="false">
    <TresSphereGeometry :args="[1, 24, 24]" />
    <TresMeshStandardMaterial color="#f4a259" :roughness="0.5" :metalness="0.1" />
  </TresMesh>

  <!-- Neck bone -->
  <TresMesh ref="neckBoneRef" :visible="false">
    <TresCylinderGeometry :args="[0.035, 0.035, 1, 12]" />
    <TresMeshStandardMaterial color="#3ddc97" :roughness="0.5" :metalness="0.1" />
  </TresMesh>

  <!-- Body bones -->
  <TresGroup ref="bodyBonesGroupRef">
    <TresMesh v-for="(bone, i) in BODY_CONNECTIONS" :key="`body-bone-${i}`" :visible="false">
      <TresCylinderGeometry :args="[0.035, 0.035, 1, 12]" />
      <TresMeshStandardMaterial color="#3ddc97" :roughness="0.5" :metalness="0.1" />
    </TresMesh>
  </TresGroup>

  <!-- Body joints -->
  <TresGroup ref="bodyJointsGroupRef">
    <TresMesh v-for="name in BODY_JOINTS" :name="name" :key="name" :position="[-1, -1, -1]" :visible="false">
      <TresSphereGeometry :args="[bodyJointRadius(name), 16, 16]" />
      <TresMeshStandardMaterial color="#f4a259" :roughness="0.4" :metalness="0.1" />
    </TresMesh>
  </TresGroup>

  <!-- Left hand bones -->
  <TresGroup ref="leftHandBonesGroupRef">
    <TresMesh v-for="(bone, i) in HAND_CONNECTIONS" :key="`lh-bone-${i}`" :visible="false">
      <TresCylinderGeometry :args="[0.012, 0.012, 1, 8]" />
      <TresMeshStandardMaterial color="#5bd1ff" :roughness="0.5" :metalness="0.1" />
    </TresMesh>
  </TresGroup>

  <!-- Right hand bones -->
  <TresGroup ref="rightHandBonesGroupRef">
    <TresMesh v-for="(bone, i) in HAND_CONNECTIONS" :key="`rh-bone-${i}`" :visible="false">
      <TresCylinderGeometry :args="[0.012, 0.012, 1, 8]" />
      <TresMeshStandardMaterial color="#5bd1ff" :roughness="0.5" :metalness="0.1" />
    </TresMesh>
  </TresGroup>

  <!-- Left hand joints -->
  <TresGroup ref="leftHandJointsGroupRef">
    <TresMesh v-for="name in HAND_JOINTS" :name="name" :key="`lh-${name}`" :position="[-1, -1, -1]" :visible="false">
      <TresSphereGeometry :args="[0.016, 10, 10]" />
      <TresMeshStandardMaterial color="#ffd166" :roughness="0.4" :metalness="0.1" />
    </TresMesh>
  </TresGroup>

  <!-- Right hand joints -->
  <TresGroup ref="rightHandJointsGroupRef">
    <TresMesh v-for="name in HAND_JOINTS" :name="name" :key="`rh-${name}`" :position="[-1, -1, -1]" :visible="false">
      <TresSphereGeometry :args="[0.016, 10, 10]" />
      <TresMeshStandardMaterial color="#ffd166" :roughness="0.4" :metalness="0.1" />
    </TresMesh>
  </TresGroup>
</template>
