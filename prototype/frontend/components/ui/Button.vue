<script setup lang="ts">
interface Props {
  variant?: 'primary' | 'secondary' | 'outline' | 'ghost'
  size?: 'sm' | 'md' | 'lg'
  disabled?: boolean
  loading?: boolean
  type?: 'button' | 'submit' | 'reset'
}

const props = withDefaults(defineProps<Props>(), {
  variant: 'primary',
  size: 'md',
  disabled: false,
  loading: false,
  type: 'button'
})

const emit = defineEmits<{
  click: [event: MouseEvent]
}>()

const baseClasses = 'inline-flex items-center justify-center font-medium transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50'

const variantClasses = {
  primary: 'bg-purple-600 text-white hover:bg-purple-700 focus-visible:ring-purple-500',
  secondary: 'bg-gray-100 text-gray-900 hover:bg-gray-200 focus-visible:ring-gray-500',
  outline: 'border border-gray-300 bg-transparent hover:bg-gray-100 focus-visible:ring-gray-500',
  ghost: 'hover:bg-gray-100 focus-visible:ring-gray-500'
}

const sizeClasses = {
  sm: 'h-8 px-3 text-sm rounded-md',
  md: 'h-10 px-4 text-sm rounded-md',
  lg: 'h-12 px-6 text-base rounded-lg'
}

const buttonClasses = computed(() => [
  baseClasses,
  variantClasses[props.variant],
  sizeClasses[props.size]
])

const handleClick = (event: MouseEvent) => {
  if (!props.disabled && !props.loading) {
    emit('click', event)
  }
}
</script>

<template>
  <button
    :class="buttonClasses"
    :disabled="disabled || loading"
    :type="type"
    @click="handleClick"
  >
    <div v-if="loading" class="mr-2 animate-spin">
      <svg class="h-4 w-4" viewBox="0 0 24 24">
        <circle
          cx="12"
          cy="12"
          r="10"
          stroke="currentColor"
          stroke-width="4"
          fill="none"
          class="opacity-25"
        />
        <path
          fill="currentColor"
          d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
          class="opacity-75"
        />
      </svg>
    </div>
    <slot />
  </button>
</template> 