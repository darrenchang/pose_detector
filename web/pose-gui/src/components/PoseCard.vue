<script setup lang="ts">
// One dropped image: a spinner while the server works, then the detected
// skeleton (drag sideways to turn it), or the error. The skeleton itself is
// drawn by the page's shared PoseCardsRenderer into this card's view area;
// the card only registers that area and its rotation.
import { computed, inject, onMounted, onUnmounted, ref, watch } from 'vue'
import { NCard, NButton, NIcon, NSpin } from 'naive-ui'
import { TrashOutline } from '@vicons/ionicons5'
import { cardViewRegistryKey } from '@/composables/cardViewRegistry'
import { hydrate } from '@/composables/cardStore'
import type { InferenceCard } from '@/interface/imageInferenceInterface'

const props = defineProps<{ item: InferenceCard }>()
const emit = defineEmits<{ remove: []; open: [] }>()

const registry = inject(cardViewRegistryKey)
const result = computed(() => props.item.result)
const hasPose = computed(() => (result.value?.pose_landmarks.length ?? 0) > 0)
const drawable = computed(() => props.item.status === 'done' && !!result.value && hasPose.value)

const viewport = ref<HTMLElement | null>(null)

function register() {
  if (registry && viewport.value && drawable.value && result.value) {
    registry.register({ id: props.item.id, el: viewport.value, result: result.value, rotationY: rotationY.value })
  }
}
function unregister() {
  registry?.unregister(props.item.id)
}

onMounted(() => {
  // A restored card has no result until it is first shown.
  hydrate(props.item)
  register()
})
onUnmounted(unregister)
// A pending card becomes drawable once its result arrives.
watch(drawable, d => (d ? register() : unregister()))

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
  registry?.setRotation(props.item.id, rotationY.value)
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

    <!-- The shared renderer paints the skeleton over this element -->
    <div
      ref="viewport"
      class="pose-card__view"
      :class="{ 'pose-card__view--interactive': drawable }"
      data-cy="pose-card-view"
      :data-drawable="drawable"
      @pointerdown="onPointerDown"
      @pointermove="onPointerMove"
      @pointerup="onPointerUp"
      @pointercancel="onPointerUp"
    >
      <template v-if="item.status === 'done' && result">
        <div v-if="!hasPose" class="pose-card__message">No pose detected</div>
      </template>
      <n-spin v-else-if="item.status === 'pending'" size="large" />
      <div v-else class="pose-card__message pose-card__message--error">{{ item.error }}</div>
    </div>
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
.pose-card__message {
  color: rgba(255, 255, 255, 0.6);
  padding: 1rem;
  text-align: center;
}
.pose-card__message--error {
  color: #ff7a7a;
}
</style>
