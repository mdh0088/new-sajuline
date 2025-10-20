/**
 * 상담사 지원 API 컴포저블 (Vue Query)
 * - 상담사 신청 관련 API 호출
 */
import { useMutation, type UseMutationOptions } from '@tanstack/vue-query'
import { useNuxtApp } from 'nuxt/app'
import type { APIResponse, APIError } from '~/types/common/api'

/**
 * 상담사 지원 요청 데이터
 */
export interface CounselorApplicationRequest {
  name: string
  nickname: string
  email: string
  phone: string
  address?: string
  specialty_types: string[]
  keywords?: string
  introduction?: string
  photos?: File[]
}

/**
 * 상담사 지원 응답 데이터
 */
export interface CounselorApplicationResponse {
  application_id: number
  name: string
  nickname: string
  email: string
  phone: string
  address?: string
  specialty_types?: string[]
  keywords?: string
  introduction?: string
  upload_image1?: string
  upload_image2?: string
  upload_image3?: string
  application_status: string
  admin_note?: string
  reviewed_by?: number
  reviewed_at?: string
  created_at: string
  updated_at?: string
}

/**
 * 상담사 지원 API 함수
 */
const counselorApplicationApi = {
  async createApplication(data: CounselorApplicationRequest): Promise<CounselorApplicationResponse> {
    const { $api } = useNuxtApp()

    // FormData 생성
    const formData = new FormData()
    formData.append('name', data.name)
    formData.append('nickname', data.nickname)
    formData.append('email', data.email)
    formData.append('phone', data.phone)
    if (data.address) formData.append('address', data.address)
    formData.append('specialty_types', JSON.stringify(data.specialty_types))
    if (data.keywords) formData.append('keywords', data.keywords)
    if (data.introduction) formData.append('introduction', data.introduction)

    // 사진 첨부
    if (data.photos && data.photos.length > 0) {
      data.photos.forEach((photo) => {
        formData.append('photos', photo)
      })
    }

    const response = await $api<APIResponse<CounselorApplicationResponse>>(
      '/api/v1/counselor-applications',
      {
        method: 'POST',
        body: formData
      }
    )

    if (!response.success || !response.data) {
      throw new Error(response.error?.message || '상담사 신청에 실패했습니다.')
    }

    return response.data
  }
}

/**
 * Vue Query 기반 상담사 지원 API 훅
 */
export const useCounselorApplicationQueries = () => {
  const useCreateApplication = (
    options?: UseMutationOptions<CounselorApplicationResponse, APIError, CounselorApplicationRequest>
  ) => {
    return useMutation({
      mutationFn: counselorApplicationApi.createApplication,
      ...options
    })
  }

  return {
    useCreateApplication
  }
}
