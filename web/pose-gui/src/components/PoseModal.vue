<script setup lang="ts">
// A card opened full size: the same TresJS skeleton, but with free orbit
// (drag), zoom (scroll / pinch) and a reset, so the model can be inspected.
import { computed, ref, watch } from 'vue'
import { NModal, NButton, NIcon, NTag, NSpace, NText } from 'naive-ui'
import { TresCanvas } from '@tresjs/core'
import { RefreshOutline } from '@vicons/ionicons5'
import PoseCardScene from '@/components/PoseCardScene.vue'
import type { InferenceCard } from '@/interface/imageInferenceInterface'

const props = defineProps<{ item: InferenceCard | null }>()
const emit = defineEmits<{ close: [] }>()

const result = computed(() => props.item?.result)
const aspect = computed(() => {
  const img = result.value?.image
  return img && img.height > 0 ? img.width / img.height : 1
})
const hasPose = computed(() => (result.value?.pose_landmarks.length ?? 0) > 0)

// --- Orbit state --------------------------------------------------------------
const DEFAULT_DISTANCE = 3.6
const MIN_DISTANCE = 1.2
const MAX_DISTANCE = 10
const ROTATE_SPEED = 0.008 // radians per pixel
const MAX_PITCH = Math.PI / 2

const rotationY = ref(0)
const rotationX = ref(0)
const distance = ref(DEFAULT_DISTANCE)

function resetView() {
  rotationY.value = 0
  rotationX.value = 0
  distance.value = DEFAULT_DISTANCE
}

// Each card opens with a fresh, un-rotated view.
watch(() => props.item, resetView)

// Pointer drag: yaw with horizontal movement, pitch with vertical. Two
// pointers (touch) pinch to zoom.
const pointers = new Map<number, { x: number; y: number }>()
let pinchStartDist = 0
let pinchStartDistance = DEFAULT_DISTANCE

function onPointerDown(e: PointerEvent) {
  ;(e.currentTarget as HTMLElement).setPointerCapture(e.pointerId)
  pointers.set(e.pointerId, { x: e.clientX, y: e.clientY })
  if (pointers.size === 2) {
    pinchStartDist = pinchDistance()
    pinchStartDistance = distance.value
  }
}

function onPointerMove(e: PointerEvent) {
  const prev = pointers.get(e.pointerId)
  if (!prev) return
  const cur = { x: e.clientX, y: e.clientY }
  pointers.set(e.pointerId, cur)
  if (pointers.size === 1) {
    rotationY.value += (cur.x - prev.x) * ROTATE_SPEED
    rotationX.value = clamp(rotationX.value + (cur.y - prev.y) * ROTATE_SPEED, -MAX_PITCH, MAX_PITCH)
  } else if (pointers.size === 2 && pinchStartDist > 0) {
    distance.value = clamp(pinchStartDistance * (pinchStartDist / pinchDistance()), MIN_DISTANCE, MAX_DISTANCE)
  }
}

function onPointerUp(e: PointerEvent) {
  pointers.delete(e.pointerId)
  if (pointers.size < 2) pinchStartDist = 0
}

function pinchDistance() {
  const [a, b] = Array.from(pointers.values())
  return Math.hypot(a.x - b.x, a.y - b.y) || 1
}

// Scroll to zoom: move the camera closer or further.
function onWheel(e: WheelEvent) {
  distance.value = clamp(distance.value * Math.exp(e.deltaY * 0.0015), MIN_DISTANCE, MAX_DISTANCE)
}

function clamp(v: number, lo: number, hi: number) {
  return Math.min(hi, Math.max(lo, v))
}

function gestureLabel(side: 'left' | 'right') {
  const g = result.value?.hand_gestures[side]
  return g ? g.replace(/_/g, ' ') : ''
}
</script>

<template>
  <n-modal
    :show="item !== null"
    preset="card"
    class="pose-modal"
    :title="item?.name"
    :bordered="false"
    size="small"
    :mask-closable="true"
    data-cy="pose-modal"
    @update:show="(v: boolean) => { if (!v) emit('close') }"
  >
    <div
      class="pose-modal__viewer"
      data-cy="pose-modal-viewer"
      @pointerdown="onPointerDown"
      @pointermove="onPointerMove"
      @pointerup="onPointerUp"
      @pointercancel="onPointerUp"
      @wheel.prevent="onWheel"
      @dblclick="resetView"
    >
      <TresCanvas v-if="result && hasPose" render-mode="on-demand" clear-color="#101826">
        <PoseCardScene
          :pose="result.pose_landmarks"
          :left-hand="result.hand_landmarks.left"
          :right-hand="result.hand_landmarks.right"
          :aspect="aspect"
          :rotation-y="rotationY"
          :rotation-x="rotationX"
          :distance="distance"
        />
      </TresCanvas>
      <div v-else class="pose-modal__message">No pose detected</div>
      <div class="pose-modal__hint">Drag to rotate · Scroll or pinch to zoom · Double-click to reset</div>
    </div>

    <template #footer>
      <n-space align="center" justify="space-between">
        <n-space v-if="result" size="small" align="center">
          <n-tag size="small" :bordered="false">{{ result.image.width }} × {{ result.image.height }}</n-tag>
          <n-tag v-if="gestureLabel('left')" size="small" type="info" :bordered="false">L: {{ gestureLabel('left') }}</n-tag>
          <n-tag v-if="gestureLabel('right')" size="small" type="info" :bordered="false">R: {{ gestureLabel('right') }}</n-tag>
          <n-text depth="3" class="pose-modal__saved">{{ result.saved_as }}</n-text>
        </n-space>
        <n-button size="small" data-cy="pose-modal-reset" @click="resetView">
          <template #icon><n-icon><RefreshOutline /></n-icon></template>
          Reset view
        </n-button>
      </n-space>
    </template>
  </n-modal>
</template>

<style>
/* Unscoped: n-modal renders outside this component's root. */
.pose-modal.n-card {
  width: min(92vw, 1100px);
}
.pose-modal__viewer {
  position: relative;
  width: 100%;
  height: min(72vh, 820px);
  border-radius: 8px;
  overflow: hidden;
  background: #101826;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: grab;
  user-select: none;
  touch-action: none;
}
.pose-modal__viewer:active {
  cursor: grabbing;
}
.pose-modal__viewer canvas {
  display: block;
}
.pose-modal__message {
  color: rgba(255, 255, 255, 0.6);
}
.pose-modal__hint {
  position: absolute;
  left: 0;
  right: 0;
  bottom: 10px;
  text-align: center;
  font-size: 0.8rem;
  color: rgba(255, 255, 255, 0.55);
  pointer-events: none;
}
.pose-modal__saved {
  font-size: 0.8rem;
}
</style>
