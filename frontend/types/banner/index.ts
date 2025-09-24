// 배너 타입 정의

export type LinkTarget = 'SELF' | 'BLANK'

export interface BannerItem {
  banner_id: number
  banner_code: string
  banner_name: string
  banner_type: 'MAIN' | 'SUB' | 'POPUP'
  image_url: string
  mobile_image_url?: string | null
  link_url?: string | null
  link_target: LinkTarget
  display_order: number
  is_active: boolean
  valid_from: string
  valid_until: string
  click_count: number
  impression_count: number
  created_at: string
  updated_at?: string | null
}


