<template>
  <SidebarProvider>
    <RouterView />
  </SidebarProvider>
</template>

<script setup lang="ts">
import { RouterView } from 'vue-router';
import { SidebarProvider } from '@/core/components/ui/sidebar';
</script>

<style></style>
