/**
 * User API Service
 * 사용자 관련 API 서비스
 */

import { ApiClient } from '../client'
import { useAuthToken } from '~/utils/auth-token'
import type { 
  UpdateProfileRequest, 
  UsePointsRequest, 
  UpdateSettingsRequest 
} from '~/types/api/requests'
import type { 
  UserProfileResponse, 
  PointTransactionsResponse 
} from '~/types/api/responses'
import type { User, UserSettings, UserStats } from '~/types/models/user'

export class UserAPI {
  constructor(private client: ApiClient) {}

  /**
   * 사용자 프로필 조회
   */
  async getProfile(userId: string): Promise<UserProfileResponse> {
    const token = useAuthToken().getAccessToken()
    if (!token) {
      throw new Error('No access token available')
    }
    
    return this.client.get(`/api/v1/users/${userId}`, {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    })
  }

  /**
   * 사용자 프로필 업데이트
   */
  async updateProfile(userId: string, request: UpdateProfileRequest): Promise<User> {
    const token = useAuthToken().getAccessToken()
    if (!token) {
      throw new Error('No access token available')
    }
    
    return this.client.put(`/api/v1/users/${userId}`, request, {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    })
  }

  /**
   * 포인트 추가
   */
  async addPoints(userId: string, amount: number, description: string): Promise<{ new_balance: number }> {
    const token = useAuthToken().getAccessToken()
    if (!token) {
      throw new Error('No access token available')
    }
    
    return this.client.post(`/api/v1/users/${userId}/points/add`, {
      amount,
      description
    }, {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    })
  }

  /**
   * 포인트 사용
   */
  async usePoints(userId: string, request: UsePointsRequest): Promise<{ new_balance: number }> {
    const token = useAuthToken().getAccessToken()
    if (!token) {
      throw new Error('No access token available')
    }
    
    return this.client.post(`/api/v1/users/${userId}/points/use`, request, {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    })
  }

  /**
   * 포인트 거래 내역 조회
   */
  async getPointTransactions(
    userId: string, 
    page: number = 1, 
    pageSize: number = 20
  ): Promise<PointTransactionsResponse> {
    const token = useAuthToken().getAccessToken()
    if (!token) {
      throw new Error('No access token available')
    }
    
    const params = new URLSearchParams({
      page: page.toString(),
      page_size: pageSize.toString()
    })
    
    return this.client.get(`/api/v1/users/${userId}/points/transactions?${params}`, {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    })
  }

  /**
   * 사용자 설정 조회
   */
  async getSettings(userId: string): Promise<UserSettings> {
    const token = useAuthToken().getAccessToken()
    if (!token) {
      throw new Error('No access token available')
    }
    
    return this.client.get(`/api/v1/users/${userId}/settings`, {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    })
  }

  /**
   * 사용자 설정 업데이트
   */
  async updateSettings(userId: string, request: UpdateSettingsRequest): Promise<UserSettings> {
    const token = useAuthToken().getAccessToken()
    if (!token) {
      throw new Error('No access token available')
    }
    
    return this.client.put(`/api/v1/users/${userId}/settings`, request, {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    })
  }

  /**
   * 사용자 통계 조회
   */
  async getStats(userId: string): Promise<UserStats> {
    const token = useAuthToken().getAccessToken()
    if (!token) {
      throw new Error('No access token available')
    }
    
    return this.client.get(`/api/v1/users/${userId}/stats`, {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    })
  }

  /**
   * 계정 삭제
   */
  async deleteAccount(userId: string, reason?: string): Promise<void> {
    const token = useAuthToken().getAccessToken()
    if (!token) {
      throw new Error('No access token available')
    }
    
    return this.client.delete(`/api/v1/users/${userId}`, {
      headers: {
        'Authorization': `Bearer ${token}`
      },
      body: reason ? { reason } : undefined
    })
  }
}