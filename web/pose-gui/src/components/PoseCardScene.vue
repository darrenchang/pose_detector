<script setup lang="ts">
// A still skeleton built from one image's inference result, for the modal.
// Nothing animates: the joints and bones come from buildSkeleton() once per
// result and the scene is only redrawn when the result or the orbit changes.
import { computed, watch } from 'vue'
import { useTresContext } from '@tresjs/core'
import type { RawLandmark } from '@/interface/imageInferenceInterface'
import { buildSkeleton } from '@/composables/poseSkeleton'

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

const scene = computed(() =>
  buildSkeleton(props.pose, props.leftHand, props.rightHand, props.aspect),
)

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
