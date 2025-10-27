<template>
  <div class="skeleton-loader" :class="[variant, { rounded }]" :style="computedStyle">
    <div class="skeleton-shimmer"></div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

interface Props {
  variant?: 'text' | 'circular' | 'rectangular' | 'card'
  width?: string | number
  height?: string | number
  rounded?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  variant: 'text',
  width: '100%',
  height: 'auto',
  rounded: false
})

const computedStyle = computed(() => {
  const style: Record<string, string> = {}

  if (props.width) {
    style.width = typeof props.width === 'number' ? `${props.width}px` : props.width
  }

  if (props.height) {
    style.height = typeof props.height === 'number' ? `${props.height}px` : props.height
  }

  return style
})
</script>

<style scoped>
.skeleton-loader {
  position: relative;
  overflow: hidden;
  background-color: #e0e0e0;
  background: linear-gradient(90deg, #e0e0e0 25%, #f0f0f0 50%, #e0e0e0 75%);
  background-size: 200% 100%;
  animation: shimmer 1.5s ease-in-out infinite;
}

.skeleton-shimmer {
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(
    90deg,
    transparent,
    rgba(255, 255, 255, 0.5),
    transparent
  );
  animation: shimmer-slide 1.5s ease-in-out infinite;
}

/* Variants */
.text {
  height: 1em;
  border-radius: 4px;
}

.circular {
  border-radius: 50%;
  width: 40px;
  height: 40px;
}

.rectangular {
  border-radius: 8px;
}

.card {
  border-radius: 12px;
  min-height: 120px;
}

.rounded {
  border-radius: 9999px;
}

/* Animations */
@keyframes shimmer {
  0% {
    background-position: 200% 0;
  }
  100% {
    background-position: -200% 0;
  }
}

@keyframes shimmer-slide {
  0% {
    left: -100%;
  }
  100% {
    left: 100%;
  }
}

/* Dark mode support */
@media (prefers-color-scheme: dark) {
  .skeleton-loader {
    background-color: #2a2a2a;
    background: linear-gradient(90deg, #2a2a2a 25%, #3a3a3a 50%, #2a2a2a 75%);
  }

  .skeleton-shimmer {
    background: linear-gradient(
      90deg,
      transparent,
      rgba(255, 255, 255, 0.1),
      transparent
    );
  }
}
</style>
