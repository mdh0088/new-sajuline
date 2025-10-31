/**
 * 문의 API 컴포저블
 */
import { computed, unref, type Ref } from 'vue'
import { useQuery, useMutation, useQueryClient, type UseQueryOptions, type UseMutationOptions } from '@tanstack/vue-query'
import type { APIResponse } from '~/types/common/api'
import type { InquiryItem, InquiryDetail, InquiryCreateRequest, InquiryListParams } from '~/types/inquiry'
import { useNuxtApp } from 'nuxt/app'

// API 호출 함수들
const inquiryApi = {
  /**
   * 문의 목록 조회
   */
  async list(params: InquiryListParams = {}): Promise<{ items: InquiryItem[]; total: number }> {
    const { $api } = useNuxtApp()
    const queryParams = new URLSearchParams()

    if (params.page) queryParams.append('page', params.page.toString())
    if (params.limit) queryParams.append('limit', params.limit.toString())
    if (params.search) queryParams.append('search', params.search)

    const url = queryParams.toString()
      ? `/api/v1/users/inquiries?${queryParams}`
      : '/api/v1/users/inquiries'

    const res = await $api<APIResponse<InquiryItem[]>>(url, { method: 'GET' })

    if (!res.success) {
      throw new Error(res.error?.message || '문의 목록 조회 실패')
    }

    return {
      items: res.data || [],
      total: res.meta?.pagination?.total || 0
    }
  },

  /**
   * 문의 상세 조회
   */
  async detail(inquiryId: number): Promise<InquiryDetail> {
    const { $api } = useNuxtApp()
    const res = await $api<APIResponse<InquiryDetail>>(`/api/v1/users/inquiries/${inquiryId}`, {
      method: 'GET'
    })

    if (!res.success || !res.data) {
      throw new Error(res.error?.message || '문의 상세 조회 실패')
    }

    return res.data
  },

  /**
   * 문의 작성
   */
  async create(data: InquiryCreateRequest): Promise<InquiryDetail> {
    const { $api } = useNuxtApp()
    const res = await $api<APIResponse<InquiryDetail>>('/api/v1/users/inquiries', {
      method: 'POST',
      body: data
    })

    if (!res.success || !res.data) {
      throw new Error(res.error?.message || '문의 작성 실패')
    }

    return res.data
  }
}

export const useInquiryQueries = () => {
  const qc = useQueryClient()

  /**
   * 문의 목록 조회 (React Query)
   */
  const useInquiryList = (
    params: Ref<InquiryListParams> | InquiryListParams = {},
    options?: Omit<UseQueryOptions<{ items: InquiryItem[]; total: number }, Error>, 'queryKey' | 'queryFn'>
  ) => {
    const reactiveParams = computed(() => unref(params))

    return useQuery({
      queryKey: computed(() => ['inquiries', 'list', reactiveParams.value]),
      queryFn: () => inquiryApi.list(reactiveParams.value),
      staleTime: 1000 * 30, // 30초
      ...options
    })
  }

  /**
   * 문의 상세 조회 (React Query)
   */
  const useInquiryDetail = (
    inquiryId: Ref<number> | number,
    options?: Omit<UseQueryOptions<InquiryDetail, Error>, 'queryKey' | 'queryFn'>
  ) => {
    const id = computed(() => Number(unref(inquiryId)))

    return useQuery({
      queryKey: computed(() => ['inquiries', 'detail', id.value]),
      queryFn: () => inquiryApi.detail(id.value),
      enabled: computed(() => !!id.value && id.value > 0),
      staleTime: 0,
      ...options
    })
  }

  /**
   * 문의 작성 (Mutation)
   */
  const useCreateInquiry = (
    options?: UseMutationOptions<InquiryDetail, Error, InquiryCreateRequest>
  ) => {
    return useMutation({
      mutationFn: (data: InquiryCreateRequest) => inquiryApi.create(data),
      onSuccess: () => {
        // 목록 캐시 무효화
        qc.invalidateQueries({ queryKey: ['inquiries', 'list'] })
      },
      ...options
    })
  }

  return {
    useInquiryList,
    useInquiryDetail,
    useCreateInquiry
  }
}
