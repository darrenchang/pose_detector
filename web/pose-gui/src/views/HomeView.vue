<template>
  <n-layout-content>
    <n-layout has-sider>
      <n-layout-sider
        class="n-layout-sider--left-placement"
        bordered
        collapse-mode="width"
        :width="240"
        :native-scrollbar="false"
        show-trigger
      >
        <n-menu :options="menuOptions" />
      </n-layout-sider>
      <n-layout-content>
        <PoseViewer />
      </n-layout-content>
      <n-layout-sider
        class="n-layout-sider--right-placement"
        bordered
        collapse-mode="width"
        :width="240"
        :native-scrollbar="false"
        show-trigger
      >
        <n-menu :options="menuOptions" />
      </n-layout-sider>
    </n-layout>
  </n-layout-content>
</template>

<script setup lang="ts">
import PoseViewer from '../components/PoseViewer.vue'
import type { Component } from 'vue'
import { NIcon } from 'naive-ui'
import { h } from 'vue'
import {
  NLayout,
  NLayoutSider,
  NLayoutContent,
  NMenu,
} from 'naive-ui'
import {
  BookOutline as BookIcon,
  PersonOutline as PersonIcon,
  WineOutline as WineIcon,
} from '@vicons/ionicons5'

function renderIcon(icon: Component) {
  return () => h(NIcon, null, { default: () => h(icon) })
}


const menuOptions = [
  {
    label: 'Hear the Wind Sing',
    key: 'hear-the-wind-sing',
    icon: renderIcon(BookIcon),
  },
  {
    label: 'Pinball 1973',
    key: 'pinball-1973',
    icon: renderIcon(BookIcon),
    disabled: true,
    children: [
      {
        label: 'Rat',
        key: 'rat',
      },
    ],
  },
  {
    label: 'A Wild Sheep Chase',
    key: 'a-wild-sheep-chase',
    disabled: true,
    icon: renderIcon(BookIcon),
  },
  {
    label: 'Dance Dance Dance',
    key: 'Dance Dance Dance',
    icon: renderIcon(BookIcon),
    children: [
      {
        type: 'group',
        label: 'People',
        key: 'people',
        children: [
          {
            label: 'Narrator',
            key: 'narrator',
            icon: renderIcon(PersonIcon),
          },
          {
            label: 'Sheep Man',
            key: 'sheep-man',
            icon: renderIcon(PersonIcon),
          },
        ],
      },
      {
        label: 'Beverage',
        key: 'beverage',
        icon: renderIcon(WineIcon),
        children: [
          {
            label: 'Whisky',
            key: 'whisky',
          },
        ],
      },
      {
        label: 'Food',
        key: 'food',
        children: [
          {
            label: 'Sandwich',
            key: 'sandwich',
          },
        ],
      },
      {
        label: 'The past increases. The future recedes.',
        key: 'the-past-increases-the-future-recedes',
      },
    ],
  },
]

</script>
