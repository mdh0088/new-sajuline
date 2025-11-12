import http from '@/api/_config/http';
import http_json from '@/api/_config/http_json';
import * as swal from '@/commonUtils/swal';
import {
  getCounselorApplicationsListURL,
  getCounselorApplicationDetailURL,
  updateCounselorApplicationURL,
  updateCounselorApplicationStatusURL,
  convertToCounselorURL
} from '@/api/counselor-application/counselorApplicationApi';
import type {
  CounselorApplicationListItem,
  CounselorApplicationResponse
} from '@/types/counselor_application';
import {Ref} from "vue";
import type {UploadUserFile} from 'element-plus';

const CDN_URL = import.meta.env.VITE_CDN_URL || '';
const UPLOAD_URL = import.meta.env.VITE_APP_UPLOAD_URL || '';

/**
 * 상담사 신청 목록 조회
 */
export const getCounselorApplicationsList = async (
    searchOptions: Ref<SearchOptionsList>,
    tableOptions: Ref<TableOptions<CounselorApplicationListItem>>
): Promise<void> => {
  tableOptions.value.isLoading = true;

  try {
    // searchOptions에서 파라미터 추출
    const searchTypeOption = searchOptions.value.optionsList.find(opt => opt.key === 'search_type');
    const searchNameOption = searchOptions.value.optionsList.find(opt => opt.key === 'search_name');
    const specialtiesOption = searchOptions.value.optionsList.find(opt => opt.key === 'specialties');
    const applicationStatusOption = searchOptions.value.optionsList.find(opt => opt.key === 'application_status');
    const dateValueOption = searchOptions.value.optionsList.find(opt => opt.key === 'date_value');

    // Query string 생성
    const queryParams = new URLSearchParams();
    queryParams.append('page', (tableOptions.value.currentPage || 1).toString());
    queryParams.append('limit', (tableOptions.value.rowPage || 10).toString());
    queryParams.append('search_type', searchTypeOption?.value === 'all' ? 'all' : (searchTypeOption?.value || 'all'));

    if (searchNameOption?.value) {
      queryParams.append('search_name', searchNameOption.value);
    }

    if (specialtiesOption?.value && specialtiesOption.value !== 'all') {
      queryParams.append('specialties', specialtiesOption.value);
    }

    if (applicationStatusOption?.value && applicationStatusOption.value !== 'all') {
      queryParams.append('application_status', applicationStatusOption.value);
    }

    if (Array.isArray(dateValueOption?.value) && dateValueOption.value.length > 0) {
      queryParams.append('start_date', dateValueOption.value[0]);
    }

    if (Array.isArray(dateValueOption?.value) && dateValueOption.value.length > 1) {
      queryParams.append('end_date', dateValueOption.value[1]);
    }

    // API 호출
    const response = await http.get(`${getCounselorApplicationsListURL}?${queryParams.toString()}`);

    // 응답 데이터 처리
    if (response.data) {
      tableOptions.value.items = response.data.data || [];
      tableOptions.value.totalCnt = response.data.meta?.pagination?.total || 0;
    }

  } catch (error) {
    console.error('상담사 신청 목록 조회 실패:', error);
    swal.swalAlert('상담사 신청 목록을 불러오는데 실패했습니다.', 'error');
  } finally {
    tableOptions.value.isLoading = false;
  }
};

/**
 * 상담사 신청 상세 조회
 */
export const getCounselorApplicationDetail = async (
    applicationId: number,
    selectedImageFile?: Ref<UploadUserFile[]>,
    uploadImage1File?: Ref<UploadUserFile[]>,
    uploadImage2File?: Ref<UploadUserFile[]>,
    uploadImage3File?: Ref<UploadUserFile[]>
): Promise<{success: boolean; data?: CounselorApplicationResponse; message?: string}> => {
  try {
    const url = `${getCounselorApplicationDetailURL}?application_id=${applicationId}`;
    const response = await http.get(url);

    const data = response.data.data;

    // 이미지 처리 - CDN 베이스 URL과 결합
    if (data.selected_image && selectedImageFile) {
      const imageUrl = data.selected_image.startsWith('http')
        ? data.selected_image
        : `${UPLOAD_URL}cs/${data.selected_image}`;
      selectedImageFile.value = [{
        name: data.selected_image.split('/').pop() || 'selected_image',
        url: imageUrl
      }];
      data.selected_image_url = imageUrl;
    }
    if (data.upload_image1 && uploadImage1File) {
      const imageUrl = data.upload_image1.startsWith('http')
        ? data.upload_image1
        : `${UPLOAD_URL}cs/${data.upload_image1}`;
      uploadImage1File.value = [{
        name: data.upload_image1.split('/').pop() || 'upload_image1',
        url: imageUrl
      }];
      data.upload_image1_url = imageUrl;
    }
    if (data.upload_image2 && uploadImage2File) {
      const imageUrl = data.upload_image2.startsWith('http')
        ? data.upload_image2
        : `${UPLOAD_URL}cs/${data.upload_image2}`;
      uploadImage2File.value = [{
        name: data.upload_image2.split('/').pop() || 'upload_image2',
        url: imageUrl
      }];
      data.upload_image2_url = imageUrl;
    }
    if (data.upload_image3 && uploadImage3File) {
      const imageUrl = data.upload_image3.startsWith('http')
        ? data.upload_image3
        : `${UPLOAD_URL}cs/${data.upload_image3}`;
      uploadImage3File.value = [{
        name: data.upload_image3.split('/').pop() || 'upload_image3',
        url: imageUrl
      }];
      data.upload_image3_url = imageUrl;
    }

    return {
      success: true,
      data
    };
  } catch (error: any) {
    console.error('상담사 신청 상세 조회 실패:', error);
    swal.swalAlert('상세 조회에 실패했습니다.', 'error');
    return {
      success: false,
      message: error.response?.data?.message || '상세 조회에 실패했습니다.'
    };
  }
};

/**
 * 상담사 신청 상태 변경
 */
export const updateApplicationStatus = async (
  applicationId: number,
  status: string,
  adminNote?: string
): Promise<{success: boolean; data?: any; message?: string}> => {
  try {
    const url = updateCounselorApplicationStatusURL(applicationId);
    const payload: any = { application_status: status };
    if (adminNote !== undefined && adminNote !== null) {
      payload.admin_note = adminNote;
    }

    const response = await http_json.patch(url, payload);

    return {
      success: true,
      data: response.data.data
    };
  } catch (error: any) {
    console.error('신청 상태 변경 실패:', error);
    swal.swalAlert('상태 변경에 실패했습니다.', 'error');
    return {
      success: false,
      message: error.response?.data?.message || '상태 변경에 실패했습니다.'
    };
  }
};

/**
 * 상담사 신청 정보 수정
 */
export const updateApplicationInfo = async (
  applicationId: number,
  formData: FormData
) => {
  try {
    const url = updateCounselorApplicationURL(applicationId);
    const response = await http.patch(url, formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    });

    return {
      success: true,
      data: response.data.data
    };
  } catch (error: any) {
    console.error('신청 정보 수정 실패:', error);
    return {
      success: false,
      message: error.response?.data?.message || '정보 수정에 실패했습니다.'
    };
  }
};

/**
 * 상담사 신청자를 정식 상담사로 전환
 */
export const convertToCounselor = async (
  counselorCode: string,
  applicationData: CounselorApplicationResponse
) => {
  try {
    const payload = {
      counselor_code: counselorCode,
      name: applicationData.name,
      nickname: applicationData.nickname,
      email: applicationData.email,
      phone: applicationData.phone,
      address: applicationData.address || '',
      specialty_types: applicationData.specialty_types,
      keywords: applicationData.keywords || '',
      introduction: applicationData.introduction || '',
      selected_image_url: applicationData.selected_image || '',
      upload_image1: applicationData.upload_image1 || '',
      upload_image2: applicationData.upload_image2 || '',
      upload_image3: applicationData.upload_image3 || '',
      application_status: applicationData.application_status
    };

    const response = await http_json.post(convertToCounselorURL, payload);

    return {
      success: true,
      data: response.data.data
    };
  } catch (error: any) {
    console.error('상담사 전환 실패:', error);
    swal.swalAlert(error.response?.data?.message || '상담사 전환에 실패했습니다.', 'error');
    return {
      success: false,
      message: error.response?.data?.message || '상담사 전환에 실패했습니다.'
    };
  }
};
