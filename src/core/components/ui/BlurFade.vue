<template>
  <Transition
    :name="transitionName"
    appear
    @enter="onEnter"
    @leave="onLeave"
  >
    <div
      v-if="show"
      :class="className"
      :style="computedStyle"
    >
      <slot />
    </div>
  </Transition>
</template>

<script setup lang="ts">
import { computed, ref, onMounted } from 'vue'

interface Props {
  show?: boolean
  delay?: number
  duration?: number
  direction?: 'up' | 'down' | 'left' | 'right'
  offset?: number
  blur?: string
  className?: string
}

const props = withDefaults(defineProps<Props>(), {
  show: true,
  delay: 0,
  duration: 400,
  direction: 'down',
  offset: 6,
  blur: '6px',
  className: ''
})

const transitionName = 'blur-fade'
const internalShow = ref(false)

const computedStyle = computed(() => ({
  '--blur-fade-duration': `${props.duration}ms`,
  '--blur-fade-delay': `${props.delay}ms`,
  '--blur-fade-offset': `${props.offset}px`,
  '--blur-fade-blur': props.blur
}))

const onEnter = (el: Element) => {
  el.classList.add('blur-fade-enter-active')
}

const onLeave = (el: Element) => {
  el.classList.add('blur-fade-leave-active')
}

onMounted(() => {
  setTimeout(() => {
    internalShow.value = props.show
  }, props.delay)
})
</script>

<style scoped>
.blur-fade-enter-active,
.blur-fade-leave-active {
  transition: all var(--blur-fade-duration, 400ms) cubic-bezier(0.4, 0, 0.2, 1);
  transition-delay: var(--blur-fade-delay, 0ms);
}

.blur-fade-enter-from {
  opacity: 0;
  filter: blur(var(--blur-fade-blur, 6px));
  transform: translateY(var(--blur-fade-offset, 6px));
}

.blur-fade-leave-to {
  opacity: 0;
  filter: blur(var(--blur-fade-blur, 6px));
  transform: translateY(calc(-1 * var(--blur-fade-offset, 6px)));
}

.blur-fade-enter-to,
.blur-fade-leave-from {
  opacity: 1;
  filter: blur(0px);
  transform: translateY(0);
}

/* Direction variations */
.blur-fade-up.blur-fade-enter-from {
  transform: translateY(calc(-1 * var(--blur-fade-offset, 6px)));
}

.blur-fade-left.blur-fade-enter-from {
  transform: translateX(var(--blur-fade-offset, 6px));
}

.blur-fade-right.blur-fade-enter-from {
  transform: translateX(calc(-1 * var(--blur-fade-offset, 6px)));
}
</style>