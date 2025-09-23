/**
 * 배너 API 컴포저블 (게스트 공개)
 */
import { computed, unref, type Ref } from 'vue'
import { useQuery, useMutation, useQueryClient, type UseQueryOptions, type UseMutationOptions } from '@tanstack/vue-query'
import type { APIResponse, APIError } from '~/types/common/api'
import type { BannerItem } from '~/types/banner'
import { useNuxtApp } from 'nuxt/app'

// API 호출 함수들
const bannerApi = {
  async listMain(): Promise<BannerItem[]> {
    const { $api } = useNuxtApp()
    const res = await $api<APIResponse<BannerItem[]>>('/api/v1/banners/public/main', { method: 'GET' })
    if (!res.success) throw { message: res.error?.message || '배너 목록 조회 실패', statusCode: 400 } satisfies APIError
    return res.data ?? []
  },

  async click(bannerId: number): Promise<void> {
    const { $api } = useNuxtApp()
    const res = await $api<APIResponse<any>>(`/api/v1/banners/${bannerId}/click`, { method: 'POST' })
    if (!res.success) throw { message: res.error?.message || '배너 클릭 실패', statusCode: 400 } satisfies APIError
  }
}

export const useBannerApi = () => {
  const qc = useQueryClient()
  type QueryOpts<T> = Omit<UseQueryOptions<T, APIError, T, any>, 'queryKey' | 'queryFn'>

  const useMainBanners = (
    options?: QueryOpts<BannerItem[]>
  ) => {
    return useQuery({
      queryKey: ['banners', 'public', 'main'],
      queryFn: () => bannerApi.listMain(),
      staleTime: 1000 * 60,
      ...options
    })
  }

  const useBannerClick = (
    options?: UseMutationOptions<void, APIError, number>
  ) => {
    return useMutation({
      mutationFn: (bannerId: number) => bannerApi.click(bannerId),
      onSuccess: () => {
        qc.invalidateQueries({ queryKey: ['banners', 'public', 'main'] })
      },
      ...options
    })
  }

  return { useMainBanners, useBannerClick }
}


