<template>
  <Toaster />
  <div>
    <RouterView />
  </div>
</template>

<script setup lang="ts">
import { RouterView } from 'vue-router';
import { Toaster } from '@/core/components/ui/sonner';
import { useAlertDialog, useFont, useTheme } from '@/core/composables';

useTheme();
useFont();
useAlertDialog();
</script>

<style></style>
