import { createApp } from 'vue';
import { createPinia } from 'pinia';
import '@/index.css';
// Shiki는 CSS 파일이 필요 없음 (인라인 스타일 사용)
import App from './App.vue';
import router from './core/router';
import 'reflect-metadata';

const app = createApp(App);

app.use(createPinia());
app.use(router);

app.mount('#app');
