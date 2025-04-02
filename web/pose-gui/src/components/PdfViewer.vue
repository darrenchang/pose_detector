<template>
  <n-layout-content>
    <div class="overlay absolute w-full h-full z-256">
      <TresCanvas>
        <TresPerspectiveCamera :position="[0, 0, 6]" :fov="45" :look-at="[0, 0, 0]" />
        <TresGroup ref="poseLandmarksGroupRef" :position="[0, 0, 0]">
          <TresMesh v-for="(landmark, key) in poseLandmarks" :name="key" :visible="true" :key="key" :position="[-1, -1, -1]">
            <TresBoxGeometry :args="landmark.cubeSize" />
            <TresMeshNormalMaterial :color="landmark.cubeColor" />
          </TresMesh>
        </TresGroup>
        <TresGroup ref="leftHandLandmarksGroupRef" :position="[0, 0, 0]">
          <TresMesh v-for="(landmark, key) in leftHandLandmarks" :name="key" :key="key" :position="[-1, -1, -1]">
            <TresBoxGeometry :args="landmark.cubeSize" />
            <TresMeshNormalMaterial :color="landmark.cubeColor" />
          </TresMesh>
        </TresGroup>
        <TresGroup ref="rightHandLandmarksGroupRef" :position="[0, 0, 0]">
          <TresMesh v-for="(landmark, key) in rightHandLandmarks" :name="key" :key="key" :position="[-1, -1, -1]">
            <TresBoxGeometry :args="landmark.cubeSize" />
            <TresMeshNormalMaterial :color="landmark.cubeColor" />
          </TresMesh>
        </TresGroup>
        <TresAmbientLight :intensity="1" />
      </TresCanvas>
    </div>
    <n-layout-content>
      <div class="flex flex-col w-full h-full">
        <div class="top-0 left-0 w-full h-full">
          <div class="grid grid-cols-1 w-full h-full">
            <!-- <button class="bg-gray-800 text-white px-4 py-2 rounded-md mx-2" -->
            <!--         :disabled="currentPage <= 1" @click="prevPage">&larr;</button> -->
            <!-- <button class="bg-gray-800 text-white px-4 py-2 rounded-md mx-2" -->
            <!--         :disabled="currentPage >= totalPages" @click="nextPage">&rarr;</button> -->
            <div ref="pdfLayersWrapper" class="border-none m-auto"
                 :style="{ width: `${pdfWidth}px`, height: `${pdfHeight}px` }">
              <div class="pdf__canvas-layer">
                <canvas ref="canvasLayer" />
              </div>
              <div ref="textLayer" class="pdf__text-layer hidden"></div>
              <div ref="annotationLayer" class="pdf__annotation-layer"></div>
            </div>
          </div>
        </div>
      </div>
    </n-layout-content>
  </n-layout-content>
</template>

<style scoped>
.overlay,
.overlay * {
  pointer-events: none;
}
canvas {
  pointer-events: none !important;
}
</style>

<script setup lang="ts">
import { NLayoutContent } from 'naive-ui'
import type { Ref } from 'vue';
import { onMounted, ref, shallowRef, watch } from 'vue';
import { pdfjsLib, pdfWorkerLib, SimpleLinkService } from '@/composables/pdfjsLib';
import { poseLandmarks } from '@/interface/poseLandmarksInterface';
import { leftHandLandmarks, rightHandLandmarks } from '@/interface/handLandmarksInterface';
import { TresCanvas, useRenderLoop } from '@tresjs/core';
import { getInfo } from '@/composables/restApiService';

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
}

const poseToCanvasCoord = (coord: number, factor: number) => {
  // Convert landmarks from pose models coord to views canvas coord
  return 1 - coord * factor;
}

const CanvasToPoseCoord = (coord: number, factor: number) => {
  // Convert landmarks from views canvas coord to models coord cord
  return (1 + coord) / factor;
}

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
}

const smoothing = (start: number, end: number, delta: number) =>  {
  const speed = Math.min(Math.max(end - start * 2, 7), 10);
  const alpha = 1 - Math.exp(-speed * delta);
  const threshold = 0.3;
  if(Math.abs(end - start) > threshold) {
    return end;
  } else {
    return start + (end - start) * alpha;
  }
}

const poseLandmarksGroupRef = shallowRef();
const leftHandLandmarksGroupRef = shallowRef();
const rightHandLandmarksGroupRef = shallowRef();

onLoop(({ delta, elapsed }) => {
  if (paused.value) return;
  if (!poseLandmarksGroupRef.value || !leftHandLandmarksGroupRef.value || !rightHandLandmarksGroupRef.value) return;

  const updateLandmarks = (groupRef, landmarks, offsetPosition = { x: 0, y: 0, z: 0 }) => {
    groupRef.value.children.forEach((item) => {
      const landmark = landmarks[item.name].position;
      const newX = poseToCanvasCoord(offsetPosition.x + landmark[0], canvas_factor);
      const newY = poseToCanvasCoord(offsetPosition.y + landmark[1], canvas_factor);
      const newZ = poseToCanvasCoord(offsetPosition.z + landmark[2], canvas_factor);
      item.position.x = smoothing(item.position.x, newX, delta);
      item.position.y = smoothing(item.position.y, newY, delta);
      item.position.z = smoothing(item.position.z, newZ, delta);
      const displayConditions = [landmarks[item.name].exist, landmarks[item.name].display]
      item.visible = displayConditions.every(item => item === true)
    });
  };
  updateLandmarks(poseLandmarksGroupRef, poseLandmarks);

  const leftPalm = getCenter([
    poseLandmarks["leftWrist"].position,
    poseLandmarks["leftPinky"].position,
    poseLandmarks["leftIndex"].position,
    poseLandmarks["leftThumb"].position,
  ]);
  updateLandmarks(leftHandLandmarksGroupRef, leftHandLandmarks, leftPalm);

  const rightPalm = getCenter([
    poseLandmarks["rightWrist"].position,
    poseLandmarks["rightPinky"].position,
    poseLandmarks["rightIndex"].position,
    poseLandmarks["rightThumb"].position,
  ]);
  updateLandmarks(rightHandLandmarksGroupRef, rightHandLandmarks, rightPalm);
});

watch(currentPage, async (newValue) => {
  const pageProxy = await pdfProxy.getPage(newValue);
  const viewport = pageProxy.getViewport({ scale: 1 });
  renderText(pageProxy, textLayer.value, viewport);
  await renderAnnotations(pageProxy, annotationLayer.value, viewport);
  renderCanvas(pageProxy, canvasLayer.value, viewport);
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
