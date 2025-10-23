import type { RouterConfig } from '@nuxt/schema'

/**
 * 사주라인 라우터 설정
 *
 * 페이지 이동 시 스크롤 동작을 제어합니다.
 * - 새로운 페이지로 이동할 때는 항상 최상단(0, 0)으로 스크롤
 * - 브라우저 뒤로가기/앞으로가기 시에도 최상단으로 이동
 * - savedPosition이 있어도 무시하고 항상 최상단으로 이동
 * - 데스크톱 레이아웃의 .mobile-container 스크롤도 초기화
 */
export default <RouterConfig>{
  scrollBehavior(to, from, savedPosition) {
    // 다음 틱에서 모든 스크롤 가능한 컨테이너를 초기화
    return new Promise((resolve) => {
      setTimeout(() => {
        // 모든 스크롤 가능한 요소들을 찾아서 최상단으로 이동
        if (process.client) {
          // 메인 윈도우 스크롤
          window.scrollTo(0, 0)

          // 데스크톱 레이아웃의 mobile-container 스크롤 초기화
          const mobileContainer = document.querySelector('.mobile-container')
          if (mobileContainer) {
            mobileContainer.scrollTop = 0
          }

          // mobile-container 내부의 스크롤 가능한 div 초기화
          const innerScrollDivs = document.querySelectorAll('.mobile-container > div')
          innerScrollDivs.forEach((div: any) => {
            if (div.scrollTop !== undefined) {
              div.scrollTop = 0
            }
          })

          // 모든 overflow-y: auto 요소 초기화
          const scrollableElements = document.querySelectorAll('[style*="overflow-y: auto"]')
          scrollableElements.forEach((el: any) => {
            el.scrollTop = 0
          })
        }

        resolve({ top: 0, left: 0, behavior: 'instant' })
      }, 0)
    })
  }
}
