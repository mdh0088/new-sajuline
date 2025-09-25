/**
 * 즐겨찾기(북마크) 전용 API 컴포저블
 */
import { useMutation, useQuery, useQueryClient, type UseMutationOptions, type UseQueryOptions } from '@tanstack/vue-query'
import { computed, unref, type Ref } from 'vue'
import { useNuxtApp } from 'nuxt/app'
import type { APIResponse, APIError, PaginatedResult } from '~/types/common/api'
import type { UserBookmarkItem } from '~/types/user/bookmark'
import type { CounselorSearchItem } from '~/types/counselor/search'

const bookmarkApi = {
  async check(counselorId: string): Promise<boolean> {
    const { $api } = useNuxtApp()
    const query = new URLSearchParams({ counselor_id: counselorId }).toString()
    const res = await $api<APIResponse<boolean>>(`/api/v1/users/bookmarks/check?${query}`, { method: 'GET' })
    if (!res.success) {
      throw new Error(res.error?.message || '즐겨찾기 여부 조회에 실패했습니다.')
    }
    return res.data ?? false
  },
  async add(counselorId: string): Promise<UserBookmarkItem> {
    const { $api } = useNuxtApp()
    const res = await $api<APIResponse<UserBookmarkItem>>(`/api/v1/users/bookmarks?counselor_id=${encodeURIComponent(counselorId)}`, {
      method: 'POST'
    })
    if (!res.success || !res.data) {
      throw new Error(res.error?.message || '즐겨찾기 등록에 실패했습니다.')
    }
    return res.data
  },
  async remove(counselorId: string): Promise<boolean> {
    const { $api } = useNuxtApp()
    const res = await $api<APIResponse<boolean>>(`/api/v1/users/bookmarks?counselor_id=${encodeURIComponent(counselorId)}`, {
      method: 'DELETE'
    })
    if (!res.success) {
      throw new Error(res.error?.message || '즐겨찾기 삭제에 실패했습니다.')
    }
    return res.data ?? false
  }
}

export const useBookmarkQueries = () => {
  const qc = useQueryClient()
  type QueryOpts<T> = Omit<UseQueryOptions<T, APIError, T, any>, 'queryKey' | 'queryFn'>

  const list = async (params: { page?: number; limit?: number } = {}): Promise<PaginatedResult<CounselorSearchItem>> => {
    const { $api } = useNuxtApp()
    const query = new URLSearchParams()
    query.set('page', String(params.page ?? 1))
    query.set('limit', String(params.limit ?? 20))
    const res = await $api<APIResponse<CounselorSearchItem[]>>(`/api/v1/users/bookmarks?${query.toString()}`, { method: 'GET' })
    if (!res.success) {
      throw new Error(res.error?.message || '즐겨찾기 목록을 불러오지 못했습니다.')
    }
    const p = res.meta?.pagination
    return {
      items: res.data ?? [],
      page: p?.page ?? (params.page ?? 1),
      limit: p?.limit ?? (params.limit ?? 20),
      total: p?.total ?? (res.data?.length ?? 0),
      total_pages: p?.total_pages ?? 1
    }
  }

  const useCheckBookmark = (
    counselorId: string | Ref<string>,
    options?: QueryOpts<boolean>
  ) => {
    const id = computed(() => String(unref(counselorId)))
    return useQuery({
      queryKey: computed(() => ['bookmark', 'check', id.value]),
      queryFn: () => bookmarkApi.check(id.value),
      enabled: computed(() => !!id.value),
      staleTime: 30 * 1000,
      ...options
    })
  }

  const useBookmarkList = (
    params: Ref<{ page?: number; limit?: number }> | { page?: number; limit?: number } = {},
    options?: QueryOpts<PaginatedResult<CounselorSearchItem>>
  ) => {
    const p = computed(() => unref(params) || {})
    return useQuery({
      queryKey: computed(() => ['bookmarks', 'list', p.value.page ?? 1, p.value.limit ?? 20]),
      queryFn: () => list({ page: p.value.page, limit: p.value.limit }),
      staleTime: 30 * 1000,
      ...options
    })
  }

  const useAddBookmark = (
    options?: UseMutationOptions<UserBookmarkItem, APIError, string>
  ) => {
    return useMutation({
      mutationFn: (counselorId: string) => bookmarkApi.add(counselorId),
      onSuccess: (_data, counselorId) => {
        qc.setQueryData(['bookmark', 'check', counselorId], true)
      },
      ...options
    })
  }

  const useRemoveBookmark = (
    options?: UseMutationOptions<boolean, APIError, string>
  ) => {
    return useMutation({
      mutationFn: (counselorId: string) => bookmarkApi.remove(counselorId),
      onSuccess: (_data, counselorId) => {
        qc.setQueryData(['bookmark', 'check', counselorId], false)
        qc.invalidateQueries({ queryKey: ['bookmarks'] })
      },
      ...options
    })
  }

  return {
    useCheckBookmark,
    useBookmarkList,
    useAddBookmark,
    useRemoveBookmark,
    list,
    checkBookmark: bookmarkApi.check,
    addBookmark: bookmarkApi.add,
    removeBookmark: bookmarkApi.remove
  }
}


