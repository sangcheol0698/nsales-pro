<template>
  <SidebarLayout>
    <router-view />
  </SidebarLayout>
</template>

<script setup lang="ts">
import { SidebarLayout } from '@/shared/components/sidebar';
// This component serves as a parent container for the my-page routes
// It wraps the child routes with the SidebarLayout
</script>
