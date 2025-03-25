<script setup lang="ts">
import { NLayoutContent } from 'naive-ui'
import { onMounted } from 'vue'
import { pdfjsLib } from '@/composables/pdfjsLib'

const pdfSrc = 'https://pdfobject.com/pdf/pdf_open_parameters_acro8.pdf'

function processLoadingTask(source: string) {
  console.log('processLoadingTask')
  const loadingTask = pdfjsLib.getDocument(source)
  loadingTask.promise
    .then(docProxy => {
      console.log(docProxy)
    })
    .then(page => {
      const renderContext = {
        // canvasContext: context,
        // viewport: viewport,
      }
      console.log("loaded")
      console.log(page)
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
    <div>hello</div>
  </n-layout-content>
</template>

<style scoped></style>
