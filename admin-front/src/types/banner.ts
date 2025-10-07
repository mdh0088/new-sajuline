/**
 * 배너 타입 정의 (새 백엔드 API 규격)
 * 백엔드 API: /api/v1/banners
 */

export interface BannerItem {
    banner_id: number;
    banner_code: string;
    banner_name: string;
    banner_type: string;
    image_url: string;
    mobile_image_url: string | null;
    link_url: string | null;
    link_target: string;
    display_order: number;
    is_active: boolean;
    valid_from: string;
    valid_until: string;
    click_count: number;
    impression_count: number;
    created_at: string;
    updated_at: string | null;
}

export interface BannerListResponse {
    items: BannerItem[];
    total: number;
}

export interface BannerCreateRequest {
    banner_name: string;
    banner_type: string;
    link_url?: string;
    link_target?: string;
    display_order?: number;
    is_active?: boolean;
    valid_from: string;
    valid_until: string;
    image?: File;
    image_url?: string;
}

export interface BannerUpdateRequest {
    banner_id: number;
    banner_name?: string;
    banner_type?: string;
    image_url?: string;
    link_url?: string;
    link_target?: string;
    display_order?: number;
    is_active?: boolean;
    valid_from?: string;
    valid_until?: string;
    image?: File;
}

export interface BannerDeleteResponse {
    banner_id: number;
    deleted: boolean;
}
