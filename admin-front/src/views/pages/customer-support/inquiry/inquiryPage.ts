import http from '@/api/_config/http';
import * as inquiryApi from '@/api/inquiry/inquiryApi';
import * as swal from '@/commonUtils/swal';
import type {
  InquiryListParams,
  CounselorInquiryItem,
  UserInquiryListParams,
  UserInquiryItem,
  UserToCsListParams,
  UserToCsInquiryItem,
  InquiryReplyUpdateRequest,
  InquiryUpdateRequest
} from '@/types/inquiry';

// ===================================================
// 상담사 문의 (CS_TO_ADMIN)
// ===================================================
export const getCounselorInquiryList = async (searchOptions: any, tableOptions: any) => {
  try {
    tableOptions.value.isLoading = true;

    const params: InquiryListParams = {
      page: tableOptions.value.currentPage,
      limit: tableOptions.value.rowPage,
      search_type: searchOptions.value.getOptionByKey('search_type')?.value || 'all',
      search_name: searchOptions.value.getOptionByKey('search_name')?.value || undefined,
      counselor_id: searchOptions.value.getOptionByKey('counselor_id')?.value || undefined,
    };

    const dateValue = searchOptions.value.getOptionByKey('dateValue')?.value;
    if (dateValue && dateValue.length === 2) {
      params.start_dt = dateValue[0];
      params.end_dt = dateValue[1];
    }

    const response = await http.get(inquiryApi.getCounselorInquiryListURL, { params });

    if (response.data.success) {
      tableOptions.value.items = response.data.data;
      tableOptions.value.totalCnt = response.data.data.total;
    }
  } catch (error: any) {
    console.error('상담사 문의 목록 조회 실패:', error);
    await swal.swalAlert(error.response?.data?.message || '목록 조회 중 오류가 발생했습니다.', 'error');
  } finally {
    tableOptions.value.isLoading = false;
  }
};

export const getCounselorInquiryDetail = async (inquiry_id: number) => {
  try {
    const response = await http.get(inquiryApi.getCounselorInquiryDetailURL, {
      params: { inquiry_id }
    });
    if (response.data.success) {
      return response.data.data;
    }
  } catch (error: any) {
    console.error('상담사 문의 상세 조회 실패:', error);
    await swal.swalAlert(error.response?.data?.message || '상세 조회 중 오류가 발생했습니다.', 'error');
  }
};

export const replyCounselorInquiry = async (payload: InquiryReplyUpdateRequest, doSearch: () => void) => {
  try {
    const response = await http.post(inquiryApi.replyCounselorInquiryURL, payload);
    if (response.data.success) {
      await swal.swalAlert('답변이 등록되었습니다.', 'success');
      await doSearch();
      return true;
    }
    return false;
  } catch (error: any) {
    console.error('상담사 문의 답변 실패:', error);
    await swal.swalAlert(error.response?.data?.message || '답변 등록 중 오류가 발생했습니다.', 'error');
    return false;
  }
};

export const deleteCounselorInquiry = async (inquiry_id: number) => {
  try {
    const response = await http.delete(inquiryApi.deleteCounselorInquiryURL, {
      params: { inquiry_id }
    });
    if (response.data.success) {
      await swal.swalAlert('삭제되었습니다.', 'success');
      return true;
    }
    return false;
  } catch (error: any) {
    console.error('상담사 문의 삭제 실패:', error);
    await swal.swalAlert(error.response?.data?.message || '삭제 중 오류가 발생했습니다.', 'error');
    return false;
  }
};

// ===================================================
// 1:1 고객센터 문의 (USER_TO_ADMIN)
// ===================================================
export const getUserInquiryList = async (searchOptions: any, tableOptions: any) => {
  try {
    tableOptions.value.isLoading = true;

    const params: UserInquiryListParams = {
      page: tableOptions.value.currentPage,
      limit: tableOptions.value.rowPage,
      search_type: searchOptions.value.getOptionByKey('search_type')?.value || 'all',
      search_name: searchOptions.value.getOptionByKey('search_name')?.value || undefined,
      user_id: searchOptions.value.getOptionByKey('user_id')?.value || undefined,
    };

    const dateValue = searchOptions.value.getOptionByKey('dateValue')?.value;
    if (dateValue && dateValue.length === 2) {
      params.start_dt = dateValue[0];
      params.end_dt = dateValue[1];
    }

    const response = await http.get(inquiryApi.getUserInquiryListURL, { params });

    if (response.data.success) {
      tableOptions.value.items = response.data.data;
      tableOptions.value.totalCnt = response.data.data.total;
    }
  } catch (error: any) {
    console.error('사용자 문의 목록 조회 실패:', error);
    await swal.swalAlert(error.response?.data?.message || '목록 조회 중 오류가 발생했습니다.', 'error');
  } finally {
    tableOptions.value.isLoading = false;
  }
};

export const getUserInquiryDetail = async (inquiry_id: number) => {
  try {
    const response = await http.get(inquiryApi.getUserInquiryDetailURL, {
      params: { inquiry_id }
    });
    if (response.data.success) {
      return response.data.data;
    }
  } catch (error: any) {
    console.error('사용자 문의 상세 조회 실패:', error);
    await swal.swalAlert(error.response?.data?.message || '상세 조회 중 오류가 발생했습니다.', 'error');
  }
};

export const replyUserInquiry = async (payload: InquiryReplyUpdateRequest, doSearch: () => void) => {
  try {
    const response = await http.post(inquiryApi.replyUserInquiryURL, payload);
    if (response.data.success) {
      await swal.swalAlert('답변이 등록되었습니다.', 'success');
      await doSearch();
      return true;
    }
    return false;
  } catch (error: any) {
    console.error('사용자 문의 답변 실패:', error);
    await swal.swalAlert(error.response?.data?.message || '답변 등록 중 오류가 발생했습니다.', 'error');
    return false;
  }
};

export const deleteUserInquiry = async (inquiry_id: number) => {
  try {
    const response = await http.delete(inquiryApi.deleteUserInquiryURL, {
      params: { inquiry_id }
    });
    if (response.data.success) {
      await swal.swalAlert('삭제되었습니다.', 'success');
      return true;
    }
    return false;
  } catch (error: any) {
    console.error('사용자 문의 삭제 실패:', error);
    await swal.swalAlert(error.response?.data?.message || '삭제 중 오류가 발생했습니다.', 'error');
    return false;
  }
};

// ===================================================
// 1:1 상담사 문의 (USER_TO_CS)
// ===================================================
export const getUserToCsList = async (searchOptions: any, tableOptions: any) => {
  try {
    tableOptions.value.isLoading = true;

    const params: UserToCsListParams = {
      page: tableOptions.value.currentPage,
      limit: tableOptions.value.rowPage,
      search_type: searchOptions.value.getOptionByKey('search_type')?.value || 'all',
      search_name: searchOptions.value.getOptionByKey('search_name')?.value || undefined,
      user_id: searchOptions.value.getOptionByKey('user_id')?.value || undefined,
      counselor_id: searchOptions.value.getOptionByKey('counselor_id')?.value || undefined,
    };

    const dateValue = searchOptions.value.getOptionByKey('dateValue')?.value;
    if (dateValue && dateValue.length === 2) {
      params.start_dt = dateValue[0];
      params.end_dt = dateValue[1];
    }

    const response = await http.get(inquiryApi.getUserToCsListURL, { params });

    if (response.data.success) {
      tableOptions.value.items = response.data.data;
      tableOptions.value.totalCnt = response.data.data.total;
    }
  } catch (error: any) {
    console.error('사용자→상담사 문의 목록 조회 실패:', error);
    await swal.swalAlert(error.response?.data?.message || '목록 조회 중 오류가 발생했습니다.', 'error');
  } finally {
    tableOptions.value.isLoading = false;
  }
};

export const getUserToCsDetail = async (inquiry_id: number) => {
  try {
    const response = await http.get(inquiryApi.getUserToCsDetailURL, {
      params: { inquiry_id }
    });
    if (response.data.success) {
      return response.data.data;
    }
  } catch (error: any) {
    console.error('사용자→상담사 문의 상세 조회 실패:', error);
    await swal.swalAlert(error.response?.data?.message || '상세 조회 중 오류가 발생했습니다.', 'error');
  }
};

export const replyUserToCs = async (payload: InquiryReplyUpdateRequest, doSearch: () => void) => {
  try {
    const response = await http.post(inquiryApi.replyUserToCsURL, payload);
    if (response.data.success) {
      await swal.swalAlert('답변이 등록되었습니다.', 'success');
      await doSearch();
      return true;
    }
    return false;
  } catch (error: any) {
    console.error('사용자→상담사 문의 답변 실패:', error);
    await swal.swalAlert(error.response?.data?.message || '답변 등록 중 오류가 발생했습니다.', 'error');
    return false;
  }
};

export const deleteUserToCs = async (inquiry_id: number) => {
  try {
    const response = await http.delete(inquiryApi.deleteUserToCsURL, {
      params: { inquiry_id }
    });
    if (response.data.success) {
      await swal.swalAlert('삭제되었습니다.', 'success');
      return true;
    }
    return false;
  } catch (error: any) {
    console.error('사용자→상담사 문의 삭제 실패:', error);
    await swal.swalAlert(error.response?.data?.message || '삭제 중 오류가 발생했습니다.', 'error');
    return false;
  }
};

// ===================================================
// 문의 수정 (제목/내용/답변)
// ===================================================
export const updateCounselorInquiry = async (payload: InquiryUpdateRequest, doSearch: () => void) => {
  try {
    const response = await http.put(inquiryApi.updateCounselorInquiryURL, payload);
    if (response.data.success) {
      await swal.swalAlert('수정되었습니다.', 'success');
      await doSearch();
      return true;
    }
    return false;
  } catch (error: any) {
    console.error('상담사 문의 수정 실패:', error);
    await swal.swalAlert(error.response?.data?.message || '수정 중 오류가 발생했습니다.', 'error');
    return false;
  }
};

export const updateUserInquiry = async (payload: InquiryUpdateRequest, doSearch: () => void) => {
  try {
    const response = await http.put(inquiryApi.updateUserInquiryURL, payload);
    if (response.data.success) {
      await swal.swalAlert('수정되었습니다.', 'success');
      await doSearch();
      return true;
    }
    return false;
  } catch (error: any) {
    console.error('사용자 문의 수정 실패:', error);
    await swal.swalAlert(error.response?.data?.message || '수정 중 오류가 발생했습니다.', 'error');
    return false;
  }
};

export const updateUserToCsInquiry = async (payload: InquiryUpdateRequest, doSearch: () => void) => {
  try {
    const response = await http.put(inquiryApi.updateUserToCsURL, payload);
    if (response.data.success) {
      await swal.swalAlert('수정되었습니다.', 'success');
      await doSearch();
      return true;
    }
    return false;
  } catch (error: any) {
    console.error('사용자→상담사 문의 수정 실패:', error);
    await swal.swalAlert(error.response?.data?.message || '수정 중 오류가 발생했습니다.', 'error');
    return false;
  }
};
