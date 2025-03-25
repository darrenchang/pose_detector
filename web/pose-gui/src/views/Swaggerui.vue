<script setup lang="ts">
import { onMounted } from 'vue'
import '@/assets/swagger-ui/swagger-ui.css'
// @ts-ignore
import SwaggerUI from '@/assets/swagger-ui/swagger-ui-es-bundle.js'
// @ts-ignore
import SwaggerUIStandalonePreset from '@/assets/swagger-ui/swagger-ui-standalone-preset.js'
import { getBaseApiUrl } from '@/composables/apiUrl'
import { NLayoutContent } from 'naive-ui'

onMounted(async () => {
  const swaggerJson = `${getBaseApiUrl()}/swagger.json`
  SwaggerUI({
    url: swaggerJson,
    dom_id: '#swagger-ui',
    presets: [SwaggerUI.presets.apis, SwaggerUIStandalonePreset],
    deepLinking: true,
    validatorUrl: 'none',
    defaultModelsExpandDepth: -1,
    persistAuthorization: true,
    displayRequestDuration: true,
    tryItOutEnabled: true,
  })
})
</script>

<template>
  <n-layout-content>
    <div id="swagger-ui"></div>
  </n-layout-content>
</template>
