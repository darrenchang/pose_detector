<script setup lang="ts">
import { NLayoutContent } from 'naive-ui'
import { onMounted } from 'vue'
import { ref } from 'vue'
import { pdfjsLib } from '@/composables/pdfjsLib'

const pdfSrc = 'https://pdfobject.com/pdf/pdf_open_parameters_acro8.pdf'
let numPages = ref(0)
let currentPage = ref(1)
let pdfProxy = undefined
let pdf = undefined

function processLoadingTask(source: string) {
  const loadingTask = pdfjsLib.getDocument(source)
  loadingTask.promise
    .then(doc => {
      pdfProxy = doc
      pdf = doc.loadingTask
      numPages.value = doc.numPages
      console.log("pdfProxy", pdfProxy)
      console.log("pdf", pdf)
      return doc.getPage(currentPage.value)
    })
    .then(page => {
      const renderContext = {
        // canvasContext: context,
        // viewport: viewport,
      }
      console.log('page', page)
      console.log('renderContext', renderContext)
      // return page.render(renderContext)
    })
}

onMounted(async () => {
  console.log(pdfSrc)
  console.log(pdfjsLib)
  processLoadingTask(pdfSrc)
})
</script>

<template>
  <n-layout-content>
    <div>Pages: {{numPages}}, Current Page: {{currentPage}}</div>
    <div
      ref="pdfLayersWrapper"
      class="pdf__layers pdfLayers"
      style="height: 300px;"
    >
      <div class="pdf__canvas-layer">
        <canvas ref="canvasLayer" />
      </div>
      <div ref="textLayer" class="pdf__text-layer"></div>
      <div ref="annotationLayer" class="pdf__annotation-layer"></div>
    </div>
  </n-layout-content>
</template>

<style scoped>
.pdfLayers {
  background-color: red;
  border: 0;
  margin: 0;
}
</style>
