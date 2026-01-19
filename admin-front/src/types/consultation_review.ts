/**
 * 상담 후기 타입 정의
 * 백엔드 API: /api/v1/consultation-reviews
 */

export interface ConsultationReviewItem {
  review_id: number;
  session_id: number;
  user_id: string;
  user_nickname: string | null;
  counselor_id: string;
  counselor_nickname: string | null;
  rating: number;
  content: string | null;
  counselor_reply: string | null;
  review_tags: string | null;
  is_best: boolean;
  is_visible: boolean;
  like_count: number;
  created_at: string;
  updated_at: string | null;
  counselor_replied_at: string | null;
}

export interface ConsultationReviewListResponse {
  items: ConsultationReviewItem[];
  page: number;
  limit: number;
  total: number;
}

export interface ConsultationReviewUpdateRequest {
  content?: string;
  counselor_reply?: string;
  is_visible?: boolean;
  is_best?: boolean;
  rating?: number;
  review_tags?: string;
}
