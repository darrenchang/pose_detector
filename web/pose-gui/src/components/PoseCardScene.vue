<script setup lang="ts">
// A still skeleton built from one image's inference result. Unlike
// SkeletonScene nothing animates: the joints and bones are computed once from
// the props, centred and scaled to fill the card, and only redrawn when the
// result or the drag-to-rotate angle changes.
import { computed, watch } from 'vue'
import { useTresContext } from '@tresjs/core'
import type { RawLandmark } from '@/interface/imageInferenceInterface'
import {
  POSE_JOINT_NAMES, HAND_JOINT_NAMES, BODY_JOINTS, BODY_CONNECTIONS, bodyJointRadius, HAND_CONNECTIONS,
  NOMINAL_HAND_SPAN, HAND_TO_TORSO, HEAD_TO_TORSO,
} from '@/composables/skeletonTopology'

const props = withDefaults(defineProps<{
  pose: RawLandmark[]
  leftHand: RawLandmark[]
  rightHand: RawLandmark[]
  // image width / height; pose x and z are normalised by the image width
  aspect: number
  // Orbit state owned by the parent: yaw / pitch of the figure and the
  // camera's distance from it (zoom).
  rotationY?: number
  rotationX?: number
  distance?: number
}>(), { rotationY: 0, rotationX: 0, distance: 4 })

type Vec3 = { x: number; y: number; z: number }
type Joint = { key: string; position: number[]; radius: number }
type Bone = { key: string; position: number[]; rotation: number[]; scale: number[] }

// The skeleton's larger extent (width or height) is scaled to this many canvas
// units; the camera below shows about 2.9 units vertically at z = 0.
const FIT_SIZE = 1.7

// Euler angles (XYZ order, as three.js reads them) that turn the +Y axis onto
// the unit direction (nx, ny, nz).
function rotationToward(nx: number, ny: number, nz: number): number[] {
  // Quaternion from (0,1,0) to n: axis = up × n, w = 1 + up · n
  let qx = nz, qy = 0, qz = -nx, qw = 1 + ny
  if (qw < 1e-6) {
    // Pointing straight down: half-turn about X
    qx = 1; qy = 0; qz = 0; qw = 0
  }
  const inv = 1 / Math.sqrt(qx * qx + qy * qy + qz * qz + qw * qw)
  qx *= inv; qy *= inv; qz *= inv; qw *= inv
  // Rotation matrix terms needed for the XYZ extraction
  const m11 = 1 - 2 * (qy * qy + qz * qz)
  const m12 = 2 * (qx * qy - qz * qw)
  const m13 = 2 * (qx * qz + qy * qw)
  const m22 = 1 - 2 * (qx * qx + qz * qz)
  const m23 = 2 * (qy * qz - qx * qw)
  const m32 = 2 * (qy * qz + qx * qw)
  const m33 = 1 - 2 * (qx * qx + qy * qy)
  const ey = Math.asin(Math.max(-1, Math.min(1, m13)))
  if (Math.abs(m13) < 0.9999999) {
    return [Math.atan2(-m23, m33), ey, Math.atan2(-m12, m11)]
  }
  return [Math.atan2(m32, m22), ey, 0]
}

function bone(key: string, a: Vec3, b: Vec3, radius: number): Bone | null {
  const dx = b.x - a.x
  const dy = b.y - a.y
  const dz = b.z - a.z
  const len = Math.sqrt(dx * dx + dy * dy + dz * dz)
  if (len < 1e-4) {
    return null
  }
  // A unit-height +Y cylinder: rotate it to point along a -> b, then stretch.
  return {
    key,
    position: [a.x + dx / 2, a.y + dy / 2, a.z + dz / 2],
    rotation: rotationToward(dx / len, dy / len, dz / len),
    scale: [radius, len, radius],
  }
}

const scene = computed(() => {
  const empty = { head: null as Joint | null, joints: [] as Joint[], bones: [] as Bone[], handJoints: [] as Joint[], handBones: [] as Bone[] }
  if (props.pose.length < POSE_JOINT_NAMES.length) {
    return empty
  }
  // 1. Pose landmarks in image units: x/z are fractions of the width, y of the
  //    height, so stretch x/z by the aspect ratio to undo the normalisation.
  const pts: Record<string, Vec3> = {}
  POSE_JOINT_NAMES.forEach((name, i) => {
    const lm = props.pose[i]
    pts[name] = { x: lm.x * props.aspect, y: lm.y, z: lm.z * props.aspect }
  })
  const mid = (a: Vec3, b: Vec3): Vec3 => ({ x: (a.x + b.x) / 2, y: (a.y + b.y) / 2, z: (a.z + b.z) / 2 })
  const head = mid(pts['leftEar'], pts['rightEar'])
  const shoulderMid = mid(pts['leftShoulder'], pts['rightShoulder'])
  const hipMid = mid(pts['leftHip'], pts['rightHip'])
  const torso = Math.max(
    Math.hypot(shoulderMid.x - hipMid.x, shoulderMid.y - hipMid.y, shoulderMid.z - hipMid.z),
    0.02,
  )
  const headRadius = HEAD_TO_TORSO * torso

  // 2. Fit: centre the drawn body (joints + head sphere) and scale its larger
  //    extent to FIT_SIZE so every card is framed the same way.
  const drawn = BODY_JOINTS.map(n => pts[n])
  let minX = head.x - headRadius, maxX = head.x + headRadius
  let minY = head.y - headRadius, maxY = head.y + headRadius
  drawn.forEach(p => {
    minX = Math.min(minX, p.x); maxX = Math.max(maxX, p.x)
    minY = Math.min(minY, p.y); maxY = Math.max(maxY, p.y)
  })
  const centre: Vec3 = { x: (minX + maxX) / 2, y: (minY + maxY) / 2, z: hipMid.z }
  const scale = FIT_SIZE / Math.max(maxX - minX, maxY - minY, 0.05)
  // Image y grows downwards and z towards the camera is negative; the canvas
  // has y up and the camera on +z.
  const toCanvas = (p: Vec3): Vec3 => ({
    x: (p.x - centre.x) * scale,
    y: -(p.y - centre.y) * scale,
    z: -(p.z - centre.z) * scale,
  })

  const bodyPos: Record<string, Vec3> = {}
  BODY_JOINTS.forEach(n => { bodyPos[n] = toCanvas(pts[n]) })
  const headPos = toCanvas(head)
  const boneRadius = 0.035 * scale * torso * 1.6
  const joints: Joint[] = BODY_JOINTS.map(n => ({ key: n, position: [bodyPos[n].x, bodyPos[n].y, bodyPos[n].z], radius: bodyJointRadius(n) * scale * torso * 1.6 }))
  const bones: Bone[] = []
  BODY_CONNECTIONS.forEach(([a, b], i) => {
    const bn = bone(`body-${i}`, bodyPos[a], bodyPos[b], boneRadius)
    if (bn) bones.push(bn)
  })
  const neck = bone('neck', headPos, toCanvas(shoulderMid), boneRadius)
  if (neck) bones.push(neck)

  // 3. Hands: metric world landmarks, anchored at the matching pose wrist and
  //    sized off the torso like the live scene.
  const handScale = (HAND_TO_TORSO * torso * scale) / NOMINAL_HAND_SPAN
  const handJoints: Joint[] = []
  const handBones: Bone[] = []
  const jointRadius = 0.016 * scale * torso * 1.6
  const fingerRadius = 0.012 * scale * torso * 1.6
  const addHand = (side: 'left' | 'right', lms: RawLandmark[]) => {
    if (lms.length < HAND_JOINT_NAMES.length) return
    const anchor = bodyPos[side === 'left' ? 'leftWrist' : 'rightWrist']
    const wrist = lms[0]
    const pos: Record<string, Vec3> = {}
    HAND_JOINT_NAMES.forEach((name, i) => {
      const lm = lms[i]
      pos[name] = {
        x: anchor.x + (lm.x - wrist.x) * handScale,
        y: anchor.y - (lm.y - wrist.y) * handScale,
        z: anchor.z - (lm.z - wrist.z) * handScale,
      }
      handJoints.push({ key: `${side}-${name}`, position: [pos[name].x, pos[name].y, pos[name].z], radius: jointRadius })
    })
    HAND_CONNECTIONS.forEach(([a, b], i) => {
      const bn = bone(`${side}-bone-${i}`, pos[a], pos[b], fingerRadius)
      if (bn) handBones.push(bn)
    })
  }
  addHand('left', props.leftHand)
  addHand('right', props.rightHand)

  return {
    head: { key: 'head', position: [headPos.x, headPos.y, headPos.z], radius: headRadius * scale },
    joints,
    bones,
    handJoints,
    handBones,
  }
})

// The canvas is in on-demand mode: ask for a frame whenever the result or the
// rotation changes (prop patches also invalidate, this covers v-for churn).
const { invalidate } = useTresContext()
watch([scene, () => props.rotationY, () => props.rotationX, () => props.distance], () => invalidate(), { flush: 'post' })
</script>

<template>
  <TresPerspectiveCamera :position="[0, 0, distance]" :fov="40" :look-at="[0, 0, 0]" />
  <TresAmbientLight :intensity="0.9" />
  <TresDirectionalLight :position="[2, 4, 5]" :intensity="1.6" />
  <TresDirectionalLight :position="[-3, 1, 2]" :intensity="0.6" />

  <TresGroup :rotation="[rotationX, rotationY, 0]">
    <!-- Head -->
    <TresMesh v-if="scene.head" :position="scene.head.position" :scale="[scene.head.radius, scene.head.radius, scene.head.radius]">
      <TresSphereGeometry :args="[1, 24, 24]" />
      <TresMeshStandardMaterial color="#f4a259" :roughness="0.5" :metalness="0.1" />
    </TresMesh>

    <!-- Body bones (unit cylinder scaled to [radius, length, radius]) -->
    <TresMesh v-for="b in scene.bones" :key="b.key" :position="b.position" :rotation="b.rotation" :scale="b.scale">
      <TresCylinderGeometry :args="[1, 1, 1, 12]" />
      <TresMeshStandardMaterial color="#3ddc97" :roughness="0.5" :metalness="0.1" />
    </TresMesh>

    <!-- Body joints -->
    <TresMesh v-for="j in scene.joints" :key="j.key" :position="j.position" :scale="[j.radius, j.radius, j.radius]">
      <TresSphereGeometry :args="[1, 16, 16]" />
      <TresMeshStandardMaterial color="#f4a259" :roughness="0.4" :metalness="0.1" />
    </TresMesh>

    <!-- Hand bones -->
    <TresMesh v-for="b in scene.handBones" :key="b.key" :position="b.position" :rotation="b.rotation" :scale="b.scale">
      <TresCylinderGeometry :args="[1, 1, 1, 8]" />
      <TresMeshStandardMaterial color="#5bd1ff" :roughness="0.5" :metalness="0.1" />
    </TresMesh>

    <!-- Hand joints -->
    <TresMesh v-for="j in scene.handJoints" :key="j.key" :position="j.position" :scale="[j.radius, j.radius, j.radius]">
      <TresSphereGeometry :args="[1, 10, 10]" />
      <TresMeshStandardMaterial color="#ffd166" :roughness="0.4" :metalness="0.1" />
    </TresMesh>
  </TresGroup>
</template>
