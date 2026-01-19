/**
 * 상담 후기 API
 * 백엔드 API: /api/v1/consultation-reviews
 */
import http from '@/api/_config/http';

const proxyURL = '/api/v1/consultation-reviews';

// API URL 상수
export const getReviewListURL = `${proxyURL}/list`;
export const getReviewDetailURL = `${proxyURL}`;
export const updateReviewURL = `${proxyURL}`;
export const createDummyReviewURL = `${proxyURL}`;

/**
 * 상담 후기 목록 조회 (페이징, 검색)
 */
export async function getReviewList(params: {
  page: number;
  limit: number;
  search_type?: string;
  search_name?: string;
  user_id?: string;
  counselor_id?: string;
  start_dt?: string;
  end_dt?: string;
}) {
  return http.get(getReviewListURL, { params });
}

/**
 * 상담 후기 상세 조회
 */
export async function getReviewDetail(review_id: number) {
  return http.get(`${getReviewDetailURL}/${review_id}`);
}

/**
 * 상담 후기 수정
 */
export async function updateReview(review_id: number, data: {
  content?: string;
  counselor_reply?: string;
  is_visible?: boolean;
  is_best?: boolean;
  rating?: number;
  review_tags?: string;
}) {
  return http.put(`${updateReviewURL}/${review_id}`, data);
}

/**
 * 더미 상담 후기 생성
 */
export async function createDummyReview(data: {
  user_id: string;
  user_nickname: string;
  counselor_id: string;
  rating: number;
  content?: string;
  counselor_reply?: string;
  review_tags?: string;
  is_visible?: boolean;
  is_best?: boolean;
}) {
  return http.post(createDummyReviewURL, data);
}
