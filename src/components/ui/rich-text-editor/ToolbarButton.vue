<template>
  <button
    type="button"
    :class="[
      'inline-flex items-center justify-center h-8 px-2 text-sm font-medium rounded-md transition-colors',
      'hover:bg-gray-100 hover:text-gray-900 dark:hover:bg-gray-800 dark:hover:text-gray-100',
      'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500',
      'disabled:pointer-events-none disabled:opacity-50',
      isActive 
        ? 'bg-blue-600 text-white dark:bg-blue-500' 
        : 'bg-transparent text-gray-600 hover:text-gray-900 dark:text-gray-400 dark:hover:text-gray-100'
    ]"
    :disabled="disabled"
    :title="title"
    @click="$emit('click', $event)"
  >
    <slot />
  </button>
</template>

<script setup lang="ts">
interface Props {
  isActive?: boolean;
  disabled?: boolean;
  title?: string;
}

interface Emits {
  (e: 'click', event: MouseEvent): void;
}

withDefaults(defineProps<Props>(), {
  isActive: false,
  disabled: false,
});

defineEmits<Emits>();
</script>