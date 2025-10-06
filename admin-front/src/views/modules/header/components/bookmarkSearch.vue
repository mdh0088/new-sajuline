<template>
    <svg>
        <use href="@/assets/svg/icon-sprite.svg#Bookmark"></use>
    </svg>
    <div class="onhover-show-div bookmark-flip" :class="bookmarkSearchBox ? 'active' : ''">
        <div class="flip-card">
            <div class="flip-card-inner" :class="bookmarkSearchBox ? 'flipped' : ''">
                <div class="front">
                    <h6 class="f-18 mb-0 dropdown-title">Bookmark</h6>
                    <ul class="bookmark-dropdown">
                        <li class="custom-scrollbar">
                            <div class="row">
                                <div class="col-4 text-center" v-for="(menuItem, index) in bookmarkItems.slice(0, 8)"
                                    :key="index"><router-link :to="{ path: menuItem.path }">
                                        <div class="bookmark-content">
                                            <div class="bookmark-icon"><svg>
<!--                                                    <use
                                                        :xlink:href="require('@/assets/svg/icon-sprite.svg') + `#${menuItem.icon1}`">
                                                    </use>-->
                                                </svg></div><span>{{ menuItem.title }}
                                            </span>
                                        </div>
                                    </router-link></div>
                            </div>
                        </li>
                        <li class="text-centermedia-body" @click="openBookmark"> <a class="flip-btn f-w-700" id="flip-btn"
                                href="javascript:void(0)">Add New Bookmark</a></li>
                    </ul>
                </div>
                <div class="back">
                    <ul>
                        <li class="position-relative p-0 m-0">
                            <div class="bookmark-dropdown flip-back-content">
                                <input type="text" placeholder="search..." @keyup="searchTerm" v-model="terms">
                            </div>

                        </li>

                        <li @click="openBookmark"><a class="f-w-700 d-block flip-back" id="flip-back"
                                href="javascript:void(0)">Back</a></li>
                    </ul>
                </div>
            </div>
        </div>
    </div>
</template>
<script lang="ts" setup>
import { ref, watch, onMounted } from 'vue'
import { useMenuStore } from "@/store/menu"
import { storeToRefs } from "pinia";

interface bookmark {
    icon1: string,
    path: string,
    title: string,
}
const bookmarkSearchBox = ref<boolean>(false)
const bookmarkItems = ref<bookmark[]>([])
const bookmarkSearchResult = ref<boolean>(false)
const bookmarkSearchResultEmpty = ref<boolean>(false)
const terms = ref<string>("");
const store = useMenuStore()
const menu = store.data
const { searchDatas: searchMenuItems } = storeToRefs(store);
watch(
    () => [searchMenuItems, terms],
    () => {
        terms.value ? addFix() : removeFix()
        if (!searchMenuItems.value.length) bookmarkSearchResultEmpty.value = true;
        else bookmarkSearchResultEmpty.value = false;
    },
    { deep: true },
);
function openBookmark() {
    bookmarkSearchBox.value = !bookmarkSearchBox.value;
    if (!bookmarkSearchBox.value) removeFix();
}
function removeFix() {
    bookmarkSearchResult.value = false;
}
function addFix() {
    bookmarkSearchResult.value = true;
}
function searchTerm() {
    store.searchterm(terms.value);
}

onMounted(() => {
    menu.filter((items) => {
        console.log('jjj', items);

        if (items.bookmark) {
            bookmarkItems.value.push(items);
        }

    });
})
</script>