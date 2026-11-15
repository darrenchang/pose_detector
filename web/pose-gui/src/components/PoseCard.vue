<script setup lang="ts">
// One dropped image: a spinner while the server works, then the detected
// skeleton drawn with TresJS (drag sideways to turn it), or the error.
import { computed, onMounted, onUnmounted, ref } from 'vue'
import { NCard, NButton, NIcon, NSpin, NTag, NSpace, NText } from 'naive-ui'
import { TresCanvas } from '@tresjs/core'
import { TrashOutline } from '@vicons/ionicons5'
import PoseCardScene from '@/components/PoseCardScene.vue'
import type { InferenceCard } from '@/interface/imageInferenceInterface'

const props = defineProps<{ item: InferenceCard }>()
const emit = defineEmits<{ remove: []; open: [] }>()

const result = computed(() => props.item.result)
const aspect = computed(() => {
  const img = result.value?.image
  return img && img.height > 0 ? img.width / img.height : 1
})
const hasPose = computed(() => (result.value?.pose_landmarks.length ?? 0) > 0)

// Browsers allow only a handful of live WebGL contexts per page, so a card
// only holds a canvas while it is scrolled into view.
const viewport = ref<HTMLElement | null>(null)
const visible = ref(false)
let observer: IntersectionObserver | null = null

onMounted(() => {
  if (typeof IntersectionObserver === 'undefined' || !viewport.value) {
    visible.value = true
    return
  }
  observer = new IntersectionObserver(
    entries => { visible.value = entries.some(e => e.isIntersecting) },
    { rootMargin: '100px' },
  )
  observer.observe(viewport.value)
})
onUnmounted(() => observer?.disconnect())

// Drag sideways to rotate the skeleton; a click (no real movement) opens
// the card in the modal instead.
const DRAG_THRESHOLD = 4 // px of movement before a press counts as a drag
const rotationY = ref(0)
let dragStartX = 0
let dragStartRotation = 0
let dragging = false
let dragged = false

function onPointerDown(e: PointerEvent) {
  dragging = true
  dragged = false
  dragStartX = e.clientX
  dragStartRotation = rotationY.value
  ;(e.currentTarget as HTMLElement).setPointerCapture(e.pointerId)
}
function onPointerMove(e: PointerEvent) {
  if (!dragging) return
  const dx = e.clientX - dragStartX
  if (Math.abs(dx) > DRAG_THRESHOLD) dragged = true
  rotationY.value = dragStartRotation + dx * 0.01
}
function onPointerUp() {
  dragging = false
}

function onCardClick() {
  if (dragged) {
    // The click that ends a drag is not a request to open the card
    dragged = false
    return
  }
  if (props.item.status === 'done') emit('open')
}

function gestureLabel(side: 'left' | 'right') {
  const g = result.value?.hand_gestures[side]
  if (!g) return ''
  return g.replace(/_/g, ' ')
}
</script>

<template>
  <n-card
    class="pose-card"
    :class="{ 'pose-card--openable': item.status === 'done' }"
    size="small"
    :bordered="true"
    data-cy="pose-card"
    :data-status="item.status"
    @click="onCardClick"
  >
    <template #header>
      <span class="pose-card__title" :title="item.name">{{ item.name }}</span>
    </template>
    <template #header-extra>
      <n-button quaternary circle size="small" title="Remove" aria-label="Remove" @click.stop="emit('remove')">
        <template #icon><n-icon><TrashOutline /></n-icon></template>
      </n-button>
    </template>

    <div
      ref="viewport"
      class="pose-card__view"
      :class="{ 'pose-card__view--interactive': item.status === 'done' && hasPose }"
      @pointerdown="onPointerDown"
      @pointermove="onPointerMove"
      @pointerup="onPointerUp"
      @pointercancel="onPointerUp"
    >
      <template v-if="item.status === 'done' && result">
        <TresCanvas v-if="visible && hasPose" render-mode="on-demand" clear-color="#101826">
          <PoseCardScene
            :pose="result.pose_landmarks"
            :left-hand="result.hand_landmarks.left"
            :right-hand="result.hand_landmarks.right"
            :aspect="aspect"
            :rotation-y="rotationY"
          />
        </TresCanvas>
        <div v-if="!hasPose" class="pose-card__message">No pose detected</div>
      </template>
      <n-spin v-else-if="item.status === 'pending'" size="large" />
      <div v-else class="pose-card__message pose-card__message--error">{{ item.error }}</div>
    </div>

    <template #footer>
      <n-space size="small" align="center">
        <template v-if="result">
          <n-tag size="small" :bordered="false">{{ result.image.width }} × {{ result.image.height }}</n-tag>
          <n-tag v-if="gestureLabel('left')" size="small" type="info" :bordered="false">L: {{ gestureLabel('left') }}</n-tag>
          <n-tag v-if="gestureLabel('right')" size="small" type="info" :bordered="false">R: {{ gestureLabel('right') }}</n-tag>
          <n-text depth="3" class="pose-card__saved" :title="result.saved_as">{{ result.saved_as }}</n-text>
        </template>
        <n-text v-else depth="3">{{ item.status === 'pending' ? 'Inferencing…' : 'Failed' }}</n-text>
      </n-space>
    </template>
  </n-card>
</template>

<style scoped>
.pose-card--openable {
  cursor: pointer;
  transition: box-shadow 0.15s ease;
}
.pose-card--openable:hover {
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.12);
}
.pose-card__title {
  display: block;
  overflow: hidden;
  white-space: nowrap;
  text-overflow: ellipsis;
  font-size: 0.9rem;
}
.pose-card__view {
  position: relative;
  aspect-ratio: 4 / 5;
  width: 100%;
  border-radius: 6px;
  overflow: hidden;
  background: #101826;
  display: flex;
  align-items: center;
  justify-content: center;
  user-select: none;
  touch-action: pan-y;
}
.pose-card__view--interactive {
  cursor: grab;
}
.pose-card__view--interactive:active {
  cursor: grabbing;
}
.pose-card__view :deep(canvas) {
  display: block;
}
.pose-card__message {
  color: rgba(255, 255, 255, 0.6);
  padding: 1rem;
  text-align: center;
}
.pose-card__message--error {
  color: #ff7a7a;
}
.pose-card__saved {
  font-size: 0.75rem;
  max-width: 100%;
  overflow: hidden;
  white-space: nowrap;
  text-overflow: ellipsis;
}
</style>
