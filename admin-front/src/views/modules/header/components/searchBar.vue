<template>
    <form class="col-auto form-inline search-full" action="#" method="get">
        <div class="form-group">
            <div class="Typeahead Typeahead&#45;&#45;twitterUsers">
                <div class="u-posRelative">
                  <div>

                  </div>
                    <input class="demo-input Typeahead-input form-control-plaintext w-100" type="text"
                        placeholder="Type to Search .." name="q" title="" autofocus>

                    <svg class="search-bg svg-color">
                        <use href="@/assets/svg/icon-sprite.svg#Search"></use>
                    </svg>
                </div>
                <div class="Typeahead-menu"></div>
            </div>
        </div>
    </form>
</template>
<script lang="ts" setup>
import { nextTick, ref } from 'vue'
import type { InputInstance } from 'element-plus'

const radio1 = ref('1')


const value = ref('핸드폰')

const options = [
  {
    value: 'Option1',
    label: '핸드폰',
  },
  {
    value: 'Option2',
    label: '이메일',
  },
  {
    value: 'Option3',
    label: '상담사 코드',
  },
  {
    value: 'Option4',
    label: '이름',
  },
  {
    value: 'Option5',
    label: '닉네임',
  },
]


const inputValue = ref('')
const dynamicTags = ref(['Tag 1', 'Tag 2', 'Tag 3'])
const inputVisible = ref(false)
const InputRef = ref<InputInstance>()

const handleClose = (tag: string) => {
  dynamicTags.value.splice(dynamicTags.value.indexOf(tag), 1)
}

const showInput = () => {
  inputVisible.value = true
  nextTick(() => {
    InputRef.value!.input!.focus()
  })
}

const handleInputConfirm = () => {
  if (inputValue.value) {
    dynamicTags.value.push(inputValue.value)
  }
  inputVisible.value = false
  inputValue.value = ''
}
</script>
<style scoped>
.tags-input {
  border: 1px solid #ccc; /* 테두리 */
  padding: 5px; /* 내부 여백 */
  border-radius: 4px; /* 모서리 둥글게 */
  display: flex; /* flexbox 레이아웃 사용 */
  flex-wrap: wrap; /* 태그가 많아질 때 줄바꿈 */
  align-items: center; /* 세로 중앙 정렬 */
  min-width: 800px;
  min-height: 30px;
}
</style>

