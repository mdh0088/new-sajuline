/**
 * 문의 관련 타입 정의
 */

export type InquiryType = 'PAY' | 'ACCOUNT' | 'CS' | 'EVENT' | 'ETC'

export interface InquiryCreateRequest {
  inquiry_type: InquiryType
  title?: string
  content: string
}

export interface InquiryItem {
  inquiry_id: number
  inquirer_type: string
  inquirer_id: string | null
  counselor_id: string | null
  category: string | null
  title: string | null
  content: string
  reply_content: string | null
  answered_at: string | null
  is_read: boolean
  has_reply: boolean
  created_at: string
  inquiry_type?: string
}

export interface InquiryDetail extends InquiryItem {
  updated_at: string | null
}

export interface InquiryListParams {
  page?: number
  limit?: number
  search?: string
}

export interface InquiryListResponse {
  items: InquiryItem[]
  total: number
  page: number
  limit: number
}

// inquiry_type 한글 변환 헬퍼
export const getInquiryTypeLabel = (type: string | undefined | null): string => {
  if (!type) return '기타'
  switch (type) {
    case 'PAY':
      return '결제문의'
    case 'ACCOUNT':
      return '계정문의'
    case 'CS':
      return '상담문의'
    case 'EVENT':
      return '이벤트문의'
    case 'ETC':
    default:
      return '기타문의'
  }
}

// 날짜 포맷 헬퍼
export const formatDate = (isoString: string): string => {
  const date = new Date(isoString)
  const yyyy = date.getFullYear()
  const mm = String(date.getMonth() + 1).padStart(2, '0')
  const dd = String(date.getDate()).padStart(2, '0')
  return `${yyyy}.${mm}.${dd}`
}
