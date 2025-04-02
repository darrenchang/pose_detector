<template>
  <n-layout>
    <div>
      <n-tabs type="line" @update:value="handleUpdate" default-value="" v-model:value="currentRouteName" size="large">
        <n-tab name="pose" tab="Pose"></n-tab>
        <n-tab name="pdf" tab="PDF"></n-tab>
        <n-tab name="swaggerui" tab="SwaggerUI"></n-tab>
      </n-tabs>
    </div>
    <router-view v-slot="{ Component }">
      <transition>
        <component :is="Component"/>
      </transition>
    </router-view>
  </n-layout>
</template>

<script setup lang="ts">
import { RouterView } from 'vue-router';
import { NLayout, NTabs, NTab } from 'naive-ui';
import { ref, watch } from 'vue';
import { useRoute, useRouter } from 'vue-router';

const route = useRoute();
const router = useRouter();
let currentRouteName = ref('');

function handleUpdate(key: string) {
  currentRouteName.value = key;
  router.push({ name: currentRouteName.value });
}

watch(
  () => route.name,
  newName => {
    if(newName) {
      currentRouteName.value = newName.toString();
    }
  },
);
</script>

<style lang="scss">
.n-layout-sider {
  background: rgba(128, 128, 128, 0.3);
}

.n-layout-content {
  height: calc(100vh - var(--header-height));
}
</style>
