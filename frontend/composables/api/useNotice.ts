/**
 * 공지사항 API 컴포저블 (게스트 공개)
 */
import { computed, unref, type Ref } from 'vue'
import { useQuery, useMutation, useQueryClient, type UseQueryOptions, type UseMutationOptions } from '@tanstack/vue-query'
import type { APIResponse } from '~/types/common/api'
import type { INoticeListItem, INoticeDetail, NoticeCategory } from '~/types/notice'
import { useNuxtApp } from 'nuxt/app'

// 백엔드 → 프론트엔드 매핑 헬퍼
const mapNoticeCategory = (notice_type: string, is_important?: boolean): NoticeCategory => {
  if (is_important) return 'important'
  switch (notice_type) {
    case 'UPDATE':
      return 'update'
    case 'EVENT':
      return 'event'
    default:
      return 'general'
  }
}

const formatDateYMD = (iso: string): string => {
  const d = new Date(iso)
  const yyyy = d.getFullYear()
  const mm = `${d.getMonth() + 1}`.padStart(2, '0')
  const dd = `${d.getDate()}`.padStart(2, '0')
  return `${yyyy}-${mm}-${dd}`
}

// API 호출 함수들
const noticeApi = {
  async list(): Promise<INoticeListItem[]> {
    const { $api } = useNuxtApp()
    const res = await $api<APIResponse<any[]>>('/api/v1/notices/public', { method: 'GET' })
    if (!res.success) throw new Error(res.error?.message || '공지 목록 조회 실패')
    const items = (res.data ?? []).map((n: any) => ({
      id: n.notice_id,
      title: n.title,
      summary: n.content?.length > 120 ? `${n.content.slice(0, 120)}…` : n.content,
      category: mapNoticeCategory(n.notice_type, n.is_important),
      viewCount: n.view_count ?? 0,
      createdAt: n.created_at
    })) as INoticeListItem[]
    return items
  },

  async detail(noticeId: number): Promise<INoticeDetail> {
    const { $api } = useNuxtApp()
    const res = await $api<APIResponse<any>>(`/api/v1/notices/${noticeId}`, { method: 'GET' })
    if (!res.success || !res.data) throw new Error(res.error?.message || '공지 상세 조회 실패')
    const n = res.data
    const detail: INoticeDetail = {
      id: n.notice_id,
      title: n.title,
      content: n.content,
      category: mapNoticeCategory(n.notice_type, n.is_important),
      viewCount: n.view_count ?? 0,
      createdAt: n.created_at,
      updatedAt: n.updated_at,
      isFixed: n.is_important ?? false,
      author: n.admin_name,
      prevNotice: n.before_notice_id ? { id: n.before_notice_id, title: '' } : null,
      nextNotice: n.after_notice_id ? { id: n.after_notice_id, title: '' } : null,
      before_notice_id: n.before_notice_id ?? null,
      after_notice_id: n.after_notice_id ?? null
    }
    return detail
  },

  async increaseView(noticeId: number): Promise<void> {
    const { $api } = useNuxtApp()
    const res = await $api<APIResponse<any>>(`/api/v1/notices/${noticeId}/views`, { method: 'POST' })
    if (!res.success) throw new Error(res.error?.message || '조회수 증가 실패')
  }
}

export const useNoticeApi = () => {
  const qc = useQueryClient()
  type QueryOpts<T> = Omit<UseQueryOptions<T, Error, T, any>, 'queryKey' | 'queryFn'>

  const useNoticeList = (
    options?: QueryOpts<INoticeListItem[]>
  ) => {
    return useQuery({
      queryKey: ['notices', 'public'],
      queryFn: () => noticeApi.list(),
      staleTime: 1000 * 30,
      ...options
    })
  }

  const useNoticeDetail = (
    noticeId: number | Ref<number>,
    options?: QueryOpts<INoticeDetail>
  ) => {
    const id = computed(() => Number(unref(noticeId)))
    return useQuery<INoticeDetail, Error, INoticeDetail, any>({
      queryKey: computed(() => ['notices', 'detail', id.value]),
      queryFn: () => noticeApi.detail(id.value),
      enabled: computed(() => !!id.value),
      staleTime: 0,
      ...options
    })
  }

  const useIncreaseView = (
    options?: UseMutationOptions<void, Error, number>
  ) => {
    return useMutation({
      mutationFn: (noticeId: number) => noticeApi.increaseView(noticeId),
      onSuccess: (_, noticeId) => {
        qc.invalidateQueries({ queryKey: ['notices', 'detail', noticeId] })
      },
      ...options
    })
  }

  return {
    useNoticeList,
    useNoticeDetail,
    useIncreaseView
  }
}


