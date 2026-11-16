// localStorage persistence for the Image Inference cards.
//
// Each finished card's result is stored under its own key and a small index
// lists the cards in order, so adding or removing one card writes only that
// card (the previous single-blob format re-serialised every card on every
// change, which made a large folder drop quadratic). Results are only read
// back when a card is first shown (hydrate), so restoring hundreds of cards
// costs one small index parse.
import { reactive } from 'vue'
import type { ImageInferenceInterface, InferenceCard } from '@/interface/imageInferenceInterface'

const INDEX_KEY = 'imageInference.index'
const CARD_PREFIX = 'imageInference.card.'
const LEGACY_KEY = 'imageInference.cards'

interface IndexEntry {
  id: string
  name: string
  size: number
}

function cardKey(id: string) {
  return CARD_PREFIX + id
}

function readIndex(): IndexEntry[] {
  try {
    const raw = localStorage.getItem(INDEX_KEY)
    return raw ? (JSON.parse(raw) as IndexEntry[]) : []
  } catch {
    return []
  }
}

function writeIndex(cards: InferenceCard[]) {
  try {
    const entries: IndexEntry[] = cards
      .filter(c => c.status === 'done')
      .map(c => ({ id: c.id, name: c.name, size: c.size }))
    localStorage.setItem(INDEX_KEY, JSON.stringify(entries))
  } catch (e) {
    console.warn('Could not save the card index', e)
  }
}

// One-off migration from the single-blob format.
function migrateLegacy() {
  try {
    const raw = localStorage.getItem(LEGACY_KEY)
    if (!raw) return
    const saved = JSON.parse(raw) as InferenceCard[]
    const cards = saved.filter(c => c && c.status === 'done' && c.result)
    cards.forEach(c => localStorage.setItem(cardKey(c.id), JSON.stringify(c.result)))
    writeIndex(cards)
    localStorage.removeItem(LEGACY_KEY)
  } catch (e) {
    console.warn('Could not migrate saved cards', e)
  }
}

/** Cards saved by a previous session, without their results (see hydrate). */
export function loadCards(): InferenceCard[] {
  migrateLegacy()
  return readIndex().map(e => reactive<InferenceCard>({ id: e.id, name: e.name, size: e.size, status: 'done' }))
}

/** Load a restored card's result from storage the first time it is needed. */
export function hydrate(card: InferenceCard): ImageInferenceInterface | undefined {
  if (card.result || card.status !== 'done') return card.result
  try {
    const raw = localStorage.getItem(cardKey(card.id))
    if (raw) card.result = JSON.parse(raw) as ImageInferenceInterface
  } catch (e) {
    console.warn(`Could not load the saved result for ${card.name}`, e)
  }
  if (!card.result) {
    // Its entry is gone or unreadable: show it as failed rather than blank.
    card.status = 'error'
    card.error = 'Saved result is missing'
  }
  return card.result
}

/** Persist one finished card; the index is rewritten by the caller. */
export function saveCard(card: InferenceCard, all: InferenceCard[]) {
  if (card.status !== 'done' || !card.result) return
  try {
    localStorage.setItem(cardKey(card.id), JSON.stringify(card.result))
  } catch (e) {
    // Quota exceeded or storage disabled: the page keeps working, this card
    // just won't survive a reload.
    console.warn(`Could not save ${card.name}`, e)
    return
  }
  scheduleIndexWrite(all)
}

export function removeCard(id: string, remaining: InferenceCard[]) {
  try {
    localStorage.removeItem(cardKey(id))
  } catch { /* storage disabled */ }
  scheduleIndexWrite(remaining)
}

export function clearCards() {
  try {
    for (let i = localStorage.length - 1; i >= 0; i--) {
      const k = localStorage.key(i)
      if (k && (k.startsWith(CARD_PREFIX) || k === INDEX_KEY || k === LEGACY_KEY)) localStorage.removeItem(k)
    }
  } catch { /* storage disabled */ }
}

// Many cards finish within the same second during a folder drop; write the
// index once they settle instead of once per card.
let indexTimer: ReturnType<typeof setTimeout> | null = null
function scheduleIndexWrite(cards: InferenceCard[]) {
  if (indexTimer !== null) clearTimeout(indexTimer)
  indexTimer = setTimeout(() => {
    indexTimer = null
    writeIndex(cards)
  }, 300)
}

/** Write any pending index update now (e.g. before the page unloads). */
export function flushIndex(cards: InferenceCard[]) {
  if (indexTimer !== null) {
    clearTimeout(indexTimer)
    indexTimer = null
    writeIndex(cards)
  }
}
