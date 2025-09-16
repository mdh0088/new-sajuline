/**
 * 멤버십 등급 공개 API 컴포저블 (게스트 접근 허용)
 */
import { useQuery, type UseQueryOptions } from '@tanstack/vue-query'
import { useNuxtApp } from 'nuxt/app'
import { computed } from 'vue'

type GradeItem = {
  grade_code: string
  grade_name: string
  grade_level: number
  min_purchase_amount: number
  point_earn_rate: number | string
  discount_rate: number | string
  grade_image_url?: string | null
  description?: string | null
}

type ApiResponse<T> = {
  success: boolean
  message?: string
  data?: T
  error?: { code: string; message: string }
}

const gradeApi = {
  async listPublic(): Promise<GradeItem[]> {
    const { $api } = useNuxtApp()
    const res = await $api<ApiResponse<GradeItem[]>>('/api/v1/grades/public', { method: 'GET' })
    if (!res.success || !res.data) throw new Error(res.error?.message || '등급 조회 실패')
    return res.data
  }
}

export const useGradeApi = () => {
  type QueryOpts<T> = Omit<UseQueryOptions<T, Error, T, any>, 'queryKey' | 'queryFn'>

  const usePublicGrades = (options?: QueryOpts<GradeItem[]>) => {
    return useQuery({
      queryKey: ['grades', 'public'],
      queryFn: () => gradeApi.listPublic(),
      staleTime: 60 * 1000,
      ...options
    })
  }

  return { usePublicGrades }
}


