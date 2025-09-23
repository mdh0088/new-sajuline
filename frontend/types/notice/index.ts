// 공지사항 관련 타입 정의

// 공지사항 카테고리
export type NoticeCategory = 'new' | 'event' | 'update' | 'important' | 'general';

// 공지사항 기본 정보
export interface INotice {
  id: number;
  title: string;
  content: string;
  category: NoticeCategory; // frontend 표현용, 백엔드 매핑 필요
  viewCount: number;
  createdAt: string;
  updatedAt?: string;
  isFixed?: boolean; // 상단 고정 여부
  author?: string;
}

// 공지사항 목록 아이템 (간략 정보)
export interface INoticeListItem {
  id: number;
  title: string;
  summary: string; // 내용 요약
  category: NoticeCategory;
  viewCount: number;
  createdAt: string;
  isFixed?: boolean;
}

// 공지사항 상세 정보
export interface INoticeDetail extends INotice {
  prevNotice?: {
    id: number;
    title: string;
  } | null;
  nextNotice?: {
    id: number;
    title: string;
  } | null;
  // 백엔드 필드 매핑 (상세 API)
  before_notice_id?: number | null;
  after_notice_id?: number | null;
  before_notice_title?: string | null;
  after_notice_title?: string | null;
}

// 공지사항 목록 페이지네이션
export interface INoticePagination {
  currentPage: number;
  totalPages: number;
  totalCount: number;
  pageSize: number;
  hasNext: boolean;
  hasPrev: boolean;
}

// 공지사항 목록 응답
export interface INoticeListResponse {
  notices: INoticeListItem[];
  pagination: INoticePagination;
}

// 공지사항 필터 옵션
export interface INoticeFilter {
  category?: NoticeCategory;
  searchTerm?: string;
  page?: number;
  pageSize?: number;
}