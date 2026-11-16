<script setup lang="ts">
// A card opened full size: the same TresJS skeleton, but with free orbit
// (drag), zoom (scroll / pinch) and a reset, so the model can be inspected.
import { computed, onMounted, onUnmounted, ref, watch } from 'vue'
import { NModal, NButton, NIcon, NSpace } from 'naive-ui'
import { TresCanvas } from '@tresjs/core'
import { RefreshOutline, ChevronBackOutline, ChevronForwardOutline } from '@vicons/ionicons5'
import PoseCardScene from '@/components/PoseCardScene.vue'
import type { InferenceCard } from '@/interface/imageInferenceInterface'

const props = defineProps<{
  item: InferenceCard | null
  // Every card that can be shown, in page order, for previous / next.
  items: InferenceCard[]
}>()
const emit = defineEmits<{ close: []; select: [card: InferenceCard] }>()

// --- Previous / next ------------------------------------------------------------
const index = computed(() => (props.item ? props.items.findIndex(c => c.id === props.item!.id) : -1))
const hasPrev = computed(() => index.value > 0)
const hasNext = computed(() => index.value >= 0 && index.value < props.items.length - 1)
const title = computed(() =>
  props.item ? `${props.item.name}  (${index.value + 1} / ${props.items.length})` : '',
)

function goPrev() {
  if (hasPrev.value) emit('select', props.items[index.value - 1])
}
function goNext() {
  if (hasNext.value) emit('select', props.items[index.value + 1])
}

// Arrow keys navigate while the modal is open.
function onKeyDown(e: KeyboardEvent) {
  if (props.item === null) return
  if (e.key === 'ArrowLeft') {
    e.preventDefault()
    goPrev()
  } else if (e.key === 'ArrowRight') {
    e.preventDefault()
    goNext()
  }
}
onMounted(() => window.addEventListener('keydown', onKeyDown))
onUnmounted(() => window.removeEventListener('keydown', onKeyDown))

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
</script>

<template>
  <n-modal
    :show="item !== null"
    preset="card"
    class="pose-modal"
    :title="title"
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
      <div class="pose-modal__hint">Drag to rotate · Scroll or pinch to zoom · Double-click to reset · ← → previous / next</div>

      <!-- Previous / next. pointerdown is stopped so a click here never starts an orbit drag. -->
      <n-button
        class="pose-modal__nav pose-modal__nav--prev"
        circle
        secondary
        size="large"
        :disabled="!hasPrev"
        title="Previous (←)"
        aria-label="Previous"
        data-cy="pose-modal-prev"
        @pointerdown.stop
        @click.stop="goPrev"
      >
        <template #icon><n-icon><ChevronBackOutline /></n-icon></template>
      </n-button>
      <n-button
        class="pose-modal__nav pose-modal__nav--next"
        circle
        secondary
        size="large"
        :disabled="!hasNext"
        title="Next (→)"
        aria-label="Next"
        data-cy="pose-modal-next"
        @pointerdown.stop
        @click.stop="goNext"
      >
        <template #icon><n-icon><ChevronForwardOutline /></n-icon></template>
      </n-button>
    </div>

    <template #footer>
      <n-space justify="end">
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
.pose-modal__nav.n-button {
  position: absolute;
  top: 50%;
  transform: translateY(-50%);
  cursor: pointer;
  /* Naive's secondary button is styled for a light page; lift it off the
     dark viewer. */
  --n-color: rgba(255, 255, 255, 0.16);
  --n-color-hover: rgba(255, 255, 255, 0.3);
  --n-color-pressed: rgba(255, 255, 255, 0.4);
  --n-text-color: #fff;
  --n-text-color-hover: #fff;
  --n-text-color-pressed: #fff;
  --n-text-color-focus: #fff;
}
.pose-modal__nav.n-button:disabled {
  opacity: 0.25;
}
.pose-modal__nav--prev {
  left: 12px;
}
.pose-modal__nav--next {
  right: 12px;
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
</style>
