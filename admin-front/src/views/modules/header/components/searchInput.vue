<template>
    <div class="serchbox" @click="collapseFilter()">
        <svg>
            <use href="@/assets/svg/icon-sprite.svg#Search"></use>
        </svg>
    </div>
    <div class="form-group search-form" :class="filtered ? 'open' : ''">
        <input type="text" placeholder="Search here...">
    </div>
</template>
<script lang="ts" setup>
import { ref } from 'vue'
const filtered = ref<boolean>(false);

function collapseFilter() {
    filtered.value = !filtered.value;
}
</script>