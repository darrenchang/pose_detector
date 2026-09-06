<script setup lang="ts">
import { TresCanvas } from '@tresjs/core'
import SkeletonScene from '@/components/SkeletonScene.vue'
</script>

<template>
  <!--
    render-mode="on-demand": the scene is only drawn on frames that call
    invalidate(). SkeletonScene invalidates while the figure is animating
    toward new landmarks and stops once it settles, so a still or absent
    subject uses no GPU frames.
  -->
  <TresCanvas render-mode="on-demand" clear-color="#101826">
    <SkeletonScene />
  </TresCanvas>
</template>
