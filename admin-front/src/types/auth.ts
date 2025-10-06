// 로그인 요청 타입 (admin-backend LoginRequest 스키마와 일치)
export interface LoginRequest {
  user_id: string;
  password: string;
}

// 로그인 응답 타입 (admin-backend LoginResponse 스키마와 일치)
export interface LoginResponse {
  user_id: string;
  email: string;
  nickname: string;
  access_token_expires_in: number;  // 30분 (초 단위)
  refresh_token_expires_in: number; // 7일 (초 단위)
}

// 관리자 정보 타입 (store에 저장할 데이터)
export interface AdminInfo {
  user_id: string;
  email: string;
  nickname: string;
}

// API 응답 래퍼 타입
export interface APIResponse<T> {
  success: boolean;
  data?: T;
  message?: string;
  error?: {
    code: string;
    message: string;
  };
}
