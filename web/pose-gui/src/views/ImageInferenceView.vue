<template>
  <n-layout-content>
    <div class="image-inference">
      <div class="image-inference__toolbar">
        <n-button type="primary" @click="fileInput?.click()">
          <template #icon><n-icon><ImagesOutline /></n-icon></template>
          Browse images
        </n-button>
        <n-button @click="folderInput?.click()">
          <template #icon><n-icon><FolderOpenOutline /></n-icon></template>
          Browse folder
        </n-button>
        <n-text depth="3" class="image-inference__count" data-cy="image-count">
          {{ countLabel }}
        </n-text>
        <n-button quaternary :disabled="cards.length === 0" @click="clearAll">
          <template #icon><n-icon><TrashOutline /></n-icon></template>
          Clear all
        </n-button>
        <input ref="fileInput" type="file" accept="image/*" multiple hidden @change="onPick" />
        <input ref="folderInput" type="file" accept="image/*" multiple webkitdirectory hidden @change="onPick" />
      </div>

      <div class="image-inference__body">
        <!-- The whole page accepts drops; this area shows the cards and, while a
             drag is in flight or nothing has been dropped yet, the target. -->
        <div ref="areaEl" class="image-inference__area" data-cy="drop-area" @scroll.passive="onScroll">
          <!-- Virtualised: only the rows near the viewport are mounted; the
               spacer keeps the scrollbar sized for every row. -->
          <div v-if="cards.length > 0" class="image-inference__spacer" :style="{ height: `${totalHeight}px` }">
            <div
              ref="gridEl"
              class="image-inference__grid"
              :style="{ transform: `translateY(${offsetTop}px)`, gridTemplateColumns: `repeat(${columns}, minmax(0, 1fr))` }"
              :data-first-row="firstRow"
            >
              <PoseCard v-for="card in visibleCards" :key="card.id" :item="card" @remove="remove(card.id)" @open="open(card)" />
            </div>
          </div>
          <transition name="fade">
            <div v-if="dragging || cards.length === 0" class="image-inference__dropzone" :class="{ 'is-dragging': dragging }" data-cy="dropzone">
              <n-icon size="56"><CloudUploadOutline /></n-icon>
              <h2>Drop Images Here</h2>
            </div>
          </transition>
        </div>
        <!-- One WebGL canvas over the scroll area draws every card's skeleton
             (a canvas per card hits the browser's live-context limit on a big
             screen and goes blank). It never takes pointer events. -->
        <div class="image-inference__canvas" data-cy="cards-canvas">
          <!-- Tres renders its own (empty) scene once on mount even in manual
               mode, which clears the canvas; redraw the cards after it. -->
          <TresCanvas
            v-if="cards.length > 0"
            render-mode="manual"
            alpha
            :clear-alpha="0"
            @ready="registry.invalidate()"
            @render="registry.invalidate()"
          >
            <PoseCardsRenderer :registry="registry" />
          </TresCanvas>
        </div>
      </div>

      <!-- Click a card to inspect its skeleton full size -->
      <PoseModal :item="selected" :items="doneCards" @close="selected = null" @select="open($event)" />
    </div>
  </n-layout-content>
</template>

<script setup lang="ts">
import { computed, nextTick, onMounted, onUnmounted, provide, reactive, ref, watch } from 'vue'
import { NLayoutContent, NButton, NIcon, NText } from 'naive-ui'
import { TresCanvas } from '@tresjs/core'
import { CloudUploadOutline, ImagesOutline, FolderOpenOutline, TrashOutline } from '@vicons/ionicons5'
import PoseCard from '@/components/PoseCard.vue'
import PoseCardsRenderer from '@/components/PoseCardsRenderer'
import PoseModal from '@/components/PoseModal.vue'
import { CardViewRegistry, cardViewRegistryKey } from '@/composables/cardViewRegistry'
import { loadCards, hydrate, saveCard, removeCard, clearCards, flushIndex } from '@/composables/cardStore'
import { inferenceImage } from '@/composables/restApiService'
import type { InferenceCard } from '@/interface/imageInferenceInterface'

const IMAGE_EXTENSIONS = ['jpg', 'jpeg', 'png', 'bmp', 'webp']

// Cards register their view areas here; the shared canvas draws into them.
const registry = new CardViewRegistry()
provide(cardViewRegistryKey, registry)

// --- Persistence ------------------------------------------------------------
// Finished cards survive a reload (see cardStore). Pending and failed cards
// are not saved: a request can't be resumed. Results of restored cards are
// loaded lazily when a card is first shown.
const cards = ref<InferenceCard[]>(loadCards())
// The card currently open in the modal, if any
const selected = ref<InferenceCard | null>(null)
const fileInput = ref<HTMLInputElement | null>(null)
const folderInput = ref<HTMLInputElement | null>(null)
const areaEl = ref<HTMLElement | null>(null)
const gridEl = ref<HTMLElement | null>(null)
// Continue numbering after whatever was restored so ids never collide.
let nextId = cards.value.reduce((max, c) => Math.max(max, Number(c.id.replace(/^img-/, '')) + 1 || 0), 0)

function open(card: InferenceCard) {
  hydrate(card)
  selected.value = card
}

// --- Virtual grid -------------------------------------------------------------
// The grid is `repeat(auto-fill, minmax(MIN_CARD_WIDTH, 1fr))` in spirit, but
// computed here so the row height is known and only rows near the viewport
// are rendered. Card height is measured from the first rendered card.
const MIN_CARD_WIDTH = 240
const GRID_GAP = 12
const AREA_PADDING = 12
const BUFFER_ROWS = 1 // extra rows rendered above and below the viewport

const areaWidth = ref(0)
const areaHeight = ref(0)
const scrollTop = ref(0)
const cardHeight = ref(0) // 0 until measured

const columns = computed(() => Math.max(1, Math.floor((areaWidth.value - 2 * AREA_PADDING + GRID_GAP) / (MIN_CARD_WIDTH + GRID_GAP))))
const cardWidth = computed(() => (areaWidth.value - 2 * AREA_PADDING - (columns.value - 1) * GRID_GAP) / columns.value)
// Before the first measurement, estimate: 4:5 view plus the header and paddings.
const rowHeight = computed(() => (cardHeight.value || cardWidth.value * 1.25 + 60) + GRID_GAP)
const rowCount = computed(() => Math.ceil(cards.value.length / columns.value))
const totalHeight = computed(() => Math.max(0, rowCount.value * rowHeight.value - GRID_GAP))
const firstRow = computed(() => Math.max(0, Math.floor((scrollTop.value - AREA_PADDING) / rowHeight.value) - BUFFER_ROWS))
const lastRow = computed(() => Math.min(rowCount.value - 1, Math.ceil((scrollTop.value - AREA_PADDING + areaHeight.value) / rowHeight.value) + BUFFER_ROWS))
const offsetTop = computed(() => firstRow.value * rowHeight.value)
const visibleCards = computed(() => cards.value.slice(firstRow.value * columns.value, (lastRow.value + 1) * columns.value))

function measureArea() {
  if (!areaEl.value) return
  areaWidth.value = areaEl.value.clientWidth
  areaHeight.value = areaEl.value.clientHeight
  scrollTop.value = areaEl.value.scrollTop
}

// Scroll events arrive faster than frames; sample once per frame.
let scrollFrame = 0
function onScroll() {
  registry.invalidate()
  if (scrollFrame) return
  scrollFrame = requestAnimationFrame(() => {
    scrollFrame = 0
    if (areaEl.value) scrollTop.value = areaEl.value.scrollTop
  })
}

function measureCard() {
  const first = gridEl.value?.firstElementChild as HTMLElement | null
  if (first) {
    const h = first.getBoundingClientRect().height
    if (h > 0 && Math.abs(h - cardHeight.value) > 0.5) cardHeight.value = h
  }
}
// Re-measure when the column width or the rendered set changes.
watch([cardWidth, visibleCards], () => nextTick(measureCard), { flush: 'post' })

// Cards the modal can step through (only finished ones can be opened).
const doneCards = computed(() => cards.value.filter(c => c.status === 'done'))

const countLabel = computed(() => {
  const total = cards.value.length
  if (total === 0) return 'No images yet'
  const pending = cards.value.filter(c => c.status === 'pending').length
  return pending > 0 ? `${total} image${total === 1 ? '' : 's'}, ${pending} inferencing` : `${total} image${total === 1 ? '' : 's'}`
})

function isImage(file: File) {
  if (file.type.startsWith('image/')) return true
  const ext = file.name.split('.').pop()?.toLowerCase() ?? ''
  return IMAGE_EXTENSIONS.includes(ext)
}

function addFiles(files: File[]) {
  files.filter(isImage).forEach(file => {
    // reactive() so the status updates below (made through this reference,
    // not through the array) still re-render the card.
    const card = reactive<InferenceCard>({ id: `img-${nextId++}`, name: file.name, size: file.size, status: 'pending' })
    cards.value.push(card)
    inferenceImage(file)
      .then(result => {
        card.result = result
        card.status = 'done'
        saveCard(card, cards.value)
      })
      .catch(err => {
        card.error = err?.response?.data?.detail ?? err?.message ?? 'Request failed'
        card.status = 'error'
      })
  })
}

function remove(id: string) {
  cards.value = cards.value.filter(c => c.id !== id)
  if (selected.value?.id === id) selected.value = null
  removeCard(id, cards.value)
}

function clearAll() {
  cards.value = []
  selected.value = null
  clearCards()
}

function onPick(e: Event) {
  const input = e.target as HTMLInputElement
  addFiles(Array.from(input.files ?? []))
  input.value = '' // allow picking the same files again
}

// --- Drag and drop ----------------------------------------------------------
// Listening on the window (rather than the drop area) means the target shows
// as soon as a file enters the page and a drop anywhere lands here. dragenter
// and dragleave fire for every child element crossed, so count them.
const dragging = ref(false)
let dragDepth = 0

function hasFiles(e: DragEvent) {
  return Array.from(e.dataTransfer?.types ?? []).includes('Files')
}

function onDragEnter(e: DragEvent) {
  if (!hasFiles(e)) return
  e.preventDefault()
  dragDepth++
  dragging.value = true
}
function onDragOver(e: DragEvent) {
  if (!hasFiles(e)) return
  e.preventDefault()
  if (e.dataTransfer) e.dataTransfer.dropEffect = 'copy'
}
function onDragLeave(e: DragEvent) {
  if (!hasFiles(e)) return
  dragDepth = Math.max(0, dragDepth - 1)
  if (dragDepth === 0) dragging.value = false
}
async function onDrop(e: DragEvent) {
  if (!hasFiles(e)) return
  e.preventDefault()
  dragDepth = 0
  dragging.value = false
  addFiles(await filesFromDataTransfer(e.dataTransfer!))
}

// Dropped folders arrive as directory entries; walk them for their images.
async function filesFromDataTransfer(dt: DataTransfer): Promise<File[]> {
  const items = Array.from(dt.items ?? [])
  const entries = items.map(item => (item.webkitGetAsEntry ? item.webkitGetAsEntry() : null))
  if (!entries.some(e => e?.isDirectory)) {
    return Array.from(dt.files)
  }
  const files: File[] = []
  for (const entry of entries) {
    if (entry) await walkEntry(entry, files)
  }
  return files
}

function walkEntry(entry: FileSystemEntry, out: File[]): Promise<void> {
  if (entry.isFile) {
    return new Promise(resolve => (entry as FileSystemFileEntry).file(f => { out.push(f); resolve() }, () => resolve()))
  }
  if (entry.isDirectory) {
    const reader = (entry as FileSystemDirectoryEntry).createReader()
    // readEntries returns results in batches; keep reading until it is empty.
    const readAll = (): Promise<FileSystemEntry[]> => new Promise(resolve => {
      const all: FileSystemEntry[] = []
      const step = () => reader.readEntries(batch => {
        if (batch.length === 0) return resolve(all)
        all.push(...batch)
        step()
      }, () => resolve(all))
      step()
    })
    return readAll().then(async children => {
      for (const child of children) await walkEntry(child, out)
    })
  }
  return Promise.resolve()
}

// Card rectangles move on scroll and on any layout change; redraw then.
const invalidateCanvas = () => registry.invalidate()

onMounted(() => {
  window.addEventListener('dragenter', onDragEnter)
  window.addEventListener('dragover', onDragOver)
  window.addEventListener('dragleave', onDragLeave)
  window.addEventListener('drop', onDrop)
  window.addEventListener('resize', invalidateCanvas)
  window.addEventListener('scroll', invalidateCanvas, true)
})

onUnmounted(() => {
  window.removeEventListener('dragenter', onDragEnter)
  window.removeEventListener('dragover', onDragOver)
  window.removeEventListener('dragleave', onDragLeave)
  window.removeEventListener('drop', onDrop)
  window.removeEventListener('resize', invalidateCanvas)
  window.removeEventListener('scroll', invalidateCanvas, true)
})

// Cards appearing/disappearing shifts the grid; redraw after the DOM settles.
watch(() => cards.value.length, () => requestAnimationFrame(invalidateCanvas))

// Any reflow of the grid (a column count change when the scrollbar appears,
// a font load, ...) moves the card rectangles without a scroll or resize
// event, so watch the grid's own size as well. The scroll area's size drives
// the virtual window.
const gridObserver = typeof ResizeObserver !== 'undefined' ? new ResizeObserver(() => { invalidateCanvas(); measureCard() }) : null
watch(gridEl, el => {
  gridObserver?.disconnect()
  if (el) gridObserver?.observe(el)
})
const areaObserver = typeof ResizeObserver !== 'undefined' ? new ResizeObserver(() => { measureArea(); invalidateCanvas() }) : null
watch(areaEl, el => {
  areaObserver?.disconnect()
  if (el) {
    areaObserver?.observe(el)
    measureArea()
  }
}, { immediate: true })
const flush = () => flushIndex(cards.value)
onMounted(() => window.addEventListener('pagehide', flush))
onUnmounted(() => {
  gridObserver?.disconnect()
  areaObserver?.disconnect()
  window.removeEventListener('pagehide', flush)
  flush()
  if (scrollFrame) cancelAnimationFrame(scrollFrame)
})
</script>

<style scoped lang="scss">
$gap: 12px;

.image-inference {
  display: flex;
  flex-direction: column;
  height: 100%;
}

.image-inference__toolbar {
  display: flex;
  align-items: center;
  gap: $gap;
  padding: $gap;
  border-bottom: 1px solid rgba(128, 128, 128, 0.2);
}

.image-inference__count {
  margin-left: auto;
}

// The scroll area and the canvas over it share this box.
.image-inference__body {
  position: relative;
  flex: 1;
  min-height: 0;
}

.image-inference__area {
  position: absolute;
  inset: 0;
  overflow: auto;
  padding: $gap;
}

.image-inference__canvas {
  position: absolute;
  inset: 0;
  pointer-events: none;
  z-index: 1;

  // TresCanvas sets pointer-events: auto inline on its canvas, which would
  // override the wrapper and swallow every click on the cards beneath.
  :deep(canvas) {
    pointer-events: none !important;
  }
}

.image-inference__spacer {
  position: relative;
}

.image-inference__grid {
  display: grid;
  // Columns are computed in the script (see MIN_CARD_WIDTH) so the row
  // height is known for virtual scrolling; the gap must match GRID_GAP.
  gap: $gap;
  align-items: start;
  will-change: transform;
}

// Full-area drop target; sits over the cards while a drag is in flight.
.image-inference__dropzone {
  position: absolute;
  inset: $gap;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-align: center;
  gap: 0.5rem;
  padding: 2rem;
  border: 3px dashed rgba(44, 62, 80, 0.5);
  border-radius: 12px;
  z-index: 2;
  color: #2c3e50;
  background: rgba(255, 255, 255, 0.85);
  pointer-events: none;

  h2 {
    font-size: 1.6rem;
    font-weight: 600;
  }
  p {
    max-width: 36rem;
    opacity: 0.75;
  }
  code {
    font-size: 0.85em;
  }

  &.is-dragging {
    border-color: #18a058;
    color: #18a058;
    background: rgba(24, 160, 88, 0.08);
  }
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.15s ease;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
