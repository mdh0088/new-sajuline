/**
 * 사용자 즐겨찾기(북마크) 타입 정의
 */
import type { APIResponse } from '~/types/common/api'

export interface UserBookmarkItem {
  bookmark_id: number
  user_id: string
  counselor_id: string
  created_at: string
}

export type UserBookmarkCreateResponse = APIResponse<UserBookmarkItem>
export type UserBookmarkDeleteResponse = APIResponse<boolean>
export type UserBookmarkCheckResponse = APIResponse<boolean>


