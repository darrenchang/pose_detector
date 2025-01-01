<script>
import { defineComponent } from 'vue'
import '@/assets/swagger-ui/swagger-ui.css'
import SwaggerUI from '@/assets/swagger-ui/swagger-ui-es-bundle.js'
import SwaggerUIStandalonePreset from '@/assets/swagger-ui/swagger-ui-standalone-preset.js'
import { getBaseApiUrl } from '@/composables/apiUrl'

export default defineComponent({
  mounted() {
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
  },
})
</script>

<template>
  <div id="swagger-ui"></div>
</template>
