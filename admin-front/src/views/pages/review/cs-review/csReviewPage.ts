/**
 * 상담 후기 관리 서비스 함수 (새 백엔드 API 규격)
 * 백엔드 API: /api/v1/consultation-reviews
 */

import http from '@/api/_config/http';
import * as consultationReviewApi from '@/api/consultation-review/consultationReviewApi';
import * as counselorApi from '@/api/counselor/counselorApi';
import * as swal from '@/commonUtils/swal';
import type {
  ConsultationReviewItem,
} from '@/types/consultation_review';

/**
 * 상담 후기 목록 조회 (페이징)
 */
export const getReviewList = async (searchOptions: any, tableOptions: any) => {
  try {
    tableOptions.value.isLoading = true;

    // 검색 파라미터 구성
    const search_type = searchOptions.value.getOptionByKey('search_type')?.value || 'all';
    const search_name = searchOptions.value.getOptionByKey('search_name')?.value || null;
    const user_id = searchOptions.value.getOptionByKey('user_id')?.value || null;
    const counselor_id = searchOptions.value.getOptionByKey('counselor_id')?.value || null;
    const dateValue = searchOptions.value.getOptionByKey('date_value')?.value;

    let start_dt = null;
    let end_dt = null;
    if (dateValue && dateValue.length === 2) {
      start_dt = dateValue[0] ? new Date(dateValue[0]).toISOString().split('T')[0] : null;
      end_dt = dateValue[1] ? new Date(dateValue[1]).toISOString().split('T')[0] : null;
    }

    const response = await http.get(consultationReviewApi.getReviewListURL, {
      params: {
        page: tableOptions.value.currentPage ?? 1,
        limit: tableOptions.value.rowPage ?? 10,
        search_type: search_type !== 'all' ? search_type : undefined,
        search_name: search_name || undefined,
        user_id: user_id || undefined,
        counselor_id: counselor_id || undefined,
        start_dt: start_dt || undefined,
        end_dt: end_dt || undefined,
      }
    });

    if (response.data.success) {
      tableOptions.value.items = response.data.data;
      tableOptions.value.totalCnt = response.data.meta.pagination.total;
      tableOptions.value.currentPage = response.data.meta.pagination.page;
      tableOptions.value.rowPage = response.data.meta.pagination.limit;
    }
  } catch (error: any) {
    console.error('상담 후기 목록 조회 실패:', error);
    await swal.swalAlert(error.response?.data?.message || '목록 조회 중 오류가 발생했습니다.', 'error');
  } finally {
    tableOptions.value.isLoading = false;
  }
};

/**
 * 상담 후기 상세 조회
 */
export const getReviewDetail = async (review_id: number): Promise<ConsultationReviewItem | null> => {
  try {
    const response = await http.get(`${consultationReviewApi.getReviewDetailURL}/${review_id}`);

    if (response.data.success) {
      return response.data.data;
    }

    return null;
  } catch (error: any) {
    console.error('상담 후기 상세 조회 실패:', error);
    await swal.swalAlert(error.response?.data?.message || '상세 조회 중 오류가 발생했습니다.', 'error');
    return null;
  }
};

/**
 * 상담 후기 수정
 */
export const updateReview = async (
  review_id: number,
  payload: {
    content?: string;
    counselor_reply?: string;
  },
  doSearch: () => void
) => {
  try {
    const response = await http.put(`${consultationReviewApi.updateReviewURL}/${review_id}`, payload);

    if (response.data.success) {
      await swal.swalAlert('상담 후기가 수정되었습니다.', 'success');
      await doSearch();
      return true;
    }
    return false;
  } catch (error: any) {
    console.error('상담 후기 수정 실패:', error);
    await swal.swalAlert(error.response?.data?.message || '수정 중 오류가 발생했습니다.', 'error');
    return false;
  }
};

/**
 * 상담 후기 즉시 수정 (베스트/노출 여부 토글)
 */
export const updateReviewQuick = async (
  review: ConsultationReviewItem,
  doSearch: () => void,
  field: 'is_best' | 'is_visible' = 'is_visible'
) => {
  const result = await swal.swalConfirm('정말 저장하시겠습니까?', 'warning');
  if (!result.isConfirmed) {
    await doSearch(); // 변경 취소시 원래대로 복원
    return false;
  }

  try {
    const payload: any = {};
    if (field === 'is_best') {
      payload.is_best = review.is_best;
    } else if (field === 'is_visible') {
      payload.is_visible = review.is_visible;
    }

    const response = await http.put(`${consultationReviewApi.updateReviewURL}/${review.review_id}`, payload);

    if (response.data.success) {
      await swal.swalAlert('상담 후기가 수정되었습니다.', 'success');
      await doSearch();
      return true;
    }
    return false;
  } catch (error: any) {
    console.error('상담 후기 수정 실패:', error);
    await swal.swalAlert(error.response?.data?.message || '수정 중 오류가 발생했습니다.', 'error');
    await doSearch(); // 에러 발생시에도 원래대로 복원
    return false;
  }
};

/**
 * 상담사 목록 조회 (더미 리뷰 생성용)
 */
export const getCounselorList = async (): Promise<Array<{ counselor_id: string; nickname: string }>> => {
  try {
    const response = await http.get(counselorApi.getCounselorsListURL, {
      params: {
        page: 1,
        limit: 1000,
        is_show: true,
        is_out: false,
      }
    });

    if (response.data.success) {
      return response.data.data.map((item: any) => ({
        counselor_id: item.counselor_id,
        nickname: item.nickname || item.name || item.counselor_id,
      }));
    }
    return [];
  } catch (error: any) {
    console.error('상담사 목록 조회 실패:', error);
    return [];
  }
};

/**
 * 더미 상담 후기 생성
 */
export const createDummyReview = async (
  payload: {
    user_id: string;
    user_nickname: string;
    counselor_id: string;
    rating: number;
    content?: string;
    counselor_reply?: string;
    review_tags?: string;
    is_visible?: boolean;
    is_best?: boolean;
  },
  doSearch: () => void
) => {
  try {
    const response = await http.post(consultationReviewApi.createDummyReviewURL, payload);

    if (response.data.success) {
      await swal.swalAlert('더미 상담 후기가 생성되었습니다.', 'success');
      await doSearch();
      return true;
    }
    return false;
  } catch (error: any) {
    console.error('더미 상담 후기 생성 실패:', error);
    await swal.swalAlert(error.response?.data?.message || '생성 중 오류가 발생했습니다.', 'error');
    return false;
  }
};
