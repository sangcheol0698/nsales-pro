<template>
  <Toaster />

  <div class="min-h-screen w-full">
    <RouterView />
  </div>
</template>

<script setup lang="ts">
import { RouterView } from 'vue-router';
import { Toaster } from '@/components/ui/sonner';
</script>

<style scoped></style>
