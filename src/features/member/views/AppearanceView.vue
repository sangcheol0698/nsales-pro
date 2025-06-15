<template>
  <MyPageLayout :loading="loading">
    <div class="space-y-6">
      <div class="space-y-2">
        <h3 class="text-lg font-medium">화면 설정</h3>
        <p class="text-sm text-muted-foreground">
          앱의 테마 및 폰트 설정을 관리합니다.
        </p>
      </div>

      <div class="space-y-6">
        <AppearanceForm />
      </div>
    </div>
  </MyPageLayout>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import AppearanceForm from '@/features/member/components/AppearanceForm.vue';
import MyPageLayout from '@/features/member/layouts/MyPageLayout.vue';

const loading = ref(false);
</script>

<style scoped></style>
