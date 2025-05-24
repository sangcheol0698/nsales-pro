<template>
  <AuthLayout logoHref="/auths/login">
    <LoginForm />
  </AuthLayout>
</template>

<script setup lang="ts">
import LoginForm from '@/features/auth/components/LoginForm.vue';
import AuthLayout from '@/core/layouts/AuthLayout.vue';
</script>

<style scoped></style>