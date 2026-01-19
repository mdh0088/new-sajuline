/**
 * Counselor API Service
 * 상담사 관련 API 서비스
 */

import { ApiClient } from '../client'
import { useAuthToken } from '~/utils/auth-token'
import type { 
  CounselorLoginRequest, 
  UpdateCounselorStatusRequest 
} from '~/types/api/requests'
import type { 
  CounselorLoginResponse, 
  CounselorListResponse 
} from '~/types/api/responses'
import type { Counselor } from '~/types/models/counselor'

export class CounselorAPI {
  constructor(private client: ApiClient) {}

  /**
   * 상담사 로그인
   */
  async login(request: CounselorLoginRequest): Promise<CounselorLoginResponse> {
    return this.client.post('/api/v1/auth/counselor/login', request)
  }

  /**
   * 상담사 정보 조회
   */
  async getProfile(): Promise<Counselor> {
    const token = useAuthToken().getAccessToken()
    if (!token) {
      throw new Error('No access token available')
    }
    
    return this.client.get('/api/v1/auth/counselor/me', {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    })
  }

  /**
   * 상담사 로그아웃
   */
  async logout(): Promise<void> {
    const token = useAuthToken().getAccessToken()
    if (!token) return
    
    return this.client.post('/api/v1/auth/counselor/logout', null, {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    })
  }

  /**
   * 상담사 상태 업데이트
   */
  async updateStatus(status: number): Promise<void> {
    const token = useAuthToken().getAccessToken()
    if (!token) {
      throw new Error('No access token available')
    }
    
    return this.client.patch('/api/v1/auth/counselor/status', 
      { counselor_status: status },
      {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      }
    )
  }

  /**
   * 상담사 목록 조회
   */
  async getList(
    page: number = 1, 
    pageSize: number = 20,
    filters?: {
      specialty?: string
      is_online?: boolean
      search?: string
    }
  ): Promise<CounselorListResponse> {
    const params = new URLSearchParams({
      page: page.toString(),
      page_size: pageSize.toString()
    })
    
    if (filters?.specialty) params.append('specialty', filters.specialty)
    if (filters?.is_online !== undefined) params.append('is_online', filters.is_online.toString())
    if (filters?.search) params.append('search', filters.search)
    
    return this.client.get(`/api/v1/counselors?${params}`)
  }

  /**
   * 특정 상담사 정보 조회
   */
  async getCounselor(counselorId: string): Promise<Counselor> {
    return this.client.get(`/api/v1/counselors/${counselorId}`)
  }

  /**
   * 상담사 전문 분야 목록 조회
   */
  async getSpecialties(): Promise<Array<{ id: string; name: string; category: string }>> {
    return this.client.get('/api/v1/counselors/specialties')
  }

  /**
   * 온라인 상담사 수 조회
   */
  async getOnlineCount(): Promise<{ count: number }> {
    return this.client.get('/api/v1/counselors/online/count')
  }
}

// Lazy singleton pattern for safer initialization
let _counselorAPI: CounselorAPI | null = null

export function getCounselorAPI(): CounselorAPI {
  if (!_counselorAPI) {
    _counselorAPI = new CounselorAPI(new ApiClient())
  }
  return _counselorAPI
}

// Default export with getter for backward compatibility
export const counselorAPI = new Proxy({} as CounselorAPI, {
  get(target, prop) {
    return getCounselorAPI()[prop as keyof CounselorAPI]
  }
})