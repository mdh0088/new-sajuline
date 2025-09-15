/**
 * 즐겨찾기(북마크) 전용 API 컴포저블
 */
import { useMutation, useQuery, useQueryClient, type UseMutationOptions, type UseQueryOptions } from '@tanstack/vue-query'
import { computed, unref, type Ref } from 'vue'
import { useNuxtApp } from 'nuxt/app'
import type { APIResponse, APIError } from '~/types/common/api'
import type { UserBookmarkItem } from '~/types/user/bookmark'

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

  const useCheckBookmark = (
    counselorId: string | Ref<string>,
    options?: Partial<UseQueryOptions<boolean, APIError>>
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
      },
      ...options
    })
  }

  return {
    useCheckBookmark,
    useAddBookmark,
    useRemoveBookmark,
    checkBookmark: bookmarkApi.check,
    addBookmark: bookmarkApi.add,
    removeBookmark: bookmarkApi.remove
  }
}


