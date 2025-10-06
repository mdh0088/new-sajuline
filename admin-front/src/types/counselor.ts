// 상담사 목록 아이템 (백엔드 CounselorListItem 스키마와 일치 - 모든 t_counselor 필드 포함)
export interface CounselorListItem {
    counselor_id: string;
    counselor_code: string;
    name: string;
    nickname: string;
    phone: string;
    profile_image_url: string | null;
    introduction_short: string | null;
    greeting_message: string | null;
    career_info: string | null;
    grade: string | null;
    specialty_types: string[] | null;
    keywords: string | null;
    work_time: string | null;
    rating_avg: number | null;
    rating_count: number | null;
    consultation_count: number | null;
    consultation_time_total: number | null;
    after_amount: number | null;
    before_amount: string;
    is_best: boolean | null;
    is_new: boolean | null;
    is_out: boolean;
    is_show: boolean;
    approved_at: string | null;
    created_at: string;
    updated_at: string | null;
    last_login_at: string | null;
    withdrawn_at: string | null;
    m_state: string | null; // "1"=대기중, "2"=상담중, "3"=부재중
}

// 상담사 상세 응답 (백엔드 CounselorResponse 스키마와 일치)
export interface CounselorResponse {
    counselor_id: string;
    counselor_code: string;
    name: string;
    nickname: string;
    phone: string;
    profile_image_url: string | null;
    introduction_short: string | null;
    greeting_message: string | null;
    career_info: string | null;
    counselor_status: string;
    grade: string | null;
    specialty_types: string | null;
    keywords: string | null;
    work_time: string | null;
    rating_avg: number | null;
    rating_count: number | null;
    consultation_count: number | null;
    consultation_time_total: number | null;
    after_amount: number | null;
    before_amount: string;
    is_best: boolean | null;
    is_new: boolean | null;
    is_out: boolean;
    is_show: boolean;
    approved_at: string | null;
    created_at: string;
    updated_at: string | null;
    last_login_at: string | null;
    withdrawn_at: string | null;
}

// ARS 멤버 정보 (백엔드 tm60_member와 일치)
export interface ArsCounselorInfo {
    idx: number;
    m_dnis: string;
    m_code: string;
    m_name: string;
    m_nickname: string;
    m_tel: string;
    m_tel1: string;
    m_tel2: string;
    m_mobile: string;
    m_state: string;
    m_nextstate: string;
    m_counselling: string;
    m_id: string;
    m_memo: string | null;
    last_chat: string;
    chat_level: string;
    class_: string;
    turn: string;
    bang: string;
    holdoff: string;
    m_bunho: string;
    m_writer: number;
    m_prate: number;
    m_fdate: string | null;
}

// 상담사 전체 상세 응답 (백엔드 CounselorFullDetailResponse 스키마와 일치)
export interface CounselorFullDetailResponse {
    counselor: CounselorResponse;
    member: ArsCounselorInfo | null;
}

// 상담사 목록 조회 파라미터 (백엔드 CounselorListParams와 일치)
export interface CounselorListParams {
    page: number;
    limit: number;
    search_type: string; // "all" | "name" | "nickname" | "counselor_id"
    search_name?: string | null;
    specialties?: string[] | null;
    is_show?: boolean | null;
    is_out?: boolean | null;
    start_dt?: string | null;
    end_dt?: string | null;
}

// 상담사 상세 수정 요청 (백엔드 CounselorDetailUpdate와 일치)
export interface CounselorDetailUpdate {
    is_show?: boolean | null;
    name?: string | null;
    nickname?: string | null;
    phone?: string | null;
    password?: string | null;
    specialties?: string | null; // JSON 문자열 예: '["TARO","SAJU"]'
    counselor_code?: string | null;
    grade?: string | null;
    after_amount?: number | null;
    before_amount?: number | string | null;
    work_time?: string | null;
    is_new?: boolean | null;
    introduction_short?: string | null;
    greeting_message?: string | null;
    career_info?: string | null;
    keywords?: string | null;
}

// 상담사 상태 업데이트 요청 (백엔드 CounselorStateUpdateRequest와 일치)
export interface CounselorStateUpdateRequest {
    counselor_id: string;
    counselor_code: string;
    m_state: "1" | "2" | "3"; // "1"=대기중, "2"=상담중, "3"=부재중
}

// 상담사 상태 업데이트 응답 (백엔드 CounselorStateUpdateResponse와 일치)
export interface CounselorStateUpdateResponse {
    counselor_id: string;
    counselor_code: string;
    m_state: string;
    updated: boolean;
}

// API 응답 래퍼
export interface CounselorListResponse {
    data: CounselorListItem[];
    page: number;
    limit: number;
    total: number;
    message: string;
}
