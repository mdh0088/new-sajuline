/**
 * 알림 대기(상담사 접속 알림) 전용 API 컴포저블
 */
import { useMutation, type UseMutationOptions } from '@tanstack/vue-query'
import { useNuxtApp } from 'nuxt/app'
import type { APIResponse, APIError } from '~/types/common/api'

interface NotificationWaitResponse {
  wait_idx: number
  user_id: string
  counselor_id: string
  is_send: boolean
  created_at: string
}

const notificationWaitApi = {
  async register(counselorId: string): Promise<NotificationWaitResponse> {
    const { $api } = useNuxtApp()
    const res = await $api<APIResponse<NotificationWaitResponse>>('/api/v1/notification-wait', {
      method: 'POST',
      body: { counselor_id: counselorId }
    })
    if (!res.success || !res.data) {
      throw new Error(res.error?.message || '알림 신청에 실패했습니다.')
    }
    return res.data
  }
}

export const useNotificationWaitQueries = () => {
  const useRegisterNotificationWait = (
    options?: UseMutationOptions<NotificationWaitResponse, APIError, string>
  ) => {
    return useMutation({
      mutationFn: (counselorId: string) => notificationWaitApi.register(counselorId),
      ...options
    })
  }

  return {
    useRegisterNotificationWait,
    registerNotificationWait: notificationWaitApi.register
  }
}
