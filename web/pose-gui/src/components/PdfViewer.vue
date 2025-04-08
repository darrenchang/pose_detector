<template>
  <n-layout-content>
    <div class="overlay absolute w-full h-full z-256">
      {{ dwellTimer.nextPage }} <br>
      {{ dwellTimer.prevPage }} <br>
      {{ currentPage }} <br>
      {{ nextProgress }} <br>
      {{ prevProgress }}
      <TresCanvas>
        <TresPerspectiveCamera :position="[0, 0, 6]" :fov="45" :look-at="[0, 0, 0]"/>
        <TresGroup ref="poseLandmarksGroupRef" :position="[0, 0, 0]" :visible="false">
          <TresMesh v-for="(landmark, key) in poseLandmarks" :name="key" :key="key" :position="[-1, -1, -1]">
            <TresBoxGeometry :args="landmark.cubeSize"/>
            <TresMeshNormalMaterial :color="landmark.cubeColor"/>
          </TresMesh>
        </TresGroup>
        <TresGroup ref="leftHandLandmarksGroupRef" :position="[0, 0, 0]">
          <TresMesh v-for="(landmark, key) in leftHandLandmarks" :name="key" :key="key" :position="[-1, -1, -1]">
            <TresBoxGeometry :args="landmark.cubeSize"/>
            <TresMeshNormalMaterial :color="landmark.cubeColor"/>
          </TresMesh>
        </TresGroup>
        <TresGroup ref="rightHandLandmarksGroupRef" :position="[0, 0, 0]">
          <TresMesh v-for="(landmark, key) in rightHandLandmarks" :name="key" :key="key" :position="[-1, -1, -1]">
            <TresBoxGeometry :args="landmark.cubeSize"/>
            <TresMeshNormalMaterial :color="landmark.cubeColor"/>
          </TresMesh>
        </TresGroup>
        <TresAmbientLight :intensity="1"/>
      </TresCanvas>
    </div>
    <n-layout-content>
      <div class="grid grid-cols-6">
        <div class="flex justify-center items-center">
          <n-progress type="circle" :percentage="prevProgress" :color="dwellTimer.prevPage.progressColor"/>
        </div>
        <div ref="pdfLayersWrapper" class="border-none m-auto col-span-4"
             :style="{ width: `${pdfWidth}px`, height: `${pdfHeight}px` }">
          <div class="pdf__canvas-layer">
            <canvas ref="canvasLayer"/>
          </div>
          <div ref="textLayer" class="pdf__text-layer hidden"></div>
          <div ref="annotationLayer" class="pdf__annotation-layer"></div>
        </div>
        <div class="flex justify-center items-center">
          <n-progress type="circle" :percentage="nextProgress" :color="dwellTimer.nextPage.progressColor"/>
        </div>
      </div>
    </n-layout-content>
  </n-layout-content>
</template>

<script setup lang="ts">
import { NLayoutContent, NProgress } from 'naive-ui';
import type { Ref, ComputedRef } from 'vue';
import { computed, onMounted, ref, shallowRef, watch, watchEffect } from 'vue';
import { pdfjsLib, pdfWorkerLib, SimpleLinkService } from '@/composables/pdfjsLib';
import { poseLandmarks } from '@/interface/poseLandmarksInterface';
import { leftHandLandmarks, rightHandLandmarks } from '@/interface/handLandmarksInterface';
import { TresCanvas, useRenderLoop } from '@tresjs/core';

const pdfLayersWrapper: Ref<any> = ref(null);
const canvasLayer: Ref<any> = ref(null);
const textLayer: Ref<any> = ref(null);
const annotationLayer: Ref<any> = ref(null);
const pdfSrc: string = 'https://pdfobject.com/pdf/pdf_open_parameters_acro8.pdf';
let pdfProxy = undefined;
let pdf = undefined;
const { onLoop } = useRenderLoop();
const currentPage: Ref<number> = ref(1);
const totalPages: Ref<number> = ref(3);
const pdfWidth: Ref<number> = ref(0);
const pdfHeight: Ref<number> = ref(0);

interface dwellTimerData {
  "nextPage": {
    currentAccTime: number
    triggerTime: number
    progressColor: string
  },
  "prevPage": {
    currentAccTime: number
    triggerTime: number
    progressColor: string
  }

}

const dwellTimer: Ref<dwellTimerData> = ref({
  nextPage: {
    currentAccTime: 0,
    triggerTime: 1,
    progressColor: '#007bff',
  },
  prevPage: {
    currentAccTime: 0,
    triggerTime: 1,
    progressColor: '#007bff',
  }
});


const nextPage = () => {
  if(currentPage.value < totalPages.value) {
    currentPage.value++;
  }
};
const prevPage = () => {
  if(currentPage.value > 1) {
    currentPage.value--;
  }
};

const getProgress = (timer): number => {
  const progress: number = Math.floor(timer * 100 / 10) * 10;
  return progress >= 80 ? 100 : progress;
};
const nextProgress: ComputedRef<number> = computed(() => getProgress(dwellTimer.value.nextPage.currentAccTime));
const prevProgress: ComputedRef<number> = computed(() => getProgress(dwellTimer.value.prevPage.currentAccTime));
const updateProgressColor = (page: dwellTimerData["nextPage"] | dwellTimerData["prevPage"], progressValue: number): void => {
  page.progressColor = (progressValue === 100) ? '#27bd01' : '#007bff';
};

const getAnnotations = async (pageProxy): Promise<any> => {
  return await pageProxy.getAnnotations({ intent: "display" });
};

const renderAnnotations = async (pdfPageProxy, annotationLayerContainer, viewport) => {
  annotationLayerContainer.replaceChildren();
  const annotations = await getAnnotations(pdfPageProxy);
  const clonedViewport = viewport.clone({ dontFlip: true });
  const annotationLayer = new pdfjsLib.AnnotationLayer({
    div: annotationLayerContainer,
    accessibilityManager: undefined,
    annotationCanvasMap: undefined,
    annotationEditorUIManager: undefined,
    page: pdfPageProxy,
    viewport: clonedViewport,
    /* new pdfjs-dist@4.10.38 */
    structTreeLayer: null
  });
  await annotationLayer.render({
    div: annotationLayerContainer,
    viewport: clonedViewport,
    page: pdfPageProxy,
    annotations,
    imageResourcesPath: undefined,
    renderForms: false,
    linkService: new SimpleLinkService(),
    downloadManager: null,
    annotationStorage: undefined,
    enableScripting: false,
    hasJSActions: undefined,
    fieldObjects: undefined
  });
  annotationLayerContainer.addEventListener("click", async (event) => {
    let annotationTarget = event.target.parentNode;
    if(!annotationTarget) {
      return;
    }
    const id = annotationTarget.dataset.annotationId;
    if(!id) {
      return;
    }
    const annotationLinkId = annotations.find((ele) => ele.id === id);
    if(!annotationLinkId) {
      return;
    }
    const pageIndex = await pdfProxy.getPageIndex(
      annotationLinkId.dest[0]
    );
    currentPage.value = pageIndex + 1;
  });
};

const renderText = (pdfPageProxy, textLayerContainer, viewport) => {
  const { scale } = viewport;
  pdfPageProxy
    .getTextContent()
    .then((content) => {
      const renderTask = new pdfjsLib.TextLayer({
        container: textLayerContainer,
        textContentSource: content,
        viewport: viewport.clone({ dontFlip: true })
      });
      return renderTask.render();
    })
    .then(() => {
    });
};

const renderCanvas = (pdfPageProxy, canvasLayer, viewport) => {
  const { width, height, rotation } = viewport;
  pdfWidth.value = width;
  pdfHeight.value = height;
  canvasLayer.width = width;
  canvasLayer.height = height;
  const context = canvasLayer.getContext("2d");
  const renderContext = {
    canvasContext: context,
    viewport: viewport
  };
  return pdfPageProxy.render(renderContext);
};

const processLoadingTask = (source: string): void => {
  const loadingTask = pdfjsLib.getDocument(source);
  loadingTask.promise
    .then(doc => {
      pdfProxy = doc;
      pdf = doc.loadingTask;
      totalPages.value = doc.numPages;
      return doc.getPage(currentPage.value);
    }, (error) => {
      // PDF loading error
      console.error(error);
    })
    .then(pageProxy => {
      pdfLayersWrapper.value.style.setProperty(
        "--scale-factor",
        `${1}`
      );
      const viewport = pageProxy.getViewport({ scale: 1 });
      renderText(pageProxy, textLayer.value, viewport);
      renderAnnotations(pageProxy, annotationLayer.value, viewport);
      return renderCanvas(pageProxy, canvasLayer.value, viewport);
    });
};

const canvas_factor = 2;
const paused = ref(false);
const pauseView = () => {
  paused.value = !paused.value;
};

const poseToCanvasCoord = (coord: number, factor: number) => {
  // Convert landmarks from pose models coord to views canvas coord
  return 1 - coord * factor;
};

const CanvasToPoseCoord = (coord: number, factor: number) => {
  // Convert landmarks from views canvas coord to models coord cord
  return (1 + coord) / factor;
};

const getCenter = (points: number[][]): { "x": number, "y": number, "z": number } => {
  const pointSum = points.reduce((acc, cur) => {
    acc["x_sum"] += cur[0];
    acc["y_sum"] += cur[1];
    acc["z_sum"] += cur[2];
    return acc;
  }, { "x_sum": 0, "y_sum": 0, "z_sum": 0 });
  return {
    x: pointSum["x_sum"] / points.length,
    y: pointSum["y_sum"] / points.length,
    z: pointSum["z_sum"] / points.length,
  };
};

const smoothing = (start: number, end: number, delta: number) => {
  const speed = Math.min(Math.max(end - start * 2, 7), 10);
  const alpha = 1 - Math.exp(-speed * delta);
  const threshold = 0.3;
  if(Math.abs(end - start) > threshold) {
    return end;
  } else {
    return start + (end - start) * alpha;
  }
};

const updateLandmarks = (groupRef, landmarks, delta, offsetPosition = { x: 0, y: 0, z: 0 }) => {
  groupRef.value.children.forEach((item) => {
    const landmark = landmarks[item.name].position;
    const newX = poseToCanvasCoord(offsetPosition.x + landmark[0], canvas_factor);
    const newY = poseToCanvasCoord(offsetPosition.y + landmark[1], canvas_factor);
    const newZ = poseToCanvasCoord(offsetPosition.z + landmark[2], canvas_factor);
    item.position.x = smoothing(item.position.x, newX, delta);
    item.position.y = smoothing(item.position.y, newY, delta);
    item.position.z = smoothing(item.position.z, newZ, delta);
    const displayConditions = [landmarks[item.name].exist, landmarks[item.name].display];
    item.visible = displayConditions.every(item => item === true);
  });
};

// Dwell activation methods
const pageTurnDwellCheck = (action: String, _dwellTimer, delta: number) => {
  const nose = poseLandmarksGroupRef.value.children.reduce((acc, cur) => {
    if(cur.name === "nose" && cur.visible) {
      acc = cur;
      return acc;
    }
    return acc;
  }, undefined);
  let hand = undefined;
  let pageTurnFunction = nextPage;
  if(action === "nextPage") {
    pageTurnFunction = nextPage;
    hand = rightHandLandmarksGroupRef;
  } else if(action === "prevPage") {
    pageTurnFunction = prevPage;
    hand = leftHandLandmarksGroupRef;
  }
  // Exit the function if no dwell check can be done
  if(hand.value.children[0].visible === false || hand === undefined || nose === undefined) {
    _dwellTimer.currentAccTime = 0;
    return;
  }

  const handLandmarkPositions = hand.value.children.reduce((positions, cur) => {
    positions.push([
      cur.position["x"],
      cur.position["y"],
      cur.position["z"],
    ]);
    return positions;
  }, []);
  const handLandmarkCenter = getCenter(handLandmarkPositions);
  const isInZone = handLandmarkCenter.y > nose.position.y;
  if(isInZone) {
    _dwellTimer.currentAccTime += delta;
  } else {
    _dwellTimer.currentAccTime = 0;
  }
  if(_dwellTimer.currentAccTime > _dwellTimer.triggerTime) {
    pageTurnFunction();
    _dwellTimer.currentAccTime = 0;
  }
};

const poseLandmarksGroupRef = shallowRef();
const leftHandLandmarksGroupRef = shallowRef();
const rightHandLandmarksGroupRef = shallowRef();

onLoop(({ delta, elapsed }) => {
  if(paused.value) return;
  if(!poseLandmarksGroupRef.value || !leftHandLandmarksGroupRef.value || !rightHandLandmarksGroupRef.value) return;

  updateLandmarks(poseLandmarksGroupRef, poseLandmarks, delta);

  const leftPalmOffset = getCenter([
    poseLandmarks["leftWrist"].position,
    poseLandmarks["leftPinky"].position,
    poseLandmarks["leftIndex"].position,
    poseLandmarks["leftThumb"].position,
  ]);
  updateLandmarks(leftHandLandmarksGroupRef, leftHandLandmarks, delta, leftPalmOffset);

  const rightPalmOffset = getCenter([
    poseLandmarks["rightWrist"].position,
    poseLandmarks["rightPinky"].position,
    poseLandmarks["rightIndex"].position,
    poseLandmarks["rightThumb"].position,
  ]);
  updateLandmarks(rightHandLandmarksGroupRef, rightHandLandmarks, delta, rightPalmOffset);
  // Check dwell activation
  pageTurnDwellCheck("nextPage", dwellTimer.value.nextPage, delta);
  pageTurnDwellCheck("prevPage", dwellTimer.value.prevPage, delta);
});

watch(currentPage, async (newValue) => {
  const pageProxy = await pdfProxy.getPage(newValue);
  const viewport = pageProxy.getViewport({ scale: 1 });
  renderText(pageProxy, textLayer.value, viewport);
  await renderAnnotations(pageProxy, annotationLayer.value, viewport);
  renderCanvas(pageProxy, canvasLayer.value, viewport);
});

watchEffect(() => {
  updateProgressColor(dwellTimer.value.nextPage, nextProgress.value);
  updateProgressColor(dwellTimer.value.prevPage, prevProgress.value);
});

onMounted(async () => {
  try {
    pdfjsLib.GlobalWorkerOptions.workerSrc = pdfWorkerLib as any;
  } catch (e) {
    window.pdfjsWorker = pdfWorkerLib;
  }
  processLoadingTask(pdfSrc);
});
</script>
<style scoped>
.overlay,
.overlay * {
  pointer-events: none;
}

canvas {
  pointer-events: none !important;
}
</style>

