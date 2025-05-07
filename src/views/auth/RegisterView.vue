<template>
  <AuthLayout logoHref="/auths/register">
    <RegisterForm />
  </AuthLayout>
</template>

<script setup lang="ts">
import RegisterForm from '@/components/auth/RegisterForm.vue';
import AuthLayout from '@/layouts/AuthLayout.vue';
</script>

<style scoped></style>
