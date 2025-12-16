export interface CounselorPublic {
  counselor_id: string
  counselor_code: string
  nickname: string
  profile_image_url?: string | null
  introduction_short?: string | null
  greeting_message?: string | null
  career_info?: string | null
  keywords?: string | null
  work_time?: string | null
  specialty_types?: string[] | null
  grade?: string | null
  after_amount?: number | null
  before_amount?: string | null
  rating_avg?: number | null
  consultation_count?: number | null
  m_state?: string | null // '1' 대기중, '2' 상담중, '3' 부재중
}





