import { useNuxtApp } from 'nuxt/app'

type ApiResponse<T> = {
  success: boolean
  message?: string
  data?: T
  error?: { code: string; message: string }
}

type PayletterRequestResponse = {
  token: string
  online_url?: string
  mobile_url?: string
}

export const usePaymentApi = () => {
  const { $api } = useNuxtApp()

  const requestPayment = async (product_id: number, payment_method: string) => {
    const res = await $api<ApiResponse<PayletterRequestResponse>>('/api/v1/payment/request', {
      method: 'POST',
      body: { product_id, payment_method }
    })
    if (!res.success || !res.data) throw new Error(res.error?.message || '결제 요청 실패')
    return res.data
  }

  return { requestPayment }
}


