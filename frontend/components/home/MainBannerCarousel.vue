<template>
  <section class="hero-banner">
    <div class="banner-swiper" ref="containerRef">
      <div class="banner-track" :style="trackStyle">
        <div v-for="item in banners" :key="item.banner_id" class="banner-slide">
          <component
            :is="linkComponent(item)"
            :to="componentTo(item)"
            :href="componentHref(item)"
            :target="item.link_target === 'BLANK' ? '_blank' : undefined"
            :rel="item.link_target === 'BLANK' ? 'noopener noreferrer' : undefined"
            class="banner-link"
            @click="handleClick(item)"
          >
            <img :src="resolveImage(item.image_url)" :alt="item.banner_name" loading="lazy" />
          </component>
        </div>
      </div>

      <div class="banner-dots" v-if="banners.length > 1">
        <button v-for="(dot, i) in banners.length" :key="i" :class="['dot', { active: i === current } ]" @click="goTo(i)" aria-label="go to slide" />
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onBeforeUnmount, watch } from 'vue'
import { useBannerApi } from '~/composables/api/useBanner'
import type { BannerItem } from '~/types/banner'
import { useCdn } from '~/composables/utils/useCdn'

const { useMainBanners, useBannerClick } = useBannerApi()
const { data } = useMainBanners()
const { mutate: clickBanner } = useBannerClick()

const banners = computed<BannerItem[]>(() => data.value ?? [])

const { cdnUrl } = useCdn()
const resolveImage = (raw: string) => {
  // counselor/mypage 참조: 절대 URL 대응 + 디렉터리 프리픽스 차이(/banner)
  const trimmed = (raw || '').trim()
  if (!trimmed) return ''
  if (/^https?:\/\//i.test(trimmed)) return cdnUrl(trimmed)
  return cdnUrl('banner', trimmed)
}

// 간단한 CSS 기반 캐러셀 (오토플레이/스와이프)
const containerRef = ref<HTMLElement | null>(null)
const current = ref(0)
const autoplayMs = 4000
let timer: any = null

const trackStyle = computed(() => ({
  transform: `translateX(-${current.value * 100}%)`
}))

const start = () => {
  stop()
  if ((banners.value?.length ?? 0) <= 1) return
  timer = setInterval(() => {
    current.value = (current.value + 1) % banners.value.length
  }, autoplayMs)
}

const stop = () => {
  if (timer) {
    clearInterval(timer)
    timer = null
  }
}

const goTo = (i: number) => {
  current.value = i % (banners.value?.length || 1)
  start()
}

// 터치 스와이프
let startX = 0
let deltaX = 0
const onTouchStart = (e: TouchEvent) => {
  const t = e.touches?.item(0) || e.changedTouches?.item(0)
  if (!t) return
  startX = t.clientX
  deltaX = 0
  stop()
}
const onTouchMove = (e: TouchEvent) => {
  const t = e.touches?.item(0) || e.changedTouches?.item(0)
  if (!t) return
  deltaX = t.clientX - startX
}
const onTouchEnd = () => {
  const threshold = 40
  const len = banners.value.length
  if (!len) { start(); return }
  if (Math.abs(deltaX) > threshold) {
    if (deltaX < 0) current.value = (current.value + 1) % len
    else current.value = (current.value - 1 + len) % len
  }
  start()
}

onMounted(() => {
  const el = containerRef.value
  if (el) {
    el.addEventListener('touchstart', onTouchStart, { passive: true })
    el.addEventListener('touchmove', onTouchMove, { passive: true })
    el.addEventListener('touchend', onTouchEnd, { passive: true })
  }
  start()
})

onBeforeUnmount(() => {
  const el = containerRef.value
  if (el) {
    el.removeEventListener('touchstart', onTouchStart)
    el.removeEventListener('touchmove', onTouchMove)
    el.removeEventListener('touchend', onTouchEnd)
  }
  stop()
})

watch(banners, () => {
  current.value = 0
  start()
})

// 링크 컴포넌트 선택 (SELF: NuxtLink, BLANK: a)
const isAbsolute = (url: string) => /^https?:\/\//i.test(url)
const linkComponent = (item: BannerItem) => {
  if (!item.link_url) return 'div'
  if (isAbsolute(item.link_url)) return 'a'
  return item.link_target === 'BLANK' ? 'a' : 'NuxtLink'
}
const componentHref = (item: BannerItem) => {
  if (!item.link_url) return undefined
  // 절대 URL이거나, 상대 URL이지만 BLANK 타겟인 경우 href 반환
  if (isAbsolute(item.link_url) || item.link_target === 'BLANK') {
    return item.link_url
  }
  return undefined
}
const componentTo = (item: BannerItem) => {
  if (!item.link_url) return undefined
  return isAbsolute(item.link_url) ? undefined : item.link_url
}

const handleClick = (item: BannerItem) => {
  if (!item?.banner_id) return
  clickBanner(item.banner_id)
}
</script>

<style scoped>
.banner-swiper { position: relative; width: 100%; overflow: hidden; }
.banner-track { display: flex; width: 100%; transition: transform 0.4s ease; }
.banner-slide { flex: 0 0 100%; }
.banner-link, .banner-slide img { display: block; width: 100%; height: auto; }
a.banner-link { cursor: pointer; }
.banner-dots { position: absolute; left: 0; right: 0; bottom: 8px; display: flex; gap: 6px; justify-content: center; }
.dot { width: 6px; height: 6px; border-radius: 9999px; background: rgba(255,255,255,0.4); border: none; padding: 0; }
.dot.active { background: rgba(255,255,255,0.95); }
</style>


