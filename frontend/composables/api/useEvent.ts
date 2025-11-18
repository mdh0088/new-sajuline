/**
 * 이벤트 API 컴포저블 (게스트 공개)
 */
import { computed, unref, type Ref } from 'vue'
import { useQuery, useMutation, useQueryClient, type UseQueryOptions, type UseMutationOptions } from '@tanstack/vue-query'
import type { APIResponse } from '~/types/common/api'

type EventStatus = 'ongoing' | 'completed' | 'upcoming'

export interface EventListItem {
  event_id: number
  event_name: string
  description?: string | null
  banner_image_url?: string | null
  is_active: boolean
  valid_from: string
  valid_until: string
  created_at: string
  event_metadata?: {
    display_type?: string
    card_config?: {
      rewards: number[]
      weights: number[]
      min_consultation_minutes: number
      chance_expiry_days: number
      reward_expiry_days: number
    }
  } | null
}

export interface EventDetail extends EventListItem {
  before_event_id: number | null
  after_event_id: number | null
}

const toStatus = (fromISO: string, untilISO: string): EventStatus => {
  const now = new Date()
  const from = new Date(fromISO)
  const until = new Date(untilISO)
  if (now < from) return 'upcoming'
  if (now > until) return 'completed'
  return 'ongoing'
}

const formatPeriod = (fromISO: string, untilISO: string): string => {
  const f = new Date(fromISO)
  const u = new Date(untilISO)
  const fY = f.getFullYear(), fM = String(f.getMonth() + 1).padStart(2, '0'), fD = String(f.getDate()).padStart(2, '0')
  const uY = u.getFullYear(), uM = String(u.getMonth() + 1).padStart(2, '0'), uD = String(u.getDate()).padStart(2, '0')
  return `${fY}.${fM}.${fD} ~ ${uY}.${uM}.${uD}`
}

export interface UIEventItem {
  id: number
  title: string
  description: string
  period: string
  status: EventStatus
  bannerImageUrl?: string | null
}

const eventApi = {
  async list(): Promise<UIEventItem[]> {
    const { $api } = useNuxtApp()
    const res = await $api<APIResponse<any[]>>('/api/v1/events/public', { method: 'GET' })
    if (!res.success) throw new Error(res.error?.message || '이벤트 목록 조회 실패')
    const rows = (res.data ?? []) as EventListItem[]
    return rows.map((e) => ({
      id: e.event_id,
      title: e.event_name,
      description: e.description ?? '',
      period: formatPeriod(e.valid_from, e.valid_until),
      status: toStatus(e.valid_from, e.valid_until),
      bannerImageUrl: e.banner_image_url ?? null,
    }))
  },

  async detail(eventId: number): Promise<EventDetail & { status: EventStatus; period: string }>{
    const { $api } = useNuxtApp()
    const res = await $api<APIResponse<any>>(`/api/v1/events/${eventId}`, { method: 'GET' })
    if (!res.success || !res.data) throw new Error(res.error?.message || '이벤트 상세 조회 실패')
    const e = res.data as EventDetail
    return {
      ...e,
      status: toStatus(e.valid_from, e.valid_until),
      period: formatPeriod(e.valid_from, e.valid_until)
    }
  }
}

export const useEventApi = () => {
  const qc = useQueryClient()
  type QueryOpts<T> = Omit<UseQueryOptions<T, Error, T, any>, 'queryKey' | 'queryFn'>

  const useEventList = (
    options?: QueryOpts<UIEventItem[]>
  ) => {
    return useQuery({
      queryKey: ['events', 'public'],
      queryFn: () => eventApi.list(),
      staleTime: 1000 * 30,
      ...options
    })
  }

  const useEventDetail = (
    eventId: number | Ref<number>,
    options?: QueryOpts<EventDetail & { status: EventStatus; period: string }>
  ) => {
    const id = computed(() => Number(unref(eventId)))
    return useQuery({
      queryKey: computed(() => ['events', 'detail', id.value]),
      queryFn: () => eventApi.detail(id.value),
      enabled: computed(() => !!id.value),
      staleTime: 5 * 60 * 1000, // 5분 캐시 (이벤트는 자주 변경되지 않음)
      ...options
    })
  }

  return { useEventList, useEventDetail }
}


