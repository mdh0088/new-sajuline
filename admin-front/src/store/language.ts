
import { defineStore } from 'pinia'
import { ref } from "vue"

import language from "@/core/data/language.json"
import lang from "@/types/language"

export const useLanguageStore = defineStore('language', () => {
    const langIcon = ref('')
    const langLangauge = ref('')
    const data: lang[] = (JSON.parse(JSON.stringify(language.language)))
    function changeLang(val: any) {
        localStorage.setItem('currentLanguage', val.id);
        localStorage.setItem('currentLanguageIcon', val.icon);
        langIcon.value = val.icon || 'flag-icon-us'
        langLangauge.value = val.id || 'EN'
    }
    return {
        data,
        changeLang,
        langIcon,
        langLangauge
    }
})
