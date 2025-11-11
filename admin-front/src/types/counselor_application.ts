// 상담사 신청 목록 아이템 (백엔드 CounselorApplicationListItem 스키마와 일치)
export interface CounselorApplicationListItem {
    application_id: number;
    name: string;
    nickname: string;
    email: string;
    phone: string;
    address: string | null;
    specialty_types: string[] | null;
    keywords: string | null;
    introduction: string | null;
    selected_image_url: string | null;
    upload_image1: string | null;
    upload_image2: string | null;
    upload_image3: string | null;
    application_status: string; // "PENDING" | "APPROVED" | "REJECTED"
    admin_note: string | null;
    reviewed_by: number | null;
    reviewed_at: string | null;
    created_at: string;
    updated_at: string | null;
}

// 상담사 신청 상세 응답 (백엔드 CounselorApplicationResponse 스키마와 일치)
export interface CounselorApplicationResponse {
    application_id: number;
    name: string;
    nickname: string;
    email: string;
    phone: string;
    address: string | null;
    specialty_types: string | null;
    keywords: string | null;
    introduction: string | null;
    selected_image_url: string | null;
    upload_image1: string | null;
    upload_image2: string | null;
    upload_image3: string | null;
    application_status: string;
    admin_note: string | null;
    reviewed_by: number | null;
    reviewed_at: string | null;
    created_at: string;
    updated_at: string | null;
}

// 상담사 신청 목록 조회 파라미터 (백엔드 CounselorApplicationListParams와 일치)
export interface CounselorApplicationListParams {
    page: number;
    limit: number;
    search_type: string; // "all" | "name" | "nickname" | "email"
    search_name?: string | null;
    specialties?: string[] | null;
    application_status?: string | null; // "PENDING" | "APPROVED" | "REJECTED"
    start_dt?: string | null;
    end_dt?: string | null;
}

// 상담사 신청 상세 수정 요청 (백엔드 CounselorApplicationDetailUpdate와 일치)
export interface CounselorApplicationDetailUpdate {
    name?: string | null;
    nickname?: string | null;
    email?: string | null;
    phone?: string | null;
    address?: string | null;
    specialties?: string | null; // JSON 문자열 예: '["TARO","SAJU"]'
    keywords?: string | null;
    introduction?: string | null;
    application_status?: string | null; // "PENDING" | "APPROVED" | "REJECTED"
    admin_note?: string | null;
    reviewed_by?: number | null;
}

// 상담사 신청 상태 변경 요청
export interface CounselorApplicationStatusUpdate {
    application_status: "PENDING" | "APPROVED" | "REJECTED";
    admin_note?: string | null;
    reviewed_by?: number | null;
}

// API 응답 래퍼
export interface CounselorApplicationListResponse {
    data: CounselorApplicationListItem[];
    page: number;
    limit: number;
    total: number;
    message: string;
}
