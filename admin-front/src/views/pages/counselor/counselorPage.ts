import * as promiseAction from '@/api/_config/promiseAction';
import * as counselorApi from '@/api/counselor/counselorApi';
import * as swal from '@/commonUtils/swal';
import http from '@/api/_config/http';
import {Ref} from "vue";
import {UploadUserFile} from "element-plus";
import type {
    CounselorListParams,
    CounselorListItem,
    CounselorFullDetailResponse,
    CounselorDetailUpdate,
    CounselorStateUpdateRequest
} from '@/types/counselor';

/**
 * 상담사 목록 조회
 */
export const getCounselorsList = async (
    searchOptions: Ref<Array<SearchOptions>>,
    tableOptions: Ref<TableOptions<CounselorListItem>>
): Promise<void> => {
    tableOptions.value.isLoading = true;

    try {
        // searchOptions에서 파라미터 추출
        const searchTypeOption = searchOptions.value.optionsList.find(opt => opt.key === 'search_type');
        const searchNameOption = searchOptions.value.optionsList.find(opt => opt.key === 'search_name');
        const specialtiesOption = searchOptions.value.optionsList.find(opt => opt.key === 'specialties');
        const isShowOption = searchOptions.value.optionsList.find(opt => opt.key === 'is_show');
        const isOutOption = searchOptions.value.optionsList.find(opt => opt.key === 'is_out');
        const dateValueOption = searchOptions.value.optionsList.find(opt => opt.key === 'date_value');

        // API 파라미터 구성
        const params: CounselorListParams = {
            page: tableOptions.value.currentPage || 1,
            limit: tableOptions.value.rowPage || 10,
            search_type: searchTypeOption?.value === 'all' ? 'all' : (searchTypeOption?.value || 'all'),
            search_name: searchNameOption?.value || null,
            specialties: specialtiesOption?.value === 'all' ? null : (specialtiesOption?.value ? [specialtiesOption.value] : null),
            is_show: isShowOption?.value === 'all' ? null : isShowOption?.value,
            is_out: isOutOption?.value === 'all' ? null : isOutOption?.value,
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

        if (params.specialties && params.specialties.length > 0) {
            params.specialties.forEach(specialty => {
                queryParams.append('specialties', specialty);
            });
        }

        if (params.is_show !== null && params.is_show !== undefined) {
            queryParams.append('is_show', params.is_show.toString());
        }

        if (params.is_out !== null && params.is_out !== undefined) {
            queryParams.append('is_out', params.is_out.toString());
        }

        if (params.start_dt) {
            queryParams.append('start_dt', params.start_dt);
        }

        if (params.end_dt) {
            queryParams.append('end_dt', params.end_dt);
        }

        // API 호출
        const response = await http.get(`${counselorApi.getCounselorsListURL}?${queryParams.toString()}`);

        // Axios response 구조: response.data = 백엔드 응답 body
        // 백엔드 응답: { data: [...], meta: {...} }
        if (response.data) {
            tableOptions.value.items = response.data.data;  // 배열 데이터
            tableOptions.value.totalCnt = response.data.meta?.pagination?.total || 0;  // meta에서 total 가져오기
        }

    } catch (error) {
        console.error('상담사 목록 조회 실패:', error);
        swal.swalAlert('상담사 목록을 불러오는데 실패했습니다.', 'error');
    } finally {
        tableOptions.value.isLoading = false;
    }
};

/**
 * 상담사 상세 정보 조회
 */
export const getCounselorDetail = async (
    counselor_id: string,
    mainfile?: Ref<UploadUserFile[]>
): Promise<CounselorFullDetailResponse | null> => {
    try {
        const response = await http.get(`${counselorApi.getCounselorDetailURL}?counselor_id=${counselor_id}`);

        if (response.data && response.data.data) {
            const data: CounselorFullDetailResponse = response.data.data;

            // 프로필 이미지 처리 - CDN 베이스 URL과 결합
            if (data.counselor.profile_image_url && mainfile) {
                const cdnBase = import.meta.env.VITE_APP_UPLOAD_URL;
                const imageUrl = data.counselor.profile_image_url.startsWith('http')
                    ? data.counselor.profile_image_url
                    : `${cdnBase}cs/${data.counselor.profile_image_url}`;

                mainfile.value = [{
                    name: data.counselor.profile_image_url.split('/').pop() || 'profile',
                    url: imageUrl
                }];
            }

            return data;
        }

        return null;
    } catch (error) {
        console.error('상담사 상세 조회 실패:', error);
        swal.swalAlert('상담사 정보를 불러오는데 실패했습니다.', 'error');
        return null;
    }
};

/**
 * 상담사 노출여부 수정 (간단 버전)
 */
export const updateCounselorShow = async (
    counselor_id: string,
    is_show: boolean,
    doSearch?: () => void
): Promise<void> => {
    try {
        const response = await http.patch(
            `${counselorApi.updateCounselorShowURL(counselor_id)}?is_show=${is_show}`
        );

        if (doSearch) {
            doSearch();
        }

    } catch (error) {
        console.error('노출여부 수정 실패:', error);
        swal.swalAlert('노출여부 수정에 실패했습니다.', 'error');
    }
};

/**
 * 상담사 정보 수정
 */
export const updateCounselorInfo = async (
    counselor_id: string,
    updateData: CounselorDetailUpdate,
    profile_image?: File | null,
    doSearch?: () => void
): Promise<boolean> => {
    try {
        const formData = new FormData();

        console.log('=== updateCounselorInfo 시작 ===');
        console.log('counselor_id:', counselor_id);
        console.log('updateData:', JSON.stringify(updateData, null, 2));
        console.log('profile_image:', profile_image);

        // 각 필드를 명시적으로 체크하고 추가
        if (updateData.is_show !== null && updateData.is_show !== undefined) {
            formData.append('is_show', String(updateData.is_show));
            console.log('✓ is_show:', updateData.is_show);
        }

        if (updateData.name) {
            formData.append('name', updateData.name);
            console.log('✓ name:', updateData.name);
        }

        if (updateData.nickname) {
            formData.append('nickname', updateData.nickname);
            console.log('✓ nickname:', updateData.nickname);
        }

        if (updateData.phone) {
            formData.append('phone', updateData.phone);
            console.log('✓ phone:', updateData.phone);
        }

        if (updateData.password) {
            formData.append('password', updateData.password);
            console.log('✓ password: [HIDDEN]');
        }

        if (updateData.specialties) {
            formData.append('specialties', updateData.specialties);
            console.log('✓ specialties:', updateData.specialties);
        }

        if (updateData.counselor_code) {
            formData.append('counselor_code', updateData.counselor_code);
            console.log('✓ counselor_code:', updateData.counselor_code);
        }

        if (updateData.grade) {
            formData.append('grade', updateData.grade);
            console.log('✓ grade:', updateData.grade);
        }

        if (updateData.after_amount !== null && updateData.after_amount !== undefined) {
            formData.append('after_amount', String(updateData.after_amount));
            console.log('✓ after_amount:', updateData.after_amount);
        }

        if (updateData.before_amount) {
            formData.append('before_amount', updateData.before_amount);
            console.log('✓ before_amount:', updateData.before_amount);
        }

        if (updateData.work_time) {
            formData.append('work_time', updateData.work_time);
            console.log('✓ work_time:', updateData.work_time);
        }

        if (updateData.is_new !== null && updateData.is_new !== undefined) {
            formData.append('is_new', String(updateData.is_new));
            console.log('✓ is_new:', updateData.is_new);
        }

        if (updateData.introduction_short !== null && updateData.introduction_short !== undefined) {
            formData.append('introduction_short', updateData.introduction_short);
            console.log('✓ introduction_short:', updateData.introduction_short);
        }

        if (updateData.greeting_message !== null && updateData.greeting_message !== undefined) {
            formData.append('greeting_message', updateData.greeting_message);
            console.log('✓ greeting_message:', updateData.greeting_message);
        }

        if (updateData.career_info !== null && updateData.career_info !== undefined) {
            formData.append('career_info', updateData.career_info);
            console.log('✓ career_info:', updateData.career_info);
        }

        if (updateData.keywords) {
            formData.append('keywords', updateData.keywords);
            console.log('✓ keywords:', updateData.keywords);
        }

        // 이미지 파일 추가
        if (profile_image) {
            formData.append('profile_image', profile_image);
            console.log('✓ profile_image:', profile_image.name);
        }

        console.log('=== FormData 최종 확인 ===');
        let fieldCount = 0;
        for (const [key, value] of formData.entries()) {
            console.log(`  ${key}:`, value);
            fieldCount++;
        }
        console.log(`총 ${fieldCount}개 필드 전송`);

        if (fieldCount === 0) {
            console.error('❌ FormData가 비어있습니다!');
            swal.swalAlert('전송할 데이터가 없습니다.', 'error');
            return false;
        }

        console.log('=== API 호출 시작 ===');
        const response = await http.patch(counselorApi.updateCounselorURL(counselor_id), formData);
        console.log('=== API 응답 ===');
        console.log('response.data:', response.data);

        swal.swalAlert('저장되었습니다.', 'success');

        if (doSearch) {
            doSearch();
        }

        return true;
    } catch (error) {
        console.error('❌ 상담사 정보 수정 실패:', error);
        swal.swalAlert('저장에 실패했습니다.', 'error');
        return false;
    }
};

/**
 * 상담사 상태 변경 (m_state)
 */
export const updateCounselorState = async (
    payload: CounselorStateUpdateRequest,
    doSearch?: () => void
): Promise<boolean> => {
    try {
        const response = await http.post(counselorApi.updateCounselorStateURL, payload);

        if (response.data?.data?.updated) {
            swal.swalAlert('상담사 상태가 변경되었습니다.', 'success');

            if (doSearch) {
                doSearch();
            }
            return true;
        } else {
            swal.swalAlert('상담사 상태 변경에 실패했습니다.', 'error');
            return false;
        }

    } catch (error) {
        console.error('상담사 상태 변경 실패:', error);
        swal.swalAlert('상담사 상태 변경에 실패했습니다.', 'error');
        return false;
    }
};
