/**
 * Social Auth Composable
 * 소셜 로그인 관련 로직을 추상화한 컴포저블
 */

import { ref } from 'vue'
import type { Ref } from 'vue'
import { authAPI } from '~/api/services/auth'
import { setTokens } from '~/utils/auth-token'
import { useAuth } from './useAuth'

export type SocialProvider = 'kakao' | 'naver'

export interface SocialSignupData {
  provider: SocialProvider
  social_id: string
  email?: string
  name: string
  nickname?: string
  agree_terms: boolean
  agree_privacy: boolean
  agree_marketing: boolean
}

export const useSocialAuth = () => {
  const { fetchCurrentUser } = useAuth()
  const isLoading = ref(false)
  const error: Ref<string | null> = ref(null)
  
  /**
   * 소셜 로그인 시작 (OAuth URL로 리다이렉트)
   */
  const startSocialLogin = async (provider: SocialProvider) => {
    isLoading.value = true
    error.value = null
    
    try {
      const response = await authAPI.getSocialLoginUrl(provider)
      
      if (response.auth_url) {
        // OAuth 페이지로 리다이렉트
        window.location.href = response.auth_url
      } else {
        throw new Error('OAuth URL을 가져올 수 없습니다.')
      }
    } catch (err: any) {
      error.value = err.message || `${provider} 로그인을 시작할 수 없습니다.`
      throw err
    } finally {
      isLoading.value = false
    }
  }
  
  /**
   * 소셜 로그인 콜백 처리
   */
  const handleSocialCallback = async (
    provider: SocialProvider, 
    code: string, 
    state?: string
  ) => {
    isLoading.value = true
    error.value = null
    
    try {
      const response = await authAPI.processSocialCallback(provider, code, state)
      
      // 로그인 성공 (기존 회원)
      if (!response.is_new_user && response.tokens?.access_token) {
        setTokens(response.tokens.access_token, response.tokens.refresh_token)
        await fetchCurrentUser()
        return { 
          success: true, 
          requiresSignup: false,
          data: response 
        }
      }
      
      // 회원가입 필요 (신규 사용자)
      if (response.is_new_user && response.requires_additional_info) {
        const socialInfo = (response as any).social_user_info || (response as any).user_info
        return { 
          success: true, 
          requiresSignup: true,
          data: socialInfo 
        }
      }
      
      throw new Error('예상치 못한 응답 형식입니다.')
    } catch (err: any) {
      error.value = err.message || `${provider} 로그인 처리에 실패했습니다.`
      return { 
        success: false, 
        requiresSignup: false,
        error: error.value 
      }
    } finally {
      isLoading.value = false
    }
  }
  
  /**
   * 소셜 회원가입
   */
  const socialSignup = async (data: SocialSignupData) => {
    isLoading.value = true
    error.value = null
    
    try {
      const response = await authAPI.socialSignup(data)
      
      // 회원가입 성공 시 자동 로그인
      if (response.tokens?.access_token) {
        setTokens(response.tokens.access_token, response.tokens.refresh_token)
        await fetchCurrentUser()
      }
      
      return response
    } catch (err: any) {
      error.value = err.message || '소셜 회원가입에 실패했습니다.'
      throw err
    } finally {
      isLoading.value = false
    }
  }
  
  /**
   * 소셜 로그인 URL 생성 (팝업용)
   */
  const getSocialLoginUrl = async (provider: SocialProvider): Promise<string | null> => {
    try {
      const response = await authAPI.getSocialLoginUrl(provider)
      return response.auth_url || null
    } catch (err) {
      console.error(`Failed to get ${provider} login URL:`, err)
      return null
    }
  }
  
  return {
    // 상태
    isLoading: readonly(isLoading),
    error: readonly(error),
    
    // 메서드
    startSocialLogin,
    handleSocialCallback,
    socialSignup,
    getSocialLoginUrl
  }
}