export interface CounselorSearchItem {
  counselor_id: string
  counselor_code: string
  nickname: string
  profile_image_url?: string | null
  introduction_short?: string | null
  specialty_types?: string[] | null
  keywords?: string | null
  after_amount?: number | null
  rating_avg?: number | null
  review_count: number
  m_state?: string | null // '1' 대기중, '2' 상담중, '3' 부재중
}

export interface CounselorSearchParams {
  page?: number
  limit?: number
  cs_status?: string | null
  is_best?: boolean | null
  is_new?: boolean | null
  cs_specialties?: string[] | null
  cs_keywords?: string[] | null
  search_name?: string | null
}



