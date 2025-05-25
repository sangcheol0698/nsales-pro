<template>
  <Toaster />

  <div class="min-h-screen w-full">
    <RouterView />
  </div>
</template>

<script setup lang="ts">
import { RouterView } from 'vue-router';
import { Toaster } from '@/core/components/ui/sonner';
import { useAlertDialog, useTheme } from '@/core/composables';

useTheme();
useAlertDialog();
</script>

<style></style>
