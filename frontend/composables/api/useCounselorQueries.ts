/**
 * Vue Query 기반 상담사 API 컴포저블
 * - TanStack Query의 강력한 캐싱과 상태 관리 활용
 * - 상담사 도메인 특화 API 호출
 */
import { 
  useMutation, 
  useQueryClient,
  useQuery,
  type UseMutationOptions,
  type UseQueryOptions,
  type UseQueryReturnType
} from '@tanstack/vue-query'
import { computed, unref, type Ref } from 'vue'
import type { 
  LoginRequest,
  LoginData,
  LoginResponse,
  LogoutResponse
} from '~/types/user/models'
import type { APIResponse, APIError, PaginatedResult } from '~/types/common/api'
import type { NoticeListItem } from '~/types/counselor/notice'
import type { ReviewSummary } from '~/types/counselor/review'
import type { InquirySummary, CounselorMypageUpdatePayload } from '~/types/counselor/inquiry'
import type { CounselorPublic } from '~/types/counselor/detail'
import type { CounselorSearchItem, CounselorSearchParams } from '~/types/counselor/search'
import { useNuxtApp } from 'nuxt/app'

// 타입은 counselor 전용 디렉터리에서 관리합니다.

/**
 * 상담사 API 호출 함수들 (Vue Query에서 사용)
 */
const counselorApi = {
  // 상담사 로그인
  async login(credentials: LoginRequest): Promise<LoginData> {
    const { $api } = useNuxtApp()
    console.log('🔍 [counselorApi.login] Calling API with credentials:', { user_id: credentials.user_id })

    const response = await $api<LoginResponse>('/api/v1/counselors/login', {
      method: 'POST',
      body: credentials
    })

    console.log('🔍 [counselorApi.login] API response received:', response)
    console.log('🔍 [counselorApi.login] Response success:', response.success)
    console.log('🔍 [counselorApi.login] Response data:', response.data)

    if (!response.success || !response.data) {
      console.error('❌ [counselorApi.login] Response validation failed:', { success: response.success, hasData: !!response.data })
      throw new Error(response.error?.message || '상담사 로그인에 실패했습니다.')
    }

    console.log('✅ [counselorApi.login] Returning data:', response.data)
    return response.data
  },

  // 공개: 상담사 상세 (code로 조회)
  async getPublicDetail(counselorCode: string): Promise<CounselorPublic> {
    const { $api } = useNuxtApp()
    const response = await $api<APIResponse<CounselorPublic>>(`/api/v1/counselors/public/${encodeURIComponent(counselorCode)}`, { method: 'GET' })
    if (!response.success || !response.data) {
      throw new Error(response.error?.message || '상담사 정보를 불러오지 못했습니다.')
    }
    return response.data
  },

  // 공개: 상담사 검색 목록 (게스트)
  async searchPublic(params: CounselorSearchParams): Promise<PaginatedResult<CounselorSearchItem>> {
    const { $api } = useNuxtApp()
    const query = new URLSearchParams()
    query.set('page', String(params.page ?? 1))
    query.set('limit', String(params.limit ?? 10))
    if (params.cs_status) query.set('cs_status', String(params.cs_status))
    if (params.is_best !== undefined && params.is_best !== null) query.set('is_best', String(params.is_best))
    if (params.is_new !== undefined && params.is_new !== null) query.set('is_new', String(params.is_new))
    if (params.search_name) query.set('search_name', params.search_name)
    // 배열 파라미터는 다중 키로 전달
    for (const v of params.cs_specialties || []) query.append('cs_specialties', v)
    for (const v of params.cs_keywords || []) query.append('cs_keywords', v)

    const response = await $api<APIResponse<CounselorSearchItem[]>>(`/api/v1/counselors/public/search?${query.toString()}`, { method: 'GET' })
    if (!response.success) {
      throw new Error(response.error?.message || '상담사 목록을 불러오지 못했습니다.')
    }
    const pagination = response.meta?.pagination
    return {
      items: response.data ?? [],
      page: pagination?.page ?? (params.page ?? 1),
      limit: pagination?.limit ?? (params.limit ?? 10),
      total: pagination?.total ?? (response.data?.length ?? 0),
      total_pages: pagination?.total_pages ?? 1
    }
  },

  // 상담사 로그아웃
  async logout(): Promise<void> {
    const { $api } = useNuxtApp()
    const response = await $api<LogoutResponse>('/api/v1/counselors/logout', {
      method: 'POST'
    })
    
    if (!response.success) {
      throw new Error(response.error?.message || '상담사 로그아웃에 실패했습니다.')
    }
  },

  // 상담사 마이페이지 정보 조회
  async getMypage() {
    const { $api } = useNuxtApp()
    const response = await $api<APIResponse<any>>('/api/v1/counselors/mypage', {
      method: 'GET'
    })
    if (!response.success || !response.data) {
      throw new Error(response.error?.message || '마이페이지 정보를 가져오지 못했습니다.')
    }
    return response.data
  },

  // 월간 상담시간/포인트 합계 조회
  async getMonthlyConsultationStats(params: { yyyy: string; mm: string }) {
    const { $api } = useNuxtApp()
    const search = new URLSearchParams({ yyyy: params.yyyy, mm: params.mm }).toString()
    const response = await $api<APIResponse<{ m_code: string; yyyy: string; mm: string; sum_realchattm: number; sum_usepoint: number }>>(`/api/v1/counselors/consultation-time?${search}`, {
      method: 'GET'
    })
    if (!response.success || !response.data) {
      throw new Error(response.error?.message || '월간 상담 통계를 가져오지 못했습니다.')
    }
    return response.data
  },

  // 상담사 마이페이지 부분 업데이트
  async updateMypage(payload: CounselorMypageUpdatePayload) {
    const { $api } = useNuxtApp()
    const response = await $api<APIResponse<any>>('/api/v1/counselors/mypage', {
      method: 'PATCH',
      body: payload
    })
    if (!response.success || !response.data) {
      throw new Error(response.error?.message || '마이페이지 변경에 실패했습니다.')
    }
    return response.data
  },

  // 공지사항 목록 (상담사 대상)
  async getNoticeList(params: { page?: number; limit?: number; notice_type?: string; target_audience?: string; is_active?: boolean; is_important?: boolean; search?: string }): Promise<PaginatedResult<NoticeListItem>> {
    const { $api } = useNuxtApp()
    const query = new URLSearchParams()
    query.set('page', String(params.page ?? 1))
    query.set('limit', String(params.limit ?? 10))
    // 기본적으로 상담사 대상, 활성 공지
    query.set('target_audience', String(params.target_audience ?? 'COUNSELOR'))
    if (params.notice_type) query.set('notice_type', params.notice_type)
    if (params.is_active ?? true) query.set('is_active', String(params.is_active ?? true))
    if (params.is_important !== undefined) query.set('is_important', String(params.is_important))
    if (params.search) query.set('search', params.search)

    const response = await $api<APIResponse<NoticeListItem[]>>(`/api/v1/notices/?${query.toString()}`, { method: 'GET' })
    if (!response.success) {
      throw new Error(response.error?.message || '공지사항을 불러오지 못했습니다.')
    }
    const pagination = response.meta?.pagination
    return {
      items: response.data ?? [],
      page: pagination?.page ?? (params.page ?? 1),
      limit: pagination?.limit ?? (params.limit ?? 10),
      total: pagination?.total ?? (response.data?.length ?? 0),
      total_pages: pagination?.total_pages ?? 1
    }
  },

  // 상담사 후기 목록 (로그인 상담사 전용)
  async getCounselorReviews(params: { page?: number; limit?: number; visible_only?: boolean }): Promise<PaginatedResult<ReviewSummary>> {
    const { $api } = useNuxtApp()
    const query = new URLSearchParams()
    query.set('page', String(params.page ?? 1))
    query.set('limit', String(params.limit ?? 20))
    if (params.visible_only !== undefined) query.set('visible_only', String(params.visible_only))
    const response = await $api<APIResponse<ReviewSummary[]>>(`/api/v1/counselors/inquiries/reviews?${query.toString()}`, { method: 'GET' })
    if (!response.success) {
      throw new Error(response.error?.message || '고객 후기를 불러오지 못했습니다.')
    }
    const pagination = response.meta?.pagination
    return {
      items: response.data ?? [],
      page: pagination?.page ?? (params.page ?? 1),
      limit: pagination?.limit ?? (params.limit ?? 20),
      total: pagination?.total ?? (response.data?.length ?? 0),
      total_pages: pagination?.total_pages ?? 1
    }
  },

  // 상담문의 목록 (사용자 → 상담사, 로그인 상담사 전용)
  async getCounselorUserInquiries(params: { page?: number; limit?: number }): Promise<PaginatedResult<InquirySummary>> {
    const { $api } = useNuxtApp()
    const query = new URLSearchParams()
    query.set('page', String(params.page ?? 1))
    query.set('limit', String(params.limit ?? 20))
    const response = await $api<APIResponse<InquirySummary[]>>(`/api/v1/counselors/inquiries/users?${query.toString()}`, { method: 'GET' })
    if (!response.success) {
      throw new Error(response.error?.message || '상담문의를 불러오지 못했습니다.')
    }
    const pagination = response.meta?.pagination
    return {
      items: response.data ?? [],
      page: pagination?.page ?? (params.page ?? 1),
      limit: pagination?.limit ?? (params.limit ?? 20),
      total: pagination?.total ?? (response.data?.length ?? 0),
      total_pages: pagination?.total_pages ?? 1
    }
  },

  // 사용자 → 상담사 문의 생성 (로그인 사용자)
  async createUserInquiry(payload: { counselor_id: string; content: string; category?: string; title?: string }) {
    const { $api } = useNuxtApp()
    const response = await $api<APIResponse<any>>(`/api/v1/users/inquiries/counselor`, {
      method: 'POST',
      body: {
        counselor_id: payload.counselor_id,
        content: payload.content,
        category: payload.category,
        title: payload.title
      }
    })
    if (!response.success || !response.data) {
      throw new Error(response.error?.message || '문의 등록에 실패했습니다.')
    }
    return response.data
  },

  // 공개: 상담사 후기 목록 (게스트)
  async getPublicCounselorReviews(params: { counselor_id: string; page?: number; limit?: number; visible_only?: boolean }): Promise<PaginatedResult<ReviewSummary>> {
    const { $api } = useNuxtApp()
    const query = new URLSearchParams()
    query.set('page', String(params.page ?? 1))
    query.set('limit', String(params.limit ?? 20))
    if (params.visible_only !== undefined) query.set('visible_only', String(params.visible_only))
    const response = await $api<APIResponse<ReviewSummary[]>>(`/api/v1/counselors/public/${encodeURIComponent(params.counselor_id)}/reviews?${query.toString()}`, { method: 'GET' })
    if (!response.success) {
      throw new Error(response.error?.message || '고객 후기를 불러오지 못했습니다.')
    }
    const pagination = response.meta?.pagination
    return {
      items: response.data ?? [],
      page: pagination?.page ?? (params.page ?? 1),
      limit: pagination?.limit ?? (params.limit ?? 20),
      total: pagination?.total ?? (response.data?.length ?? 0),
      total_pages: pagination?.total_pages ?? 1
    }
  },

  // 공개: 상담문의 목록 (게스트)
  async getPublicCounselorUserInquiries(params: { counselor_id: string; page?: number; limit?: number }): Promise<PaginatedResult<InquirySummary>> {
    const { $api } = useNuxtApp()
    const query = new URLSearchParams()
    query.set('page', String(params.page ?? 1))
    query.set('limit', String(params.limit ?? 20))
    const response = await $api<APIResponse<InquirySummary[]>>(`/api/v1/counselors/public/${encodeURIComponent(params.counselor_id)}/inquiries?${query.toString()}`, { method: 'GET' })
    if (!response.success) {
      throw new Error(response.error?.message || '상담문의를 불러오지 못했습니다.')
    }
    const pagination = response.meta?.pagination
    return {
      items: response.data ?? [],
      page: pagination?.page ?? (params.page ?? 1),
      limit: pagination?.limit ?? (params.limit ?? 20),
      total: pagination?.total ?? (response.data?.length ?? 0),
      total_pages: pagination?.total_pages ?? 1
    }
  },

  // 관리자문의 목록 (상담사 → 관리자)
  async getCounselorAdminInquiries(params: { page?: number; limit?: number }): Promise<PaginatedResult<InquirySummary>> {
    const { $api } = useNuxtApp()
    const query = new URLSearchParams()
    query.set('page', String(params.page ?? 1))
    query.set('limit', String(params.limit ?? 20))

    const response = await $api<APIResponse<InquirySummary[]>>(`/api/v1/counselors/inquiries/admin?${query.toString()}`, { method: 'GET' })
    if (!response.success) {
      throw new Error(response.error?.message || '관리자문의를 불러오지 못했습니다.')
    }
    const pagination = response.meta?.pagination
    return {
      items: response.data ?? [],
      page: pagination?.page ?? (params.page ?? 1),
      limit: pagination?.limit ?? (params.limit ?? 20),
      total: pagination?.total ?? (response.data?.length ?? 0),
      total_pages: pagination?.total_pages ?? 1
    }
  },

  // 후기 개수만 조회 (최적화)
  async getCounselorReviewsCount(params: { visible_only?: boolean }): Promise<number> {
    const { $api } = useNuxtApp()
    const query = new URLSearchParams()
    if (params.visible_only !== undefined) query.set('visible_only', String(params.visible_only))
    const response = await $api<APIResponse<{ count: number }>>(`/api/v1/counselors/inquiries/reviews/count?${query.toString()}`, { method: 'GET' })
    if (!response.success || !response.data) {
      throw new Error(response.error?.message || '후기 개수를 불러오지 못했습니다.')
    }
    return response.data.count
  },

  // 상담문의 개수만 조회 (최적화)
  async getCounselorUserInquiriesCount(): Promise<number> {
    const { $api } = useNuxtApp()
    const response = await $api<APIResponse<{ count: number }>>('/api/v1/counselors/inquiries/users/count', { method: 'GET' })
    if (!response.success || !response.data) {
      throw new Error(response.error?.message || '상담문의 개수를 불러오지 못했습니다.')
    }
    return response.data.count
  },

  // 관리자문의 개수만 조회 (최적화)
  async getCounselorAdminInquiriesCount(): Promise<number> {
    const { $api } = useNuxtApp()
    const response = await $api<APIResponse<{ count: number }>>('/api/v1/counselors/inquiries/admin/count', { method: 'GET' })
    if (!response.success || !response.data) {
      throw new Error(response.error?.message || '관리자문의 개수를 불러오지 못했습니다.')
    }
    return response.data.count
  },

  // 상담문의 답변 작성
  async replyToUserInquiry(inquiryId: number, replyContent: string): Promise<any> {
    const { $api } = useNuxtApp()
    const response = await $api<APIResponse<any>>(`/api/v1/counselors/inquiries/users/${inquiryId}/reply`, {
      method: 'POST',
      body: { reply_content: replyContent }
    })
    if (!response.success || !response.data) {
      throw new Error(response.error?.message || '답변 등록에 실패했습니다.')
    }
    return response.data
  },

  // 고객 후기 답변 작성
  async replyToReview(reviewId: number, replyContent: string): Promise<any> {
    const { $api } = useNuxtApp()
    const response = await $api<APIResponse<any>>(`/api/v1/counselors/inquiries/reviews/${reviewId}/reply`, {
      method: 'POST',
      body: { counselor_reply: replyContent }
    })
    if (!response.success || !response.data) {
      throw new Error(response.error?.message || '답변 등록에 실패했습니다.')
    }
    return response.data
  },

  // 관리자 문의 작성
  async createCounselorAdminInquiry(payload: { inquiry_type: string; title?: string; content: string }): Promise<any> {
    const { $api } = useNuxtApp()
    const response = await $api<APIResponse<any>>('/api/v1/counselors/inquiries/admin', {
      method: 'POST',
      body: payload
    })
    if (!response.success || !response.data) {
      throw new Error(response.error?.message || '관리자 문의 등록에 실패했습니다.')
    }
    return response.data
  }
}

/**
 * Vue Query 기반 상담사 API 훅들
 */
export const useCounselorQueries = () => {
  const queryClient = useQueryClient()
  // 사용자 옵션 타입: 내부에서 queryKey/queryFn을 설정하므로 외부 옵션에서는 제외
  type QueryOpts<T> = Omit<UseQueryOptions<T, APIError, T, any>, 'queryKey' | 'queryFn'>

  // 상담사 로그인 뮤테이션
  const useLogin = (
    options?: UseMutationOptions<LoginData, APIError, LoginRequest>
  ) => {
    return useMutation({
      mutationFn: counselorApi.login,
      onSuccess: (data) => {
        // 로그인 성공 시 상담사 관련 쿼리들 무효화 (최신 정보 로드)
        queryClient.invalidateQueries({ queryKey: ['counselor'] })
      },
      ...options
    })
  }

  // 상담사 로그아웃 뮤테이션  
  const useLogout = (
    options?: UseMutationOptions<void, APIError, void>
  ) => {
    return useMutation({
      mutationFn: counselorApi.logout,
      onSuccess: () => {
        // 로그아웃 시 모든 상담사 관련 캐시 클리어
        queryClient.removeQueries({ queryKey: ['counselor'] })
      },
      ...options
    })
  }

  // 상담사 마이페이지 조회 쿼리
  const useMypage = (
    options?: QueryOpts<any>
  ) => {
    return useQuery({
      queryKey: ['counselor', 'mypage'],
      queryFn: counselorApi.getMypage,
      staleTime: 1000 * 60, // 1분
      ...options
    })
  }

  // 월간 상담시간/포인트 합계 쿼리
  const useMonthlyConsultationStats = (
    yyyy: string | Ref<string>,
    mm: string | Ref<string>,
    options?: UseQueryOptions<any, APIError, any>
  ) => {
    return useQuery({
      queryKey: computed(() => ['counselor', 'consultation-time', unref(yyyy), unref(mm)]),
      queryFn: () => counselorApi.getMonthlyConsultationStats({ yyyy: String(unref(yyyy)), mm: String(unref(mm)) }),
      staleTime: 1000 * 60, // 1분
      ...options
    })
  }

  // 공개: 상담사 검색 목록 쿼리
  const usePublicSearch = (
    params: Ref<CounselorSearchParams> | CounselorSearchParams,
    options?: QueryOpts<PaginatedResult<CounselorSearchItem>>
  ) => {
    const p = computed(() => unref(params))
    return useQuery({
      queryKey: computed(() => ['counselor', 'public', 'search',
        p.value.page ?? 1,
        p.value.limit ?? 10,
        p.value.cs_status ?? '',
        String(p.value.is_best ?? ''),
        String(p.value.is_new ?? ''),
        (p.value.cs_specialties || []).join(','),
        (p.value.cs_keywords || []).join(','),
        p.value.search_name ?? ''
      ]),
      queryFn: () => counselorApi.searchPublic(p.value),
      staleTime: 1000 * 30,
      ...options
    })
  }

  // 상담사 마이페이지 업데이트 뮤테이션
  const useUpdateMypage = (
    options?: UseMutationOptions<any, APIError, CounselorMypageUpdatePayload>
  ) => {
    return useMutation({
      mutationFn: counselorApi.updateMypage,
      onSuccess: () => {
        // 업데이트 후 최신 정보로 갱신
        queryClient.invalidateQueries({ queryKey: ['counselor', 'mypage'] })
      },
      ...options
    })
  }

  // 공지사항 목록 쿼리
  const useNoticeList = (
    page: number | Ref<number> = 1,
    limit: number | Ref<number> = 10,
    filters?: { notice_type?: string; target_audience?: string; is_active?: boolean; is_important?: boolean; search?: string },
    options?: QueryOpts<PaginatedResult<NoticeListItem>>
  ) => {
    const p = computed(() => Number(unref(page)))
    const l = computed(() => Number(unref(limit)))
    return useQuery({
      queryKey: computed(() => ['notices', p.value, l.value, filters?.notice_type ?? '', filters?.target_audience ?? 'COUNSELOR', String(filters?.is_active ?? true), String(filters?.is_important ?? ''), filters?.search ?? '']),
      queryFn: () => counselorApi.getNoticeList({ page: p.value, limit: l.value, ...filters }),
      staleTime: 1000 * 60,
      ...options
    })
  }

  // 고객 후기 목록 쿼리 (로그인 상담사)
  const useCounselorReviews = (
    page: number | Ref<number> = 1,
    limit: number | Ref<number> = 20,
    visibleOnly: boolean | Ref<boolean> = true,
    options?: QueryOpts<PaginatedResult<ReviewSummary>>
  ) => {
    const p = computed(() => Number(unref(page)))
    const l = computed(() => Number(unref(limit)))
    const v = computed(() => Boolean(unref(visibleOnly)))
    return useQuery({
      queryKey: computed(() => ['counselor', 'reviews', p.value, l.value, v.value]),
      queryFn: () => counselorApi.getCounselorReviews({ page: p.value, limit: l.value, visible_only: v.value }),
      staleTime: 1000 * 60,
      ...options
    })
  }

  // 상담문의 목록 쿼리 (사용자→상담사)
  // 상담문의 목록 쿼리 (사용자→상담사, 로그인 상담사)
  const useCounselorUserInquiries = (
    page: number | Ref<number> = 1,
    limit: number | Ref<number> = 20,
    options?: QueryOpts<PaginatedResult<InquirySummary>>
  ) => {
    const p = computed(() => Number(unref(page)))
    const l = computed(() => Number(unref(limit)))
    return useQuery({
      queryKey: computed(() => ['counselor', 'inquiries', 'users', p.value, l.value]),
      queryFn: () => counselorApi.getCounselorUserInquiries({ page: p.value, limit: l.value }),
      staleTime: 1000 * 60,
      ...options
    })
  }

  // 공개: 상담사 상세 쿼리
  const usePublicDetail = (
    counselorCode: string | Ref<string>,
    options?: UseQueryOptions<CounselorPublic, APIError, CounselorPublic>
  ) => {
    const code = computed(() => String(unref(counselorCode)))
    return useQuery<CounselorPublic, APIError, CounselorPublic, any>({
      queryKey: computed(() => ['counselor', 'public', code.value]),
      queryFn: () => counselorApi.getPublicDetail(code.value),
      staleTime: 1000 * 60,
      ...options
    })
  }

  // 관리자문의 목록 쿼리 (상담사→관리자)
  const useCounselorAdminInquiries = (
    page: number | Ref<number> = 1,
    limit: number | Ref<number> = 20,
    options?: QueryOpts<PaginatedResult<InquirySummary>>
  ) => {
    const p = computed(() => Number(unref(page)))
    const l = computed(() => Number(unref(limit)))
    return useQuery({
      queryKey: computed(() => ['counselor', 'inquiries', 'admin', p.value, l.value]),
      queryFn: () => counselorApi.getCounselorAdminInquiries({ page: p.value, limit: l.value }),
      staleTime: 1000 * 60,
      ...options
    })
  }

  // 후기 개수 쿼리 (최적화)
  const useCounselorReviewsCount = (
    visibleOnly: boolean | Ref<boolean> = true,
    options?: QueryOpts<number>
  ) => {
    const v = computed(() => Boolean(unref(visibleOnly)))
    return useQuery({
      queryKey: computed(() => ['counselor', 'reviews', 'count', v.value]),
      queryFn: () => counselorApi.getCounselorReviewsCount({ visible_only: v.value }),
      staleTime: 1000 * 60,
      ...options
    })
  }

  // 상담문의 개수 쿼리 (최적화)
  const useCounselorUserInquiriesCount = (
    options?: QueryOpts<number>
  ) => {
    return useQuery({
      queryKey: ['counselor', 'inquiries', 'users', 'count'],
      queryFn: () => counselorApi.getCounselorUserInquiriesCount(),
      staleTime: 1000 * 60,
      ...options
    })
  }

  // 관리자문의 개수 쿼리 (최적화)
  const useCounselorAdminInquiriesCount = (
    options?: QueryOpts<number>
  ) => {
    return useQuery({
      queryKey: ['counselor', 'inquiries', 'admin', 'count'],
      queryFn: () => counselorApi.getCounselorAdminInquiriesCount(),
      staleTime: 1000 * 60,
      ...options
    })
  }

  return {
    // Mutations
    useLogin,
    useLogout,
    useUpdateMypage,
    // Queries
    useMypage,
    useMonthlyConsultationStats,
    useNoticeList,
    useCounselorReviews,
    useCounselorUserInquiries,
    useCounselorAdminInquiries,
    useCounselorReviewsCount,
    useCounselorUserInquiriesCount,
    useCounselorAdminInquiriesCount,
    usePublicDetail,
    usePublicSearch,
    searchPublic: counselorApi.searchPublic,
    getPublicCounselorReviews: counselorApi.getPublicCounselorReviews,
    getPublicCounselorUserInquiries: counselorApi.getPublicCounselorUserInquiries,
    createUserInquiry: counselorApi.createUserInquiry,
    replyToUserInquiry: counselorApi.replyToUserInquiry,
    replyToReview: counselorApi.replyToReview,
    createCounselorAdminInquiry: counselorApi.createCounselorAdminInquiry
  }
}