/**
 * 브라우저의 자동 스크롤 복원 기능 비활성화 플러그인
 *
 * 브라우저가 페이지 이동 시 이전 스크롤 위치를 복원하는 것을 방지합니다.
 * 이를 통해 router.options.ts의 scrollBehavior 설정이 정상적으로 작동하도록 합니다.
 */
export default defineNuxtPlugin(() => {
  if (process.client && 'scrollRestoration' in window.history) {
    window.history.scrollRestoration = 'manual'
  }
})
