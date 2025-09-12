export type InquirerType = 'USER' | 'COUNSELOR' | 'GUEST'

export interface InquirySummary {
  inquiry_id: number
  inquirer_type: InquirerType
  inquirer_id?: string | null
  counselor_id?: string | null
  category?: string | null
  title?: string | null
  is_read: boolean
  has_reply: boolean
  created_at: string
}

export type CounselorStatus = 'WAITING' | 'CONSULTING' | 'ABSENT'

export type CounselorMypageUpdatePayload = Partial<{
  counselor_status: CounselorStatus
  work_time: string
  introduction_short: string
  greeting_message: string
  career_info: string
}>


