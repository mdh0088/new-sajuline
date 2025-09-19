/**
 * 포인트 상품 공개 API 컴포저블 (게스트 접근 허용)
 */
import { useQuery, type UseQueryOptions } from '@tanstack/vue-query'
import { useNuxtApp } from 'nuxt/app'

type PointProduct = {
  product_id: number
  product_name: string
  point_amount: number
  price: number
  bonus_point: number
  discount_rate: number
  display_order: number
  is_active: boolean
}

type ApiResponse<T> = {
  success: boolean
  message?: string
  data?: T
  error?: { code: string; message: string }
}

const pointProductApi = {
  async listPublic(): Promise<PointProduct[]> {
    const { $api } = useNuxtApp()
    const res = await $api<ApiResponse<PointProduct[]>>('/api/v1/point-products/public', { method: 'GET' })
    if (!res.success || !res.data) throw new Error(res.error?.message || '포인트 상품 조회 실패')
    return res.data
  }
}

export const usePointProductApi = () => {
  type QueryOpts<T> = Omit<UseQueryOptions<T, Error, T, any>, 'queryKey' | 'queryFn'>

  const usePublicPointProducts = (options?: QueryOpts<PointProduct[]>) => {
    return useQuery({
      queryKey: ['point-products', 'public'],
      queryFn: () => pointProductApi.listPublic(),
      staleTime: 60 * 1000,
      ...options
    })
  }

  return { usePublicPointProducts }
}

export type { PointProduct }



