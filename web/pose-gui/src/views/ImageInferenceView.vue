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

      <!-- The whole page accepts drops; this area shows the cards and, while a
           drag is in flight or nothing has been dropped yet, the target. -->
      <div class="image-inference__area" data-cy="drop-area">
        <div v-if="cards.length > 0" class="image-inference__grid">
          <PoseCard v-for="card in cards" :key="card.id" :item="card" @remove="remove(card.id)" @open="selected = card" />
        </div>
        <transition name="fade">
          <div v-if="dragging || cards.length === 0" class="image-inference__dropzone" :class="{ 'is-dragging': dragging }" data-cy="dropzone">
            <n-icon size="56"><CloudUploadOutline /></n-icon>
            <h2>Drop Images Here</h2>
            <p>Each image is sent to the server for pose and hand detection; the result is saved under <code>app/src/poses_data/</code> and drawn below as a skeleton.</p>
          </div>
        </transition>
      </div>

      <!-- Click a card to inspect its skeleton full size -->
      <PoseModal :item="selected" @close="selected = null" />
    </div>
  </n-layout-content>
</template>

<script setup lang="ts">
import { computed, onMounted, onUnmounted, reactive, ref } from 'vue'
import { NLayoutContent, NButton, NIcon, NText } from 'naive-ui'
import { CloudUploadOutline, ImagesOutline, FolderOpenOutline, TrashOutline } from '@vicons/ionicons5'
import PoseCard from '@/components/PoseCard.vue'
import PoseModal from '@/components/PoseModal.vue'
import { inferenceImage } from '@/composables/restApiService'
import type { InferenceCard } from '@/interface/imageInferenceInterface'

const IMAGE_EXTENSIONS = ['jpg', 'jpeg', 'png', 'bmp', 'webp']

const cards = ref<InferenceCard[]>([])
// The card currently open in the modal, if any
const selected = ref<InferenceCard | null>(null)
const fileInput = ref<HTMLInputElement | null>(null)
const folderInput = ref<HTMLInputElement | null>(null)
let nextId = 0

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
}

function clearAll() {
  cards.value = []
  selected.value = null
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

onMounted(() => {
  window.addEventListener('dragenter', onDragEnter)
  window.addEventListener('dragover', onDragOver)
  window.addEventListener('dragleave', onDragLeave)
  window.addEventListener('drop', onDrop)
})

onUnmounted(() => {
  window.removeEventListener('dragenter', onDragEnter)
  window.removeEventListener('dragover', onDragOver)
  window.removeEventListener('dragleave', onDragLeave)
  window.removeEventListener('drop', onDrop)
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

.image-inference__area {
  position: relative;
  flex: 1;
  min-height: 0;
  overflow: auto;
  padding: $gap;
}

.image-inference__grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
  gap: $gap;
  align-items: start;
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
  z-index: 1;
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
