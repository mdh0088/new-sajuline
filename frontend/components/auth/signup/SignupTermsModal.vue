<template>
  <!-- 약관 모달 -->
  <div v-if="show" class="modal" @click="closeModal">
    <div class="modal-content" @click.stop>
      <div class="modal-header">
        <h3 class="modal-title">약관 상세</h3>
        <button class="modal-close" @click="closeModal">×</button>
      </div>
      <div class="modal-body">
        <div v-html="content"></div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
interface Props {
  show: boolean
  content: string
}

const props = defineProps<Props>()
const emit = defineEmits<{
  'close': []
}>()

const closeModal = () => {
  emit('close')
}

// 모달이 열릴 때 스크롤 막기
watch(() => props.show, (newShow) => {
  if (newShow) {
    document.body.style.overflow = 'hidden'
  } else {
    document.body.style.overflow = 'auto'
  }
})
</script>