import * as noticeApi from '@/api/notice/noticeApi';
import * as swal from '@/commonUtils/swal';
import http from '@/api/_config/http';
import {Ref} from "vue";
import type {
    NoticeListParams,
    NoticeListItem,
    NoticeDetailResponse,
    NoticeCreateRequest,
    NoticeUpdateRequest
} from '@/types/notice';

/**
 * 공지사항 목록 조회
 */
export const getNoticesList = async (
    searchOptions: Ref<Array<SearchOptions>>,
    tableOptions: Ref<TableOptions<any>>
): Promise<void> => {
    tableOptions.value.isLoading = true;

    try {
        // searchOptions에서 파라미터 추출
        const searchTypeOption = searchOptions.value.optionsList.find(opt => opt.key === 'search_type');
        const searchNameOption = searchOptions.value.optionsList.find(opt => opt.key === 'search_name');
        const targetAudienceOption = searchOptions.value.optionsList.find(opt => opt.key === 'target_audience');
        const isImportantOption = searchOptions.value.optionsList.find(opt => opt.key === 'is_important');
        const isActiveOption = searchOptions.value.optionsList.find(opt => opt.key === 'is_active');
        const dateValueOption = searchOptions.value.optionsList.find(opt => opt.key === 'date_value');

        // API 파라미터 구성
        const searchNameValue = searchNameOption?.value?.trim();

        const params: NoticeListParams = {
            page: tableOptions.value.currentPage || 1,
            limit: tableOptions.value.rowPage || 10,
            search_type: searchTypeOption?.value === 'all' ? 'all' : (searchTypeOption?.value || 'all'),
            search_name: searchNameValue || undefined,
            target_audience: targetAudienceOption?.value === 'all' ? undefined : targetAudienceOption?.value,
            is_important: isImportantOption?.value === 'all' ? undefined : isImportantOption?.value,
            is_active: isActiveOption?.value === 'all' ? undefined : isActiveOption?.value,
            start_dt: Array.isArray(dateValueOption?.value) && dateValueOption.value.length > 0 ? dateValueOption.value[0] : undefined,
            end_dt: Array.isArray(dateValueOption?.value) && dateValueOption.value.length > 1 ? dateValueOption.value[1] : undefined,
        };

        // Query string 생성
        const queryParams = new URLSearchParams();
        queryParams.append('page', params.page.toString());
        queryParams.append('limit', params.limit.toString());
        queryParams.append('search_type', params.search_type);

        if (params.search_name) {
            queryParams.append('search_name', params.search_name);
        }

        if (params.target_audience) {
            queryParams.append('target_audience', params.target_audience);
        }

        if (params.is_important !== undefined) {
            queryParams.append('is_important', params.is_important.toString());
        }

        if (params.is_active !== undefined) {
            queryParams.append('is_active', params.is_active.toString());
        }

        if (params.start_dt) {
            queryParams.append('start_dt', params.start_dt);
        }

        if (params.end_dt) {
            queryParams.append('end_dt', params.end_dt);
        }

        // API 호출
        const response = await http.get(`${noticeApi.getNoticeListURL}?${queryParams.toString()}`);

        // 백엔드 응답: { data: [...], meta: {...} }
        if (response.data) {
            tableOptions.value.items = response.data.data || [];
            tableOptions.value.totalCnt = response.data.meta?.pagination?.total || 0;
        }

    } catch (error) {
        console.error('공지사항 목록 조회 실패:', error);
        swal.swalAlert('공지사항 목록을 불러오는데 실패했습니다.', 'error');
    } finally {
        tableOptions.value.isLoading = false;
    }
};

/**
 * 공지사항 상세 정보 조회
 */
export const getNoticeDetail = async (
    notice_id: number,
    isLoading: Ref<boolean>
): Promise<NoticeDetailResponse | null> => {
    try {
        isLoading.value = true;

        const response = await http.get(`${noticeApi.getNoticeDetailURL}?notice_id=${notice_id}`);

        if (response.data && response.data.data) {
            return response.data.data;
        }

        return null;
    } catch (error) {
        console.error('공지사항 상세 조회 실패:', error);
        swal.swalAlert('공지사항 상세 정보를 불러오는데 실패했습니다.', 'error');
        return null;
    } finally {
        isLoading.value = false;
    }
};

/**
 * 공지사항 등록
 */
export const createNotice = async (
    requestData: NoticeCreateRequest,
    doSearch?: () => Promise<void>
): Promise<boolean> => {
    try {
        // 전체 로딩 시작
        const { ElLoading } = await import('element-plus');
        const loading = ElLoading.service({
            lock: true,
            text: '공지사항 등록 중...',
            background: 'rgba(0, 0, 0, 0.7)',
        });

        try {
            // API 호출
            const response = await http.post(noticeApi.createNoticeURL, requestData);

            if (response.data && response.data.success) {
                await swal.swalAlert('공지사항이 등록되었습니다.', 'success');

                // 목록 새로고침
                if (doSearch) {
                    await doSearch();
                }

                return true;
            } else {
                await swal.swalAlert('공지사항 등록에 실패했습니다.', 'error');
                return false;
            }
        } finally {
            // 전체 로딩 종료
            loading.close();
        }
    } catch (error: any) {
        console.error('공지사항 등록 실패:', error);
        const errorMessage = error.response?.data?.message || '공지사항 등록 중 오류가 발생했습니다.';
        await swal.swalAlert(errorMessage, 'error');
        return false;
    }
};

/**
 * 공지사항 수정
 */
export const updateNotice = async (
    requestData: NoticeUpdateRequest,
    doSearch?: () => Promise<void>
): Promise<boolean> => {
    try {
        // 전체 로딩 시작
        const { ElLoading } = await import('element-plus');
        const loading = ElLoading.service({
            lock: true,
            text: '공지사항 수정 중...',
            background: 'rgba(0, 0, 0, 0.7)',
        });

        try {
            // API 호출
            const response = await http.post(noticeApi.updateNoticeURL, requestData);

            if (response.data && response.data.success) {
                await swal.swalAlert('공지사항이 수정되었습니다.', 'success');

                // 목록 새로고침
                if (doSearch) {
                    await doSearch();
                }

                return true;
            } else {
                await swal.swalAlert('공지사항 수정에 실패했습니다.', 'error');
                return false;
            }
        } finally {
            // 전체 로딩 종료
            loading.close();
        }
    } catch (error: any) {
        console.error('공지사항 수정 실패:', error);
        const errorMessage = error.response?.data?.message || '공지사항 수정 중 오류가 발생했습니다.';
        await swal.swalAlert(errorMessage, 'error');
        return false;
    }
};

/**
 * 공지사항 삭제
 */
export const deleteNotice = async (
    notice_id: number,
    doSearch?: () => Promise<void>
): Promise<boolean> => {
    try {
        // 확인 팝업
        const result = await swal.swalConfirm(
            '공지사항을 삭제하시겠습니까?\n삭제된 공지사항은 복구할 수 없습니다.',
            'warning'
        );

        if (!result.isConfirmed) {
            return false;
        }

        // 전체 로딩 시작
        const { ElLoading } = await import('element-plus');
        const loading = ElLoading.service({
            lock: true,
            text: '공지사항 삭제 중...',
            background: 'rgba(0, 0, 0, 0.7)',
        });

        try {
            // API 호출
            const response = await http.delete(`${noticeApi.deleteNoticeURL}?notice_id=${notice_id}`);

            if (response.data && response.data.success) {
                await swal.swalAlert('공지사항이 삭제되었습니다.', 'success');

                // 목록 새로고침
                if (doSearch) {
                    await doSearch();
                }

                return true;
            } else {
                await swal.swalAlert('공지사항 삭제에 실패했습니다.', 'error');
                return false;
            }
        } finally {
            // 전체 로딩 종료
            loading.close();
        }
    } catch (error: any) {
        console.error('공지사항 삭제 실패:', error);
        const errorMessage = error.response?.data?.message || '공지사항 삭제 중 오류가 발생했습니다.';
        await swal.swalAlert(errorMessage, 'error');
        return false;
    }
};

/**
 * 공지사항 활성 상태 변경
 */
export const updateNoticeActiveStatus = async (
    notice_id: number,
    is_active: boolean,
    doSearch?: () => Promise<void>
): Promise<boolean> => {
    try {
        // 전체 로딩 시작
        const { ElLoading } = await import('element-plus');
        const loading = ElLoading.service({
            lock: true,
            text: '상태 변경 중...',
            background: 'rgba(0, 0, 0, 0.7)',
        });

        try {
            // API 호출
            const requestData: NoticeUpdateRequest = {
                notice_id: notice_id,
                is_active: is_active,
            };

            const response = await http.post(noticeApi.updateNoticeURL, requestData);

            if (response.data && response.data.success) {
                await swal.swalAlert('활성 상태가 변경되었습니다.', 'success');

                // 목록 새로고침
                if (doSearch) {
                    await doSearch();
                }

                return true;
            } else {
                await swal.swalAlert('활성 상태 변경에 실패했습니다.', 'error');
                return false;
            }
        } finally {
            // 전체 로딩 종료
            loading.close();
        }
    } catch (error: any) {
        console.error('활성 상태 변경 실패:', error);
        const errorMessage = error.response?.data?.message || '활성 상태 변경 중 오류가 발생했습니다.';
        await swal.swalAlert(errorMessage, 'error');
        return false;
    }
};
