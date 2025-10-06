// 등급 아이템 (백엔드 GradeItem과 일치)
export interface GradeItem {
    grade_code: string;
    grade_name: string;
    grade_level: number;
    min_purchase_amount: number;
    point_earn_rate: number;
    discount_rate: number;
    benefits: Record<string, any> | null;
    grade_image_url: string | null;
    description: string | null;
    is_active: boolean;
    created_at: string;
    updated_at: string | null;
}

// 등급 목록 응답 (백엔드 GradeListResponse와 일치)
export interface GradeListResponse {
    grades: GradeItem[];
    total: number;
}

// 등급 상세 응답 (백엔드 GradeDetailResponse와 일치)
export interface GradeDetailResponse {
    grade: GradeItem;
}

// 등급 생성 요청 (백엔드 GradeCreateRequest와 일치)
export interface GradeCreateRequest {
    grade_code: string;
    grade_name: string;
    grade_level: number;
    min_purchase_amount: number;
    point_earn_rate: number;
    discount_rate: number;
    benefits?: Record<string, any> | null;
    description?: string | null;
    is_active?: boolean;
}

// 등급 수정 요청 (백엔드 GradeUpdateRequest와 일치)
export interface GradeUpdateRequest {
    grade_code: string;
    grade_name?: string | null;
    grade_level?: number | null;
    min_purchase_amount?: number | null;
    point_earn_rate?: number | null;
    discount_rate?: number | null;
    benefits?: Record<string, any> | null;
    description?: string | null;
    is_active?: boolean | null;
}

// 등급 삭제 응답 (백엔드 GradeDeleteResponse와 일치)
export interface GradeDeleteResponse {
    grade_code: string;
    deleted: boolean;
}

// 등급별 유저 아이템 (백엔드 UsersByGradeItem과 일치)
export interface UsersByGradeItem {
    user_id: string;
    email: string;
    nickname: string;
    phone: string;
    join_type: string;
    grade_code: string;
    created_at: string;
}

// 등급별 유저 목록 응답 (백엔드 UsersByGradeResponse와 일치)
export interface UsersByGradeResponse {
    users: UsersByGradeItem[];
    total: number;
}
