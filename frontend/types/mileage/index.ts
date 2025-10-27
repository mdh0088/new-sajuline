/**
 * 마일리지 상품 관련 타입 정의
 */

/**
 * 마일리지 상품 정보
 * Backend: MileageProductResponse
 */
export interface MileageProduct {
  mileage_id: number
  m_product_name: string
  m_product_value: number
  charge_point: number
  m_product_img: string | null
  image_url: string | null
  valid_from: string | null
  valid_until: string | null
  ord: number
  tags: string | null
  description: string | null
  is_active: boolean
  created_at: string
  updated_at: string | null
}

/**
 * 마일리지 상품 구매 요청
 * Backend: MileagePurchaseRequest
 */
export interface MileagePurchaseRequest {
  mileage_id: number
}

/**
 * 마일리지 상품 구매 결과
 */
export interface MileagePurchaseResult {
  user_id: string
  mileage_id: number
  m_product_name: string
  deducted_mileage: number
  charged_point: number
  remaining_mileage: number
  new_point_balance: number
  transaction_id: number
}
