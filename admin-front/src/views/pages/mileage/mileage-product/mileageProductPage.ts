/**
 * 마일리지 상품 관리 서비스 함수 (새 백엔드 API 규격)
 * 백엔드 API: /api/v1/mileage
 */

import type { Ref } from 'vue';
import type { UploadUserFile } from 'element-plus';
import http_json from '@/api/_config/http_json';
import * as mileageProductApi from '@/api/mileage/mileageProductApi';
import * as swal from '@/commonUtils/swal';
import type {
  MileageProductItem,
  MileageProductListResponse,
  MileageProductCreateRequest,
  MileageProductUpdateRequest
} from '@/types/mileage';

/**
 * 마일리지 상품 목록 조회 (페이징)
 */
export const getMileageProductList = async (tableOptions: any) => {
  try {
    tableOptions.value.isLoading = true;

    const response = await http_json.get(mileageProductApi.getMileageProductListURL, {
      params: {
        page: tableOptions.value.currentPage ?? 1,
        limit: tableOptions.value.rowPage ?? 10
      }
    });

    if (response.data.success) {
      tableOptions.value.items = response.data.data;
      tableOptions.value.totalCnt = response.data.meta.pagination.total;
      tableOptions.value.currentPage = response.data.meta.pagination.page;
      tableOptions.value.rowPage = response.data.meta.pagination.limit;
    }
  } catch (error: any) {
    console.error('마일리지 상품 목록 조회 실패:', error);
    await swal.swalAlert(error.response?.data?.message || '목록 조회 중 오류가 발생했습니다.', 'error');
  } finally {
    tableOptions.value.isLoading = false;
  }
};

/**
 * 마일리지 상품 상세 조회
 */
export const getMileageProductDetail = async (
  mileage_id: number,
  attachFile?: Ref<UploadUserFile[]>
): Promise<MileageProductItem | null> => {
  try {
    const response = await http_json.get(`${mileageProductApi.getMileageProductDetailURL}/${mileage_id}`);

    if (response.data.success) {
      const data: MileageProductItem = response.data.data;

      // 이미지 처리 - CDN 베이스 URL과 결합
      if (data.m_product_img && attachFile) {
        const cdnBase = import.meta.env.VITE_APP_UPLOAD_URL;
        const imageUrl = data.m_product_img.startsWith('http')
          ? data.m_product_img
          : `${cdnBase}mileage/${data.m_product_img}`;

        attachFile.value = [{
          name: data.m_product_img.split('/').pop() || 'mileage',
          url: imageUrl
        }];
      }

      return data;
    }

    return null;
  } catch (error: any) {
    console.error('마일리지 상품 상세 조회 실패:', error);
    await swal.swalAlert(error.response?.data?.message || '상세 조회 중 오류가 발생했습니다.', 'error');
    return null;
  }
};

/**
 * 마일리지 상품 생성
 */
export const createMileageProduct = async (payload: MileageProductCreateRequest, doSearch: () => void) => {
  try {
    const formData = new FormData();

    // 필수 필드
    formData.append('m_product_name', payload.m_product_name);
    formData.append('m_product_value', payload.m_product_value.toString());
    formData.append('charge_point', payload.charge_point.toString());
    formData.append('valid_from', payload.valid_from);
    formData.append('valid_until', payload.valid_until);

    // 선택 필드
    if (payload.ord !== undefined) formData.append('ord', payload.ord.toString());
    if (payload.description) formData.append('description', payload.description);
    if (payload.is_active !== undefined) formData.append('is_active', payload.is_active.toString());

    // 이미지 파일 (필수)
    if (payload.image) {
      formData.append('image_file', payload.image);
    }

    const response = await http_json.post(mileageProductApi.createMileageProductURL, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });

    if (response.data.success) {
      await swal.swalAlert('마일리지 상품이 생성되었습니다.', 'success');
      await doSearch();
      return true;
    }
    return false;
  } catch (error: any) {
    console.error('마일리지 상품 생성 실패:', error);
    await swal.swalAlert(error.response?.data?.message || '생성 중 오류가 발생했습니다.', 'error');
    return false;
  }
};

/**
 * 마일리지 상품 수정
 */
export const updateMileageProduct = async (
  mileage_id: number,
  payload: MileageProductUpdateRequest,
  doSearch: () => void
) => {
  try {
    const formData = new FormData();

    // 선택 필드 (변경된 것만)
    if (payload.m_product_name) formData.append('m_product_name', payload.m_product_name);
    if (payload.m_product_value) formData.append('m_product_value', payload.m_product_value.toString());
    if (payload.charge_point) formData.append('charge_point', payload.charge_point.toString());
    if (payload.valid_from) formData.append('valid_from', payload.valid_from);
    if (payload.valid_until) formData.append('valid_until', payload.valid_until);
    if (payload.ord !== undefined) formData.append('ord', payload.ord.toString());
    if (payload.description !== undefined) formData.append('description', payload.description || '');
    if (payload.is_active !== undefined) formData.append('is_active', payload.is_active.toString());

    // 이미지 파일 (선택)
    if (payload.image) {
      formData.append('image_file', payload.image);
    }

    const response = await http_json.put(`${mileageProductApi.updateMileageProductURL}/${mileage_id}`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });

    if (response.data.success) {
      await swal.swalAlert('마일리지 상품이 수정되었습니다.', 'success');
      await doSearch();
      return true;
    }
    return false;
  } catch (error: any) {
    console.error('마일리지 상품 수정 실패:', error);
    await swal.swalAlert(error.response?.data?.message || '수정 중 오류가 발생했습니다.', 'error');
    return false;
  }
};

/**
 * 마일리지 상품 삭제
 */
export const deleteMileageProduct = async (mileage_id: number) => {
  try {
    const response = await http_json.delete(`${mileageProductApi.deleteMileageProductURL}/${mileage_id}`);

    if (response.data.success) {
      await swal.swalAlert('마일리지 상품이 삭제되었습니다.', 'success');
      return true;
    }
    return false;
  } catch (error: any) {
    console.error('마일리지 상품 삭제 실패:', error);
    await swal.swalAlert(error.response?.data?.message || '삭제 중 오류가 발생했습니다.', 'error');
    return false;
  }
};

/**
 * 마일리지 상품 즉시 수정 (활성화 여부 토글)
 */
export const updateMileageProductQuick = async (product: MileageProductItem, doSearch: () => void) => {
  const result = await swal.swalConfirm('정말 저장하시겠습니까?', 'warning');
  if (!result.isConfirmed) {
    await doSearch(); // 변경 취소시 원래대로 복원
    return false;
  }

  const payload: MileageProductUpdateRequest = {
    is_active: product.is_active
  };

  try {
    const formData = new FormData();
    formData.append('is_active', product.is_active.toString());

    const response = await http_json.put(`${mileageProductApi.updateMileageProductURL}/${product.mileage_id}`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });

    if (response.data.success) {
      await swal.swalAlert('마일리지 상품이 수정되었습니다.', 'success');
      await doSearch();
      return true;
    }
    return false;
  } catch (error: any) {
    console.error('마일리지 상품 수정 실패:', error);
    await swal.swalAlert(error.response?.data?.message || '수정 중 오류가 발생했습니다.', 'error');
    await doSearch(); // 에러 발생시에도 원래대로 복원
    return false;
  }
};
