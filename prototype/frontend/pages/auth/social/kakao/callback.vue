<script setup lang="ts">
// 카카오 OAuth 콜백 처리 페이지
useHead({
  title: '카카오 로그인 처리 중...',
  meta: [
    { name: 'robots', content: 'noindex, nofollow' }
  ]
})

// URL 파라미터에서 code와 error 추출
const route = useRoute()
const code = route.query.code as string
const error = route.query.error as string
const error_description = route.query.error_description as string

// 페이지 로드 시 즉시 처리
onMounted(() => {
  try {
    if (error) {
      // OAuth 에러 발생
      const errorMessage = error_description || '카카오 로그인 중 오류가 발생했습니다.'
      
      // 부모 창에 에러 메시지 전송
      if (window.opener) {
        window.opener.postMessage({
          type: 'SOCIAL_LOGIN_ERROR',
          provider: 'kakao',
          message: errorMessage
        }, window.location.origin)
      }
      
      // 팝업 창 닫기
      window.close()
      
    } else if (code) {
      // OAuth 성공 - 부모 창에 code 전송
      if (window.opener) {
        window.opener.postMessage({
          type: 'SOCIAL_LOGIN_SUCCESS',
          provider: 'kakao',
          code: code
        }, window.location.origin)
      }
      
      // 팝업 창 닫기
      window.close()
      
    } else {
      // 예상하지 못한 상황
      throw new Error('OAuth 응답에 필요한 파라미터가 없습니다.')
    }
    
  } catch (error: any) {
    console.error('카카오 OAuth 콜백 처리 오류:', error)
    
    // 부모 창에 에러 메시지 전송
    if (window.opener) {
      window.opener.postMessage({
        type: 'SOCIAL_LOGIN_ERROR',
        provider: 'kakao',
        message: '카카오 로그인 처리 중 오류가 발생했습니다.'
      }, window.location.origin)
    }
    
    // 팝업 창 닫기
    window.close()
  }
})

// 리다이렉트 모드 처리 (모바일)
onMounted(async () => {
  // 팝업이 아닌 경우 (모바일 리다이렉트)
  if (!window.opener && (code || error)) {
    try {
      if (error) {
        // 에러 발생 시 로그인 페이지로 이동
        const errorMessage = error_description || '카카오 로그인 중 오류가 발생했습니다.'
        await navigateTo(`/login?error=${encodeURIComponent(errorMessage)}`)
        return
      }
      
      if (code) {
        // 콜백 처리
        const { authAPI } = await import('~/api/services/auth')
        const { handleSocialLoginResult } = await import('~/utils/social-login')
        
        const result = await authAPI.processSocialCallback('kakao', code)
        
        // 신규 사용자이고 추가 정보가 필요한 경우
        if (result.is_new_user && result.requires_additional_info) {
          console.log('[DEBUG] 카카오 신규 사용자 - 추가 정보 입력 필요:', result)
          
          // 소셜 사용자 정보를 세션에 저장
          const socialInfo = (result as any).social_user_info || (result as any).user_info
          if (socialInfo) {
            sessionStorage.setItem('social_user_info', JSON.stringify(socialInfo))
          }
          
          // 누락된 필드 정보 저장
          if (result.missing_fields) {
            sessionStorage.setItem('missing_fields', JSON.stringify(result.missing_fields))
          }
          
          // 기존 signup.vue로 리다이렉트 (소셜 모드)
          await navigateTo('/signup?social=true')
          return
        }
        
        // 기존 사용자 또는 추가 정보 없이 가입 가능한 경우
        const processedResult = handleSocialLoginResult(result)
        
        if (processedResult.success) {
          // 소셜 로그인 성공 (기존 사용자)
          console.log('[DEBUG] 카카오 기존 사용자 로그인 성공:', processedResult)
          await navigateTo('/?message=social_login_success')
        } else {
          throw new Error(processedResult.message || '카카오 로그인 처리 실패')
        }
      }
      
    } catch (error: any) {
      console.error('카카오 리다이렉트 콜백 처리 오류:', error)
      await navigateTo(`/login?error=${encodeURIComponent('카카오 로그인 처리 중 오류가 발생했습니다.')}`)
    }
  }
})
</script>

<template>
  <div class="min-h-screen bg-slate-950 text-white flex items-center justify-center">
    <div class="text-center">
      <div class="text-6xl mb-4">⏳</div>
      <h1 class="text-xl font-semibold mb-2">카카오 로그인 처리 중...</h1>
      <p class="text-white/70">잠시만 기다려주세요.</p>
    </div>
  </div>
</template> 