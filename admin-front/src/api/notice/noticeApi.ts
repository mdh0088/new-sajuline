/**
 * 공지사항 API (새 백엔드 규격)
 * 백엔드 API: /api/v1/notices
 */

const proxyURL = '/api/v1/notices';

// 공지사항 목록 조회
export const getNoticeListURL = `${proxyURL}/list`;

// 공지사항 상세 조회
export const getNoticeDetailURL = `${proxyURL}/detail`;

// 공지사항 등록
export const createNoticeURL = `${proxyURL}/create`;

// 공지사항 수정
export const updateNoticeURL = `${proxyURL}/update`;

// 공지사항 삭제
export const deleteNoticeURL = `${proxyURL}/delete`;
