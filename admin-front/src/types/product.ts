// 포인트 상품 타입 정의 (백엔드 PointProductItem과 매칭)

export interface PointProductItem {
    product_id: number;
    product_code: string;
    product_name: string;
    point_amount: number;
    price: number;
    bonus_point: number;
    discount_rate: number;
    display_order: number;
    is_active: boolean;
    valid_from: string | null;
    valid_until: string | null;
    created_at: string;
    updated_at: string | null;
}

export interface PointProductListResponse {
    items: PointProductItem[];
    total: number;
}

export interface PointProductCreateRequest {
    product_name: string;
    point_amount: number;
    price: number;
    bonus_point?: number;
    discount_rate?: number;
    display_order?: number;
    is_active?: boolean;
    valid_from?: string | null;
    valid_until?: string | null;
}

export interface PointProductUpdateRequest {
    product_id: number;
    product_name?: string;
    point_amount?: number;
    price?: number;
    bonus_point?: number;
    discount_rate?: number;
    display_order?: number;
    is_active?: boolean;
    valid_from?: string | null;
    valid_until?: string | null;
}

export interface PointProductDeleteRequest {
    product_id: number;
}

export interface PointProductDeleteResponse {
    product_id: number;
    updated: boolean;
}
