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

<style>
/* Global transition effects for theme switching */
:root {
  transition:
    background-color 0.3s ease,
    color 0.3s ease,
    border-color 0.3s ease;
}

/* Apply transitions to common elements */
*,
*::before,
*::after {
  transition:
    background-color 0.3s ease,
    color 0.3s ease,
    border-color 0.3s ease,
    box-shadow 0.3s ease,
    opacity 0.3s ease;
}

/* Exclude transitions from certain elements where it might cause issues */
button:active,
.no-transition,
.no-transition * {
  transition: none !important;
}
</style>
