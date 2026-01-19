/**
 * API Plugin
 * API 서비스 초기화 플러그인
 */

import { initializeApi } from '~/api'

export default defineNuxtPlugin((nuxtApp) => {
  // API 서비스 초기화 (fetch 옵션을 전달하지 않음으로써 ApiClient가 자체 baseURL을 사용하도록 함)
  initializeApi()
  
  console.log('[API Plugin] API services initialized')
})