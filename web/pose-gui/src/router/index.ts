import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'pose',
      component: () => import('@/views/PoseView.vue'),
    },
    {
      path: '/pdf',
      name: 'pdf',
      component: () => import('@/views/PdfView.vue') ,
    },
    {
      path: '/swaggerui',
      name: 'swaggerui',
      component: () => import('@/views/Swaggerui.vue') ,
    },
  ],
})

export default router
