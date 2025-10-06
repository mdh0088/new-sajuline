<template>
    <div class="mode" :class="actives ? 'active' : ''">
        <svg v-show="mixLayout == 'light'" @click="customizeMixLayout('dark-only')">
            <use href="@/assets/svg/icon-sprite.svg#moon"></use>
        </svg>

        <svg v-show="mixLayout == 'dark-only'" @click="customizeMixLayout('light')">
            <use href="@/assets/svg/icon-sprite.svg#moon"></use>
        </svg>
    </div>
</template>
<script lang="ts" setup>
import { ref } from 'vue';
import { uselayoutStore } from '@/store/layout'
const mixLayout = ref<string>('light')
const actives = ref<boolean>(false)
let store = uselayoutStore()

function customizeMixLayout(val: string) {
    mixLayout.value = val;
    actives.value = !actives.value
    store.setLayout({ class: val })
}
</script>