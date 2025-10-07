/**
 * 마일리지 상품 타입 정의 (새 백엔드 API 규격)
 * 백엔드 API: /api/v1/mileage
 */

export interface MileageProductItem {
    mileage_id: number;
    m_product_name: string;
    m_product_value: number;
    charge_point: number;
    m_product_img: string;
    image_url: string;
    valid_from: string;
    valid_until: string;
    ord: number;
    is_active: boolean;
    description: string | null;
    created_at: string;
    updated_at: string | null;
}

export interface MileageProductListResponse {
    items: MileageProductItem[];
    total: number;
}

export interface MileageProductCreateRequest {
    m_product_name: string;
    m_product_value: number;
    charge_point: number;
    valid_from: string;
    valid_until: string;
    ord?: number;
    description?: string;
    is_active?: boolean;
    image?: File;
}

export interface MileageProductUpdateRequest {
    m_product_name?: string;
    m_product_value?: number;
    charge_point?: number;
    valid_from?: string;
    valid_until?: string;
    ord?: number;
    description?: string;
    is_active?: boolean;
    image?: File;
}

export interface MileageProductDeleteResponse {
    message: string;
    deleted_id: number;
}
