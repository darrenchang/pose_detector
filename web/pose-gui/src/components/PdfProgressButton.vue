<template>
  <n-button class="pointer-events-auto! rounded-none" @click="btnEvent" secondary>
    <slot name="icon"/>
    <div class="btn-progress overlay absolute w-full h-full left-[0] right-[0]">
      <n-progress border-radius="0 0 0 0" class="h-full" type="line" :percentage="nProgressPercentage"
                  :color="nProgressColor"
                  :show-indicator="false"/>
    </div>
  </n-button>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import { NProgress, NButton } from 'naive-ui';

const props = defineProps<{
  btnEvent: (index: number) => void;
  progressPercentage: number;
  progressColor: string;
}>();

const nProgressPercentage = computed(() => props.progressPercentage);
const nProgressColor = computed(() => props.progressColor);
</script>
