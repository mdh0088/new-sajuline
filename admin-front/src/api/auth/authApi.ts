import http from '@/api/_config/http';
import type { LoginRequest, LoginResponse, APIResponse } from '@/types/auth';

// admin-backend의 실제 라우팅 경로: /api/v1/auth
const AUTH_PREFIX = '/api/v1/auth';

/**
 * 관리자 로그인
 * - POST /auth/admin/login
 * - HttpOnly 쿠키로 access_token, refresh_token 자동 설정
 * @param loginData - 로그인 요청 데이터 (user_id, password)
 * @returns LoginResponse (user_id, email, nickname, token 만료 시간)
 */
export async function adminLogin(loginData: LoginRequest): Promise<APIResponse<LoginResponse>> {
  return http.post(`${AUTH_PREFIX}/admin/login`, loginData);
}

/**
 * 관리자 로그아웃
 * - POST /auth/admin/logout
 * - HttpOnly 쿠키의 토큰 삭제
 */
export async function adminLogout(): Promise<APIResponse<void>> {
  return http.post(`${AUTH_PREFIX}/admin/logout`);
}

/**
 * 상담사 로그인
 * - POST /auth/counselor/login
 * - HttpOnly 쿠키로 access_token, refresh_token 자동 설정
 */
export async function counselorLogin(loginData: LoginRequest): Promise<APIResponse<LoginResponse>> {
  return http.post(`${AUTH_PREFIX}/counselor/login`, loginData);
}

/**
 * 상담사 로그아웃
 * - POST /auth/counselor/logout
 * - HttpOnly 쿠키의 토큰 삭제
 */
export async function counselorLogout(): Promise<APIResponse<void>> {
  return http.post(`${AUTH_PREFIX}/counselor/logout`);
}
