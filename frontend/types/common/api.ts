/**
 * 공통 API 타입 정의
 * - 모든 API에서 사용하는 전역 타입
 * - Backend ResponseWrapper 기반
 */

/**
 * 페이지네이션 메타데이터
 * Backend: PaginationMeta 클래스
 */
export interface PaginationMeta {
  page: number              // 현재 페이지
  limit: number            // 페이지당 항목 수  
  total: number            // 전체 항목 수
  total_pages: number      // 전체 페이지 수
}

/**
 * 응답 메타데이터
 * Backend: ResponseMeta 클래스
 */
export interface ResponseMeta {
  timestamp: string                    // 응답 시간 (ISO string)
  request_id?: string                  // 요청 ID
  pagination?: PaginationMeta          // 페이지네이션 정보
}

/**
 * 에러 본문
 * Backend: ErrorBody 클래스  
 */
export interface ErrorBody {
  code: string                         // 에러 코드
  message: string                      // 에러 메시지
  details?: Record<string, any>        // 추가 상세 정보
}

/**
 * 표준 API 응답 형식
 * Backend: APIResponse[T] 클래스
 */
export interface APIResponse<T = any> {
  success: boolean                     // 성공 여부
  message?: string                     // 응답 메시지
  data?: T                            // 응답 데이터
  error?: ErrorBody                   // 에러 정보
  meta?: ResponseMeta                 // 메타데이터
}

/**
 * API 에러 타입 (프론트엔드 전용)
 */
export interface APIError {
  message: string
  statusCode: number
  data?: ErrorBody
}

/**
 * 페이지네이션 공통 결과 타입
 * - meta.pagination을 편히 쓰기 위한 전개형 구조
 */
export interface PaginatedResult<T> {
  items: T[]
  page: number
  limit: number
  total: number
  total_pages: number
}

/**
 * 페이지네이션 요청 파라미터
 */
export interface PaginationParams {
  page?: number
  size?: number
  limit?: number
}

/**
 * 정렬 파라미터
 */
export interface SortParams {
  sort_by?: string
  sort_order?: 'asc' | 'desc'
}

/**
 * 검색 파라미터
 */
export interface SearchParams {
  q?: string
  search?: string
}

/**
 * 공통 필터 파라미터
 */
export interface FilterParams extends PaginationParams, SortParams, SearchParams {
  [key: string]: any
}