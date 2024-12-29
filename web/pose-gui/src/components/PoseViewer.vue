<script setup lang="ts">
import { NLayoutContent } from 'naive-ui'
import { TresCanvas, useRenderLoop } from '@tresjs/core'
import { socket } from '@/socket'
import { shallowRef } from 'vue'

const { onLoop } = useRenderLoop()

interface poseLandmarksInterface {
  [key: string]: {
    cubeSize: number[]
    cubeColor: string
    position: number[]
  }
}
const factor = 2
let poseLandmarks: poseLandmarksInterface = {
  // head
  nose: {
    cubeColor: 'orage',
    cubeSize: [0.05, 0.05, 0.05],
    position: [0, 0, 0],
  },
  leftEyeInner: {
    cubeColor: 'orage',
    cubeSize: [0.02, 0.02, 0.02],
    position: [0, 0, 0],
  },
  leftEye: {
    cubeColor: 'orage',
    cubeSize: [0.02, 0.02, 0.02],
    position: [0, 0, 0],
  },
  leftEyeOuter: {
    cubeColor: 'orage',
    cubeSize: [0.02, 0.02, 0.02],
    position: [0, 0, 0],
  },
  rightEyeInner: {
    cubeColor: 'orage',
    cubeSize: [0.02, 0.02, 0.02],
    position: [0, 0, 0],
  },
  rightEye: {
    cubeColor: 'orage',
    cubeSize: [0.02, 0.02, 0.02],
    position: [0, 0, 0],
  },
  rightEyeOuter: {
    cubeColor: 'orage',
    cubeSize: [0.02, 0.02, 0.02],
    position: [0, 0, 0],
  },
  leftEar: {
    cubeColor: 'orage',
    cubeSize: [0.05, 0.05, 0.05],
    position: [0, 0, 0],
  },
  rightEar: {
    cubeColor: 'orage',
    cubeSize: [0.05, 0.05, 0.05],
    position: [0, 0, 0],
  },
  mouthLeft: {
    cubeColor: 'orage',
    cubeSize: [0.05, 0.05, 0.05],
    position: [0, 0, 0],
  },
  mouthRight: {
    cubeColor: 'orage',
    cubeSize: [0.05, 0.05, 0.05],
    position: [0, 0, 0],
  },
  // body
  leftShoulder: {
    cubeColor: 'orage',
    cubeSize: [0.1, 0.1, 0.1],
    position: [0, 0, 0],
  },
  rightShoulder: {
    cubeColor: 'orage',
    cubeSize: [0.1, 0.1, 0.1],
    position: [0, 0, 0],
  },
  leftElbow: {
    cubeColor: 'orage',
    cubeSize: [0.1, 0.1, 0.1],
    position: [0, 0, 0],
  },
  rightElbow: {
    cubeColor: 'orage',
    cubeSize: [0.1, 0.1, 0.1],
    position: [0, 0, 0],
  },
  leftWrist: {
    cubeColor: 'orage',
    cubeSize: [0.1, 0.1, 0.1],
    position: [0, 0, 0],
  },
  rightWrist: {
    cubeColor: 'orage',
    cubeSize: [0.1, 0.1, 0.1],
    position: [0, 0, 0],
  },
  leftPinky: {
    cubeColor: 'orage',
    cubeSize: [0.1, 0.1, 0.1],
    position: [0, 0, 0],
  },
  rightPinky: {
    cubeColor: 'orage',
    cubeSize: [0.1, 0.1, 0.1],
    position: [0, 0, 0],
  },
  leftIndex: {
    cubeColor: 'orage',
    cubeSize: [0.1, 0.1, 0.1],
    position: [0, 0, 0],
  },
  rightIndex: {
    cubeColor: 'orage',
    cubeSize: [0.1, 0.1, 0.1],
    position: [0, 0, 0],
  },
  leftThumb: {
    cubeColor: 'orage',
    cubeSize: [0.1, 0.1, 0.1],
    position: [0, 0, 0],
  },
  rightThumb: {
    cubeColor: 'orage',
    cubeSize: [0.1, 0.1, 0.1],
    position: [0, 0, 0],
  },
  leftHip: {
    cubeColor: 'orage',
    cubeSize: [0.1, 0.1, 0.1],
    position: [0, 0, 0],
  },
  rightHip: {
    cubeColor: 'orage',
    cubeSize: [0.1, 0.1, 0.1],
    position: [0, 0, 0],
  },
  leftKnee: {
    cubeColor: 'orage',
    cubeSize: [0.1, 0.1, 0.1],
    position: [0, 0, 0],
  },
  rightKnee: {
    cubeColor: 'orage',
    cubeSize: [0.1, 0.1, 0.1],
    position: [0, 0, 0],
  },
  leftAnkle: {
    cubeColor: 'orage',
    cubeSize: [0.1, 0.1, 0.1],
    position: [0, 0, 0],
  },
  rightAnkle: {
    cubeColor: 'orage',
    cubeSize: [0.1, 0.1, 0.1],
    position: [0, 0, 0],
  },
  leftHeel: {
    cubeColor: 'orage',
    cubeSize: [0.1, 0.1, 0.1],
    position: [0, 0, 0],
  },
  rightHeel: {
    cubeColor: 'orage',
    cubeSize: [0.1, 0.1, 0.1],
    position: [0, 0, 0],
  },
  leftFootIndex: {
    cubeColor: 'orage',
    cubeSize: [0.1, 0.1, 0.1],
    position: [0, 0, 0],
  },
  rightFootIndex: {
    cubeColor: 'orage',
    cubeSize: [0.1, 0.1, 0.1],
    position: [0, 0, 0],
  },
}

socket.on('pose_landmarks', message => {
  if (message.length <= 0) {
    return
  }
  Object.keys(poseLandmarks).forEach((key, index) => {
    const position = [
      message[index]['x'] * factor,
      message[index]['y'] * factor,
      message[index]['z'] * factor,
    ]
    poseLandmarks[key].position = position
  })
})

function lerp(start: number, end: number, delta: number) {
  const smoothingFactor = 10
  const threshold = 0.3
  if (Math.abs(end - start) > threshold) {
    return end
  } else {
    return start + (end - start) * delta * smoothingFactor
  }
}

const landmarksGroupRef = shallowRef()
onLoop(({ delta, elapsed }) => {
  if (!landmarksGroupRef.value) {
    return
  }
  const landmarks: any[] = landmarksGroupRef.value.children
  landmarks.forEach((item, _) => {
    const newX = 1 - poseLandmarks[item.name].position[0]
    item.position.x = lerp(item.position.x, newX, delta)
    const newY = 1 - poseLandmarks[item.name].position[1]
    item.position.y = lerp(item.position.y, newY, delta)
    const newZ = 1 - poseLandmarks[item.name].position[2]
    item.position.z = lerp(item.position.z, newZ, delta)
  })
})
</script>

<template>
  <n-layout-content>
    <TresCanvas clear-color="#82DBC5">
      <TresPerspectiveCamera :position="[0, 0, 6]" :fov="45" :look-at="[0, 0, 0]" />
      <TresGroup ref="landmarksGroupRef" :position="[0, 0, 0]">
        <TresMesh v-for="(landmark, key) in poseLandmarks" :name="key" :key="key" :position="[-1, -1, -1]">
          <TresBoxGeometry :args="landmark.cubeSize" />
          <TresMeshNormalMaterial :color="landmark.cubeColor" />
        </TresMesh>
      </TresGroup>
      <TresAmbientLight :intensity="1" />
    </TresCanvas>
  </n-layout-content>
</template>
