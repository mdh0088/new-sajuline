import { defineStore } from 'pinia'
import { ref } from 'vue'
import header from "@/core/data/header.json"
interface item {
    title: string,
    time: string,
    font: string,
    class: string
}
interface msg {
    img: string,
    name: string,
    desc: string
}
interface profi {
    icon: string,
    title: string,
    path: string
}

export const useHeaderStore = defineStore('header', () => {

    const data: item[] = (JSON.parse(JSON.stringify(header.notification)))
    const meg = ref<msg[]>(header.message)
    const profileItem = ref<profi[]>(header.profile)
    return {
        data,
        meg,
        profileItem
    }
})
