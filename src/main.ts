import { createApp } from 'vue';
import { createPinia } from 'pinia';
import '@/index.css';
import App from './App.vue';
import router from './core/router';
import 'reflect-metadata';

const app = createApp(App);

app.use(createPinia());
app.use(router);

app.mount('#app');
