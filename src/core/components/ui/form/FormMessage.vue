<script lang="ts" setup>
import { cn } from '@/shared/utils/utils.ts';
import { ErrorMessage } from 'vee-validate';
import { type HTMLAttributes, toValue } from 'vue';
import { useFormField } from './useFormField';

const props = defineProps<{
  class?: HTMLAttributes['class'];
}>();

const { name, formMessageId } = useFormField();
</script>

<template>
  <ErrorMessage
    :id="formMessageId"
    data-slot="form-message"
    as="p"
    :name="toValue(name)"
    :class="cn('text-destructive text-sm', props.class)"
  />
</template>
