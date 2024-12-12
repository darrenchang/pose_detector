<script setup lang="ts">
import { NLayoutContent } from 'naive-ui'
import { TresCanvas } from '@tresjs/core'
import SubComponent from './SubComponent.vue'
import { state } from "@/socket";
import { connect, disconnect, sub } from '../composables/socketManager';
import { computed } from 'vue'


const connected = computed(() => state.connected);

</script>

<template>
  <n-layout-content>
    <p @click="connect()">connect</p>
    <p @click="disconnect()">disconnect</p>
    <p @click="sub()">sub</p>
    <p>State: {{ connected }}</p>
    <TresCanvas clear-color="#82DBC5">
      <TresPerspectiveCamera
        :position="[3, 3, 3]"
        :fov="45"
        :look-at="[0, 0, 0]"/>
      <TresMesh ref="boxRef">
        <TresTorusGeometry :args="[1, 0.5, 16, 32]" />
        <TresMeshBasicMaterial color="orange" />
      </TresMesh>
      <TresAmbientLight :intensity="1" />
      <SubComponent />
    </TresCanvas>
  </n-layout-content>
</template>
