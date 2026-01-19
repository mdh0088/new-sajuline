<script setup lang="ts">
interface Props {
  variant?: 'default' | 'outline' | 'ghost'
  padding?: 'none' | 'sm' | 'md' | 'lg'
  hover?: boolean
  clickable?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  variant: 'default',
  padding: 'md',
  hover: false,
  clickable: false
})

const emit = defineEmits<{
  click: [event: MouseEvent]
}>()

const baseClasses = 'rounded-lg transition-all duration-200'

const variantClasses = {
  default: 'bg-white shadow-sm border border-gray-200',
  outline: 'border border-gray-300 bg-transparent',
  ghost: 'bg-gray-50'
}

const paddingClasses = {
  none: '',
  sm: 'p-3',
  md: 'p-6',
  lg: 'p-8'
}

const cardClasses = computed(() => [
  baseClasses,
  variantClasses[props.variant],
  paddingClasses[props.padding],
  {
    'hover:shadow-md hover:border-gray-300': props.hover,
    'cursor-pointer': props.clickable
  }
])

const handleClick = (event: MouseEvent) => {
  if (props.clickable) {
    emit('click', event)
  }
}
</script>

<template>
  <div 
    :class="cardClasses"
    @click="handleClick"
  >
    <slot />
  </div>
</template> 