<template>
  <div class="w-full">
    <div class="badge">Annotation Layer</div>
    <div class="page-navigation">
      <button :disabled="currentPage <= 1" @click="--currentPage">&larr;</button>
      <span>{{ currentPage }}/{{ totalPages }}</span>
      <button :disabled="currentPage >= totalPages" @click="++currentPage">&rarr;</button>
    </div>
    <div
      ref="pdfLayersWrapper"
      class="pdf__layers pdfLayers border-none m-auto"
      :style="{
        width: `${pdfWidth}px`,
        height: `${pdfHeight}px`,
      }"
    >
      <div class="pdf__canvas-layer">
        <canvas ref="canvasLayer"/>
      </div>
      <div ref="textLayer" class="pdf__text-layer hidden"></div>
      <div ref="annotationLayer" class="pdf__annotation-layer"></div>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { Ref } from 'vue';
import { onMounted, ref, watch } from 'vue';
import { pdfjsLib, SimpleLinkService, pdfWorkerLib } from '@/composables/pdfjsLib';

const pdfLayersWrapper: Ref<any> = ref(null);
const canvasLayer: Ref<any> = ref(null);
const textLayer: Ref<any> = ref(null);
const annotationLayer: Ref<any> = ref(null);
const pdfSrc: string = 'https://pdfobject.com/pdf/pdf_open_parameters_acro8.pdf';
let pdfProxy = undefined;
let pdf = undefined;

const currentPage: Ref<number> = ref(1);
const totalPages: Ref<number> = ref(3);
const pdfWidth: Ref<number> = ref(0);
const pdfHeight: Ref<number> = ref(0);

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
  console.log(width, height);
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
    console.log(pdfWorkerLib);
    pdfjsLib.GlobalWorkerOptions.workerSrc = pdfWorkerLib as any;
  } catch (e) {
    window.pdfjsWorker = pdfWorkerLib;
  }
  processLoadingTask(pdfSrc);
});
</script>
