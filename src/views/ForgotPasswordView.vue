<template>
  <AuthLayout logoHref="/auths/login" :showTerms="false">
    <ForgotPasswordForm />
  </AuthLayout>
</template>

<script setup lang="ts">
import ForgotPasswordForm from '@/components/ForgotPasswordForm.vue';
import AuthLayout from '@/layouts/AuthLayout.vue';
</script>

<style scoped></style>
