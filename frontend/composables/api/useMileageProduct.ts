/**
 * 마일리지 상품 API
 */
import type { UseMutationOptions, UseQueryOptions } from '@tanstack/vue-query'
import { useMutation, useQuery, useQueryClient } from '@tanstack/vue-query'
import { computed, toValue, type MaybeRefOrGetter } from 'vue'
import type { APIResponse } from '~/types/common/api'
import type { MileageProduct, MileagePurchaseRequest, MileagePurchaseResult, MileageHistoryItem } from '~/types/mileage'

type QueryOpts<T> = Omit<UseQueryOptions<T, Error>, 'queryKey' | 'queryFn'>
type MutationOpts<TData, TVariables> = Omit<UseMutationOptions<TData, Error, TVariables>, 'mutationFn'>

/**
 * 마일리지 내역 조회 파라미터
 */
export interface MileageHistoryParams {
  transaction_type: 'EARN' | 'USE'
  start_dt?: string
  end_dt?: string
  order_type?: 'latest' | 'highest' | 'lowest'
  page?: number
  limit?: number
}

const mileageProductApi = {
  /**
   * 활성 마일리지 상품 목록 조회
   */
  async listProducts(): Promise<MileageProduct[]> {
    const { $api } = useNuxtApp()
    const res = await $api<APIResponse<MileageProduct[]>>('/api/v1/mileage-products/list', {
      method: 'GET',
    })
    if (!res.success || !res.data) {
      throw new Error(res.error?.message || '마일리지 상품 조회 실패')
    }
    return res.data
  },

  /**
   * 마일리지 상품 구매
   */
  async purchaseProduct(request: MileagePurchaseRequest): Promise<MileagePurchaseResult> {
    const { $api } = useNuxtApp()
    const res = await $api<APIResponse<MileagePurchaseResult>>('/api/v1/mileage-products/purchase', {
      method: 'POST',
      body: request,
    })
    if (!res.success || !res.data) {
      throw new Error(res.error?.message || '마일리지 상품 구매 실패')
    }
    return res.data
  },

  /**
   * 마일리지 내역 조회 (적립/사용)
   */
  async listHistory(params: MileageHistoryParams): Promise<{ items: MileageHistoryItem[]; total: number }> {
    const { $api } = useNuxtApp()
    const queryParams = new URLSearchParams()
    queryParams.append('transaction_type', params.transaction_type)
    if (params.start_dt) queryParams.append('start_dt', params.start_dt)
    if (params.end_dt) queryParams.append('end_dt', params.end_dt)
    if (params.order_type) queryParams.append('order_type', params.order_type)
    if (params.page) queryParams.append('page', params.page.toString())
    if (params.limit) queryParams.append('limit', params.limit.toString())

    const res = await $api<APIResponse<MileageHistoryItem[]>>(
      `/api/v1/mileage-products/history?${queryParams.toString()}`,
      { method: 'GET' }
    )
    if (!res.success || !res.data) {
      throw new Error(res.error?.message || '마일리지 내역 조회 실패')
    }
    const total = (res.meta as any)?.pagination?.total || 0
    return { items: res.data, total }
  },
}

export const useMileageProductApi = () => {
  const queryClient = useQueryClient()

  /**
   * 마일리지 상품 목록 조회 쿼리
   */
  const useMileageProducts = (options?: QueryOpts<MileageProduct[]>) => {
    return useQuery({
      queryKey: ['mileage-products', 'list'],
      queryFn: () => mileageProductApi.listProducts(),
      staleTime: 60 * 1000, // 1분
      ...options,
    })
  }

  /**
   * 마일리지 상품 구매 뮤테이션
   */
  const usePurchaseMileage = (options?: MutationOpts<MileagePurchaseResult, MileagePurchaseRequest>) => {
    return useMutation({
      mutationFn: (request: MileagePurchaseRequest) => mileageProductApi.purchaseProduct(request),
      onSuccess: () => {
        // 구매 후 마일리지 상품 목록 갱신
        queryClient.invalidateQueries({ queryKey: ['mileage-products'] })
        // 사용자 정보 갱신 (mileage_point 변경)
        queryClient.invalidateQueries({ queryKey: ['user', 'mypage'] })
        // 마일리지 내역 갱신
        queryClient.invalidateQueries({ queryKey: ['mileage-history'] })
      },
      ...options,
    })
  }

  /**
   * 마일리지 내역 조회 쿼리
   */
  const useMileageHistory = (
    params: MaybeRefOrGetter<MileageHistoryParams>,
    options?: QueryOpts<{ items: MileageHistoryItem[]; total: number }>
  ) => {
    return useQuery({
      queryKey: ['mileage-history', params],
      queryFn: () => mileageProductApi.listHistory(toValue(params)),
      staleTime: 30 * 1000, // 30초
      enabled: computed(() => {
        const p = toValue(params)
        return !!(p.start_dt && p.end_dt)
      }),
      ...options,
    })
  }

  return {
    useMileageProducts,
    usePurchaseMileage,
    useMileageHistory,
  }
}
