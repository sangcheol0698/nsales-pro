<template>
  <AuthLayout logoHref="/" :showTerms="false">
    <SetPasswordForm />
  </AuthLayout>
</template>

<script setup lang="ts">
import SetPasswordForm from '@/components/auth/SetPasswordForm.vue';
import AuthLayout from '@/layouts/AuthLayout.vue';
</script>

<style scoped></style>
