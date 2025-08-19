<template>
  <SidebarProvider>
    <Toaster />
    <RouterView />
  </SidebarProvider>
</template>

<script setup lang="ts">
import { RouterView } from 'vue-router';
import { Toaster } from '@/components/ui/sonner';
import { SidebarProvider } from '@/components/ui/sidebar';
import { useAlertDialog, useFont, useTheme } from '@/core/composables';

useTheme();
useFont();
useAlertDialog();
</script>

<style></style>
