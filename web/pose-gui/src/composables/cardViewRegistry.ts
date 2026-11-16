// Shared between the Image Inference page, its cards and the single WebGL
// canvas that draws them. Each card registers the element its skeleton should
// appear in; the renderer reads the element's on-screen rectangle every frame
// it draws. Plain objects (no reactivity): the renderer polls at frame rate
// and is told to redraw through invalidate().
import type { InjectionKey } from 'vue'
import type { ImageInferenceInterface } from '@/interface/imageInferenceInterface'

export interface CardView {
  id: string
  el: HTMLElement
  result: ImageInferenceInterface
  rotationY: number
}

export class CardViewRegistry {
  readonly views = new Map<string, CardView>()
  // Set whenever something on screen changed; the renderer clears it after
  // drawing. Starts true so the first frame draws.
  dirty = true

  register(view: CardView) {
    this.views.set(view.id, view)
    this.invalidate()
  }

  unregister(id: string) {
    this.views.delete(id)
    this.invalidate()
  }

  setRotation(id: string, rotationY: number) {
    const view = this.views.get(id)
    if (view) {
      view.rotationY = rotationY
      this.invalidate()
    }
  }

  invalidate() {
    this.dirty = true
  }

  /** True once per invalidation: the renderer calls this before each frame. */
  takeDirty(): boolean {
    const d = this.dirty
    this.dirty = false
    return d
  }
}

export const cardViewRegistryKey: InjectionKey<CardViewRegistry> = Symbol('cardViewRegistry')
