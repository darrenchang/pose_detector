import { computed } from 'vue'
import { defineStore } from 'pinia'

export const usePostLandmarksStore = defineStore('postLandmarks', () => {
  let poseLandmarks: number[] = [3, 3, 3];
  const getPoseLandmarks = computed(() => poseLandmarks)
  function updatePoseLandmarks(value: number[]) {
    poseLandmarks = value;
  }

  return { poseLandmarks, updatePoseLandmarks, getPoseLandmarks }
})
