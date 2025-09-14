export interface ReviewSummary {
  review_id: number
  user_id: string
  counselor_id: string
  rating: number
  content?: string | null
  counselor_reply?: string | null
  counselor_replied_at?: string | null
  is_best: boolean
  like_count: number
  created_at: string
  has_reply: boolean
}


