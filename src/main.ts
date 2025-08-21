import 'reflect-metadata';
import { createApp } from 'vue';
import { createPinia } from 'pinia';
import '@/index.css';
// Shiki는 CSS 파일이 필요 없음 (인라인 스타일 사용)
import App from './App.vue';
import router from './core/router';
import { useTheme } from '@/core/composables';

// 개발환경 인증 유틸리티
import '@/core/utils/auth-dev';
// 개발환경 사용자 설정 유틸리티
import '@/core/utils/dev-user-setup';

const app = createApp(App);

app.use(createPinia());
app.use(router);

// 테마 초기화
const { initializeTheme } = useTheme();
initializeTheme();

app.mount('#app');
