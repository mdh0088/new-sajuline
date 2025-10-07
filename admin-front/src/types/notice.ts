/**
 * 공지사항 타입 정의 (새 백엔드 API 규격)
 */

// 공지사항 목록 조회 파라미터
export interface NoticeListParams {
    page: number;
    limit: number;
    search_type: string; // all|title|content
    search_name?: string;
    target_audience?: string; // ALL|USER|COUNSELOR
    notice_type?: string;
    is_important?: boolean;
    is_active?: boolean;
    start_dt?: string;
    end_dt?: string;
}

// 공지사항 목록 아이템
export interface NoticeListItem {
    notice_id: number;
    notice_type: string;
    target_audience: string;
    title: string;
    is_important: boolean;
    is_active: boolean;
    view_count: number;
    created_by: number; // 관리자 ID (정수)
    created_at: string;
}

// 공지사항 상세 아이템 (content 포함)
export interface NoticeDetail {
    notice_id: number;
    notice_type: string;
    target_audience: string;
    title: string;
    content: string;
    is_important: boolean;
    is_active: boolean;
    view_count: number;
    created_by: number;
    created_at: string;
}

// 공지사항 상세 응답
export interface NoticeDetailResponse {
    notice: NoticeDetail;
}

// 공지사항 생성 요청
export interface NoticeCreateRequest {
    notice_type?: string;
    title: string;
    content: string;
    target_audience?: string;
    is_important?: boolean;
}

// 공지사항 수정 요청
export interface NoticeUpdateRequest {
    notice_id: number;
    notice_type?: string;
    title?: string;
    content?: string;
    target_audience?: string;
    is_important?: boolean;
}

// 공지사항 삭제 응답
export interface NoticeDeleteResponse {
    notice_id: number;
    deleted: boolean;
}
