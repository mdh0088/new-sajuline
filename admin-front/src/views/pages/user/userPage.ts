import * as userApi from '@/api/user/userApi';
import * as swal from '@/commonUtils/swal';
import http from '@/api/_config/http';
import {Ref} from "vue";
import type {
    UserListParams,
    UserListItemResponse,
    UserDetailResponse,
    UserUpdateRequest,
    UserPointAdjustRequest,
    PointTransactionItem,
    NotificationLogItem
} from '@/types/user';
import type {TableOptions, SearchOptionsList} from '@/types/common';

/**
 * 사용자 목록 조회
 */
export const getUsersList = async (
    searchOptions: Ref<SearchOptionsList>,
    tableOptions: Ref<TableOptions<UserListItemResponse>>
): Promise<void> => {
    tableOptions.value.isLoading = true;

    try {
        // searchOptions에서 파라미터 추출
        const searchTypeOption = searchOptions.value.optionsList.find(opt => opt.key === 'search_type');
        const searchNameOption = searchOptions.value.optionsList.find(opt => opt.key === 'search_name');
        const joinTypeOption = searchOptions.value.optionsList.find(opt => opt.key === 'join_type');
        const gradeCodeOption = searchOptions.value.optionsList.find(opt => opt.key === 'grade_code');
        const dateValueOption = searchOptions.value.optionsList.find(opt => opt.key === 'date_value');

        // API 파라미터 구성
        const params: UserListParams = {
            page: tableOptions.value.currentPage || 1,
            limit: tableOptions.value.rowPage || 10,
            search_type: searchTypeOption?.value === 'all' ? 'all' : (searchTypeOption?.value || 'all'),
            search_name: searchNameOption?.value || null,
            join_type: joinTypeOption?.value === 'all' ? null : (joinTypeOption?.value || null),
            grade: gradeCodeOption?.value === 'all' ? null : (gradeCodeOption?.value || null),
            start_dt: Array.isArray(dateValueOption?.value) && dateValueOption.value.length > 0 ? dateValueOption.value[0] : null,
            end_dt: Array.isArray(dateValueOption?.value) && dateValueOption.value.length > 1 ? dateValueOption.value[1] : null,
        };

        // Query string 생성
        const queryParams = new URLSearchParams();
        queryParams.append('page', params.page.toString());
        queryParams.append('limit', params.limit.toString());
        queryParams.append('search_type', params.search_type);

        if (params.search_name) {
            queryParams.append('search_name', params.search_name);
        }

        if (params.join_type) {
            queryParams.append('join_type', params.join_type);
        }

        if (params.grade) {
            queryParams.append('grade', params.grade);
        }

        if (params.start_dt) {
            queryParams.append('start_dt', params.start_dt);
        }

        if (params.end_dt) {
            queryParams.append('end_dt', params.end_dt);
        }

        // API 호출
        const response = await http.get(`${userApi.getUsersListURL}?${queryParams.toString()}`);

        // Axios response 구조: response.data = 백엔드 응답 body
        // 백엔드 응답: { data: [...], meta: {...} }
        if (response.data) {
            tableOptions.value.items = response.data.data;  // 배열 데이터
            tableOptions.value.totalCnt = response.data.meta?.pagination?.total || 0;  // meta에서 total 가져오기
        }

    } catch (error) {
        console.error('사용자 목록 조회 실패:', error);
        swal.swalAlert('사용자 목록을 불러오는데 실패했습니다.', 'error');
    } finally {
        tableOptions.value.isLoading = false;
    }
};

/**
 * 사용자 상세 정보 조회
 */
export const getUserDetail = async (
    user_id: string
): Promise<UserDetailResponse | null> => {
    try {
        const response = await http.get(`${userApi.getUserDetailURL}?user_id=${user_id}`);

        if (response.data && response.data.data) {
            return response.data.data;
        }

        return null;
    } catch (error) {
        console.error('사용자 상세 조회 실패:', error);
        swal.swalAlert('사용자 정보를 불러오는데 실패했습니다.', 'error');
        return null;
    }
};

/**
 * 사용자 정보 수정
 */
export const updateUser = async (
    payload: UserUpdateRequest,
    doSearch?: () => void
): Promise<boolean> => {
    try {
        const response = await http.patch(userApi.updateUserURL, payload);

        if (response.data) {
            swal.swalAlert('저장되었습니다.', 'success');

            if (doSearch) {
                doSearch();
            }
            return true;
        }

        return false;
    } catch (error) {
        console.error('사용자 정보 수정 실패:', error);
        swal.swalAlert('저장에 실패했습니다.', 'error');
        return false;
    }
};

/**
 * 사용자 포인트 조정 (지급/차감)
 */
export const adjustUserPoints = async (
    payload: UserPointAdjustRequest,
    doSearch?: () => void
): Promise<boolean> => {
    try {
        const response = await http.post(userApi.adjustUserPointsURL, payload);

        if (response.data) {
            swal.swalAlert('포인트가 조정되었습니다.', 'success');

            if (doSearch) {
                doSearch();
            }
            return true;
        }

        return false;
    } catch (error) {
        console.error('포인트 조정 실패:', error);
        swal.swalAlert('포인트 조정에 실패했습니다.', 'error');
        return false;
    }
};

/**
 * 사용자 알리톡 로그 조회
 */
export const getUserNotificationLogs = async (
    user_id: string,
    tableOptions: Ref<TableOptions<NotificationLogItem>>
): Promise<void> => {
    try {
        const response = await http.get(`${userApi.getUserNotificationLogsURL}?user_id=${user_id}`);

        if (response.data && response.data.data) {
            tableOptions.value.items = response.data.data.logs || [];
        }
    } catch (error) {
        console.error('알리톡 로그 조회 실패:', error);
        swal.swalAlert('알리톡 로그를 불러오는데 실패했습니다.', 'error');
    }
};

/**
 * 사용자 마일리지 사용 내역 조회
 */
export const getMileageUseLogs = async (
    user_id: string,
    tableOptions: Ref<TableOptions<PointTransactionItem>>
): Promise<void> => {
    try {
        const response = await http.get(`${userApi.getMileageUseLogsURL}?user_id=${user_id}`);

        if (response.data && response.data.data) {
            tableOptions.value.items = response.data.data.items || [];
        }
    } catch (error) {
        console.error('마일리지 사용 내역 조회 실패:', error);
        swal.swalAlert('마일리지 사용 내역을 불러오는데 실패했습니다.', 'error');
    }
};

/**
 * 사용자 마일리지 적립 내역 조회
 */
export const getMileageEarnLogs = async (
    user_id: string,
    tableOptions: Ref<TableOptions<PointTransactionItem>>
): Promise<void> => {
    try {
        const response = await http.get(`${userApi.getMileageEarnLogsURL}?user_id=${user_id}`);

        if (response.data && response.data.data) {
            tableOptions.value.items = response.data.data.items || [];
        }
    } catch (error) {
        console.error('마일리지 적립 내역 조회 실패:', error);
        swal.swalAlert('마일리지 적립 내역을 불러오는데 실패했습니다.', 'error');
    }
};
