/**
 * 마일리지 상품 API
 */
import type { UseMutationOptions, UseQueryOptions } from '@tanstack/vue-query'
import { useMutation, useQuery, useQueryClient } from '@tanstack/vue-query'
import type { APIResponse } from '~/types/common/api'
import type { MileageProduct, MileagePurchaseRequest, MileagePurchaseResult } from '~/types/mileage'

type QueryOpts<T> = Omit<UseQueryOptions<T, Error>, 'queryKey' | 'queryFn'>
type MutationOpts<TData, TVariables> = Omit<UseMutationOptions<TData, Error, TVariables>, 'mutationFn'>

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
      },
      ...options,
    })
  }

  return {
    useMileageProducts,
    usePurchaseMileage,
  }
}
