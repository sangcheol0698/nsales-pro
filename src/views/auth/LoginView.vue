<template>
  <AuthLayout logoHref="/auths/login">
    <LoginForm />
  </AuthLayout>
</template>

<script setup lang="ts">
import LoginForm from '@/components/auth/LoginForm.vue';
import AuthLayout from '@/layouts/AuthLayout.vue';
</script>

<style scoped></style>
