<template>
  <n-config-provider :theme="lightTheme" :theme-overrides="defaultTheme" inline-theme-disabled>
    <n-layout>
      <div>
        <n-tabs type="line" @update:value="handleUpdate" default-value="" v-model:value="currentRouteName" size="large">
          <n-tab name="pose" tab="Pose"></n-tab>
          <n-tab name="runnergame" tab="Runner Game"></n-tab>
          <n-tab name="imageinference" tab="Image Inference"></n-tab>
          <n-tab name="pdf" tab="PDF"></n-tab>
          <n-tab name="swaggerui" tab="SwaggerUI"></n-tab>
        </n-tabs>
      </div>
      <div class="page-slider">
        <router-view v-slot="{ Component }">
          <transition :name="`slide-${slideDirection}`">
            <component :is="Component" :key="route.name"/>
          </transition>
        </router-view>
      </div>
    </n-layout>
  </n-config-provider>
</template>

<script setup lang="ts">
import { RouterView } from 'vue-router';
import { lightTheme, NConfigProvider, NLayout, NTabs, NTab } from 'naive-ui';
import { ref, watch } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { defaultTheme } from '@/assets/themes/default';

const route = useRoute();
const router = useRouter();
let currentRouteName = ref('');

const TAB_ORDER = ['pose', 'runnergame', 'imageinference', 'pdf', 'swaggerui'];
const slideDirection = ref<'left' | 'right'>('left');

function handleUpdate(key: string) {
  currentRouteName.value = key;
  router.push({ name: currentRouteName.value });
}

watch(
  () => route.name,
  (newName, oldName) => {
    if(newName) {
      const from = TAB_ORDER.indexOf(String(oldName ?? ''));
      const to = TAB_ORDER.indexOf(String(newName));
      if (from >= 0 && to >= 0) {
        slideDirection.value = to > from ? 'left' : 'right';
      }
      currentRouteName.value = newName.toString();
    }
  },
);
</script>

<style lang="scss">
// --- Page slide -------------------------------------------------------------
$page-slide-duration: 0.3s;
$page-slide-easing: ease;

.page-slider {
  position: relative;
  // Clip the pages while they are translated off to the side, otherwise the
  // document grows and shows a horizontal scrollbar for the duration.
  overflow: hidden;
}

.slide-left-enter-active,
.slide-left-leave-active,
.slide-right-enter-active,
.slide-right-leave-active {
  transition: transform $page-slide-duration $page-slide-easing;
}

// The leaving page overlaps the entering one instead of pushing it down.
.slide-left-leave-active,
.slide-right-leave-active {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
}

// slide-left: new page comes in from the right, old one exits to the left
.slide-left-enter-from { transform: translateX(100%); }
.slide-left-leave-to { transform: translateX(-100%); }

// slide-right: the reverse
.slide-right-enter-from { transform: translateX(-100%); }
.slide-right-leave-to { transform: translateX(100%); }

.n-layout-sider {
  background: rgba(128, 128, 128, 0.3);
}

.n-layout-content {
  height: calc(100vh - var(--header-height));
}
</style>
