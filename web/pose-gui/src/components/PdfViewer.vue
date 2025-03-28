<template>
  <div class="grid grid-cols-1">
    <div ref="pdfLayersWrapper" class="border-none m-auto" :style="{ width: `${pdfWidth}px`, height: `${pdfHeight}px` }">
      <div class="badge">Annotation Layer</div>
      <div class="page-navigation">
        <button :disabled="currentPage <= 1" @click="prevPage">&larr;</button>
        <span>{{ currentPage }}/{{ totalPages }}</span>
        <button :disabled="currentPage >= totalPages" @click="nextPage">&rarr;</button>
      </div>
      <div class="pdf__canvas-layer"><canvas ref="canvasLayer" /></div>
      <div ref="textLayer" class="pdf__text-layer hidden"></div>
      <div ref="annotationLayer" class="pdf__annotation-layer"></div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue';
import type { Ref } from 'vue';
import { pdfjsLib, SimpleLinkService, pdfWorkerLib } from '@/composables/pdfjsLib';
import { poseLandmarks } from '@/interface/poseLandmarksInterface';
import { useRenderLoop } from '@tresjs/core';

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
  if (currentPage.value < totalPages.value) {
    currentPage.value++;
  }
};
const prevPage = () => {
  if (currentPage.value > 1) {
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
    this.currentPage = pageIndex + 1;
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
      console.log("pdfProxy", pdfProxy);
      console.log("pdf", pdf);
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

const debounceTime = 1000;
const lastGestureTime:Ref<number> = ref(0);
onLoop(() => {
  if (
    !poseLandmarks["rightWrist"] ||
    !poseLandmarks["leftWrist"] ||
    !poseLandmarks["rightShoulder"] ||
    !poseLandmarks["leftShoulder"]
  ) return;

  const rightWristY = poseLandmarks["rightWrist"].position[1];
  const leftWristY = poseLandmarks["leftWrist"].position[1];
  const shoulderY = (poseLandmarks["rightShoulder"].position[1] + poseLandmarks["leftShoulder"].position[1]) / 2;
  const now = Date.now();

  const isBothHandsRaised = rightWristY < shoulderY && leftWristY < shoulderY;
  if (isBothHandsRaised) {
    return;
  }

  if (rightWristY < shoulderY && now - lastGestureTime.value > debounceTime && currentPage.value < totalPages.value) {
    nextPage();
    lastGestureTime.value = now;
  }

  if (leftWristY < shoulderY && now - lastGestureTime.value > debounceTime && currentPage.value > 1) {
    prevPage();
    lastGestureTime.value = now;
  }
});
</script>

<style scoped lang="scss">
.page-navigation {
  margin: 15px;
  display: flex;
  justify-content: center;
  align-items: center;
}
.page-navigation button {
  margin: 0 10px;
  padding: 5px 10px;
  font-size: 18px;
  cursor: pointer;
}
</style>
