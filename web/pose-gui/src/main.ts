import './assets/main.css';
import { createApp } from 'vue';
import { createPinia } from 'pinia';
import VueDragscroll from "vue-dragscroll";
import App from './App.vue';
import router from './router';

const app = createApp(App);

app.use(createPinia());
app.use(VueDragscroll);
app.use(router);
app.mount('#app');
