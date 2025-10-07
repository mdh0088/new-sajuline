/**
 * 배너 관리 서비스 함수 (새 백엔드 API 규격)
 * 백엔드 API: /api/v1/banners
 */

import type { Ref } from 'vue';
import type { UploadUserFile } from 'element-plus';
import http from '@/api/_config/http';
import http_json from '@/api/_config/http_json';
import * as bannerApi from '@/api/banner/bannerApi';
import * as swal from '@/commonUtils/swal';
import type {
  BannerItem,
  BannerListResponse,
  BannerCreateRequest,
  BannerUpdateRequest,
  BannerDeleteResponse
} from '@/types/banner';

/**
 * 배너 목록 조회
 */
export const getBannerList = async (searchOptions: any, tableOptions: any, banner_type: string = 'MAIN') => {
  try {
    tableOptions.value.isLoading = true;

    const response = await http.get(bannerApi.getBannerListURL, {
      params: { banner_type }
    });

    if (response.data.success) {
      const banners: BannerListResponse = response.data.data;

      // 필터링 로직 (프론트엔드에서 필터링)
      let filteredItems = banners.items;

      // 검색 타입별 필터링
      const search_type = searchOptions.value.getOptionByKey('search_type')?.value;
      const search_name = searchOptions.value.getOptionByKey('search_name')?.value;

      if (search_name && search_type !== 'all') {
        filteredItems = filteredItems.filter(item => {
          const fieldValue = item[search_type as keyof BannerItem];
          return fieldValue?.toString().toLowerCase().includes(search_name.toLowerCase());
        });
      }

      // 활성 여부 필터링
      const is_active = searchOptions.value.getOptionByKey('is_active')?.value;
      if (is_active !== 'all') {
        filteredItems = filteredItems.filter(item => item.is_active === is_active);
      }

      // 날짜 필터링
      const dateValue = searchOptions.value.getOptionByKey('date_value')?.value;
      if (dateValue && dateValue.length === 2) {
        const startDate = new Date(dateValue[0]);
        const endDate = new Date(dateValue[1]);
        filteredItems = filteredItems.filter(item => {
          const createdDate = new Date(item.created_at);
          return createdDate >= startDate && createdDate <= endDate;
        });
      }

      tableOptions.value.items = filteredItems;
      tableOptions.value.totalCnt = filteredItems.length;
    }
  } catch (error: any) {
    console.error('배너 목록 조회 실패:', error);
    await swal.swalAlert(error.response?.data?.message || '목록 조회 중 오류가 발생했습니다.', 'error');
  } finally {
    tableOptions.value.isLoading = false;
  }
};

/**
 * 배너 상세 조회
 */
export const getBannerDetail = async (
  banner_id: number,
  attachFile?: Ref<UploadUserFile[]>
): Promise<BannerItem | null> => {
  try {
    const response = await http.get(bannerApi.getBannerDetailURL, {
      params: { banner_id }
    });

    if (response.data.success) {
      const data: BannerItem = response.data.data;

      // 이미지 처리 - CDN 베이스 URL과 결합
      if (data.image_url && attachFile) {
        const cdnBase = import.meta.env.VITE_APP_UPLOAD_URL;
        const imageUrl = data.image_url.startsWith('http')
          ? data.image_url
          : `${cdnBase}banner/${data.image_url}`;

        attachFile.value = [{
          name: data.image_url.split('/').pop() || 'banner',
          url: imageUrl
        }];
      }

      return data;
    }

    return null;
  } catch (error: any) {
    console.error('배너 상세 조회 실패:', error);
    await swal.swalAlert(error.response?.data?.message || '상세 조회 중 오류가 발생했습니다.', 'error');
    return null;
  }
};

/**
 * 배너 생성
 */
export const createBanner = async (payload: BannerCreateRequest, doSearch: () => void) => {
  try {
    const formData = new FormData();

    // 필수 필드
    formData.append('banner_name', payload.banner_name);
    formData.append('banner_type', payload.banner_type);
    formData.append('valid_from', payload.valid_from);
    formData.append('valid_until', payload.valid_until);

    // 선택 필드
    if (payload.link_url) formData.append('link_url', payload.link_url);
    if (payload.link_target) formData.append('link_target', payload.link_target);
    if (payload.display_order !== undefined) formData.append('display_order', payload.display_order.toString());
    if (payload.is_active !== undefined) formData.append('is_active', payload.is_active.toString());
    if (payload.image_url) formData.append('image_url', payload.image_url);

    // 이미지 파일
    if (payload.image) {
      formData.append('image', payload.image);
    }

    const response = await http_json.post(bannerApi.createBannerURL, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });

    if (response.data.success) {
      await swal.swalAlert('배너가 생성되었습니다.', 'success');
      await doSearch();
      return true;
    }
    return false;
  } catch (error: any) {
    console.error('배너 생성 실패:', error);
    await swal.swalAlert(error.response?.data?.message || '생성 중 오류가 발생했습니다.', 'error');
    return false;
  }
};

/**
 * 배너 수정
 */
export const updateBanner = async (payload: BannerUpdateRequest, doSearch: () => void) => {
  try {
    const formData = new FormData();

    // 필수 필드
    formData.append('banner_id', payload.banner_id.toString());

    // 선택 필드 (변경된 것만)
    if (payload.banner_name) formData.append('banner_name', payload.banner_name);
    if (payload.banner_type) formData.append('banner_type', payload.banner_type);
    if (payload.image_url) formData.append('image_url', payload.image_url);
    if (payload.link_url) formData.append('link_url', payload.link_url);
    if (payload.link_target) formData.append('link_target', payload.link_target);
    if (payload.display_order !== undefined && payload.display_order !== null) formData.append('display_order', payload.display_order.toString());
    if (payload.is_active !== undefined) formData.append('is_active', payload.is_active.toString());
    if (payload.valid_from) formData.append('valid_from', payload.valid_from);
    if (payload.valid_until) formData.append('valid_until', payload.valid_until);

    // 이미지 파일
    if (payload.image) {
      formData.append('image', payload.image);
    }

    const response = await http_json.post(bannerApi.updateBannerURL, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });

    if (response.data.success) {
      await swal.swalAlert('배너가 수정되었습니다.', 'success');
      await doSearch();
      return true;
    }
    return false;
  } catch (error: any) {
    console.error('배너 수정 실패:', error);
    await swal.swalAlert(error.response?.data?.message || '수정 중 오류가 발생했습니다.', 'error');
    return false;
  }
};

/**
 * 배너 정보 즉시 수정 (순서 변경, 노출 여부 토글)
 */
export const updateBannerQuick = async (banner: BannerItem, doSearch: () => void) => {
  const result = await swal.swalConfirm('정말 저장하시겠습니까?', 'warning');
  if (!result.isConfirmed) {
    await doSearch(); // 변경 취소시 원래대로 복원
    return false;
  }

  const payload: BannerUpdateRequest = {
    banner_id: banner.banner_id,
    display_order: banner.display_order,
    is_active: banner.is_active
  };

  return await updateBanner(payload, doSearch);
};

/**
 * 배너 삭제
 */
export const deleteBanner = async (banner_id: number) => {
  try {
    const response = await http.delete(bannerApi.deleteBannerURL, {
      params: { banner_id }
    });
    if (response.data.success) {
      await swal.swalAlert('배너가 삭제되었습니다.', 'success');
      return true;
    }
    return false;
  } catch (error: any) {
    console.error('배너 삭제 실패:', error);
    await swal.swalAlert(error.response?.data?.message || '삭제 중 오류가 발생했습니다.', 'error');
    return false;
  }
};
