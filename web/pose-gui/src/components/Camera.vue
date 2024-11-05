<template>
  <div>
    <video ref="video" autoplay playsinline webkit-playsinline muted hidden></video>
    <canvas ref="canvas" width="800" height="640"></canvas>
    <div>button</div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';

const canvas = ref(null);
const video = ref(null);
const ctx = ref(null);

const constraints = ref({
  audio: false,
  video: true,
});

onMounted(async () => {
  if (video.value) {
    ctx.value = canvas.value.getContext("2d");
    await navigator.mediaDevices
      .getUserMedia(constraints.value)
      .then(SetStream)
      .catch(e => {
        console.error(e);
      })
  }
})

function SetStream(stream) {
  video.value.srcObject = stream;
  video.value.play();

  requestAnimationFrame(Draw);
}

function Draw() {
  ctx.value.drawImage(video.value, 0, 0, canvas.value.width, canvas.value.height);
  requestAnimationFrame(Draw);
}

</script>
