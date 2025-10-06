import * as gradeApi from '@/api/grade/gradeApi';
import * as swal from '@/commonUtils/swal';
import http from '@/api/_config/http';
import {Ref} from "vue";
import {UploadUserFile} from "element-plus";
import type {
    GradeItem,
    GradeListResponse,
    GradeDetailResponse,
    GradeCreateRequest,
    GradeUpdateRequest,
    GradeDeleteResponse,
    UsersByGradeResponse
} from '@/types/grade';

/**
 * 등급 목록 조회
 */
export const getGradesList = async (
    tableOptions: Ref<TableOptions<GradeItem>>
): Promise<void> => {
    tableOptions.value.isLoading = true;

    try {
        const response = await http.get(gradeApi.getGradeListURL);

        if (response.data && response.data.data) {
            const data: GradeListResponse = response.data.data;
            tableOptions.value.items = data.grades;
            tableOptions.value.totalCnt = data.total || 0;
        }

    } catch (error) {
        console.error('등급 목록 조회 실패:', error);
        swal.swalAlert('등급 목록을 불러오는데 실패했습니다.', 'error');
    } finally {
        tableOptions.value.isLoading = false;
    }
};

/**
 * 등급 상세 정보 조회
 */
export const getGradeDetail = async (
    grade_code: string,
    gradeImageFile?: Ref<UploadUserFile[]>
): Promise<GradeItem | null> => {
    try {
        const response = await http.get(`${gradeApi.getGradeDetailURL}?grade_code=${grade_code}`);

        if (response.data && response.data.data) {
            const data: GradeDetailResponse = response.data.data;

            // 등급 이미지 처리 - CDN 베이스 URL과 결합
            if (data.grade.grade_image_url && gradeImageFile) {
                const cdnBase = import.meta.env.VITE_APP_UPLOAD_URL;
                const imageUrl = data.grade.grade_image_url.startsWith('http')
                    ? data.grade.grade_image_url
                    : `${cdnBase}grade/${data.grade.grade_image_url}`;

                gradeImageFile.value = [{
                    name: data.grade.grade_image_url.split('/').pop() || 'grade',
                    url: imageUrl
                }];
            }

            // 숫자 타입 변환 (백엔드에서 문자열로 올 수 있음)
            return {
                ...data.grade,
                grade_level: Number(data.grade.grade_level),
                min_purchase_amount: Number(data.grade.min_purchase_amount),
                point_earn_rate: Number(data.grade.point_earn_rate),
                discount_rate: Number(data.grade.discount_rate),
            };
        }

        return null;
    } catch (error) {
        console.error('등급 상세 조회 실패:', error);
        swal.swalAlert('등급 정보를 불러오는데 실패했습니다.', 'error');
        return null;
    }
};

/**
 * 등급 생성
 */
export const createGrade = async (
    gradeData: GradeCreateRequest,
    grade_image?: File | null,
    doSearch?: () => void
): Promise<boolean> => {
    try {
        const formData = new FormData();

        // 필수 필드
        formData.append('grade_code', gradeData.grade_code);
        formData.append('grade_name', gradeData.grade_name);
        formData.append('grade_level', String(gradeData.grade_level));
        formData.append('min_purchase_amount', String(gradeData.min_purchase_amount));
        formData.append('point_earn_rate', String(gradeData.point_earn_rate));
        formData.append('discount_rate', String(gradeData.discount_rate));

        // 선택 필드
        if (gradeData.benefits) {
            formData.append('benefits', JSON.stringify(gradeData.benefits));
        }

        if (gradeData.description) {
            formData.append('description', gradeData.description);
        }

        if (gradeData.is_active !== null && gradeData.is_active !== undefined) {
            formData.append('is_active', String(gradeData.is_active));
        }

        // 이미지 파일
        if (grade_image) {
            formData.append('grade_image', grade_image);
        }

        const response = await http.post(gradeApi.createGradeURL, formData, {
            headers: {
                'Content-Type': 'multipart/form-data',
            },
        });

        swal.swalAlert('등급이 생성되었습니다.', 'success');

        if (doSearch) {
            doSearch();
        }

        return true;
    } catch (error) {
        console.error('등급 생성 실패:', error);
        swal.swalAlert('등급 생성에 실패했습니다.', 'error');
        return false;
    }
};

/**
 * 등급 수정
 */
export const updateGrade = async (
    grade_code: string,
    gradeData: GradeUpdateRequest,
    grade_image?: File | null,
    doSearch?: () => void
): Promise<boolean> => {
    try {
        const formData = new FormData();

        formData.append('grade_code', grade_code);

        if (gradeData.grade_name) {
            formData.append('grade_name', gradeData.grade_name);
        }

        if (gradeData.grade_level !== null && gradeData.grade_level !== undefined) {
            formData.append('grade_level', String(gradeData.grade_level));
        }

        if (gradeData.min_purchase_amount !== null && gradeData.min_purchase_amount !== undefined) {
            formData.append('min_purchase_amount', String(gradeData.min_purchase_amount));
        }

        if (gradeData.point_earn_rate !== null && gradeData.point_earn_rate !== undefined) {
            formData.append('point_earn_rate', String(gradeData.point_earn_rate));
        }

        if (gradeData.discount_rate !== null && gradeData.discount_rate !== undefined) {
            formData.append('discount_rate', String(gradeData.discount_rate));
        }

        if (gradeData.benefits) {
            formData.append('benefits', JSON.stringify(gradeData.benefits));
        }

        if (gradeData.description !== null && gradeData.description !== undefined) {
            formData.append('description', gradeData.description);
        }

        if (gradeData.is_active !== null && gradeData.is_active !== undefined) {
            formData.append('is_active', String(gradeData.is_active));
        }

        if (grade_image) {
            formData.append('grade_image', grade_image);
        }

        const response = await http.post(gradeApi.updateGradeURL, formData, {
            headers: {
                'Content-Type': 'multipart/form-data',
            },
        });

        swal.swalAlert('등급이 수정되었습니다.', 'success');

        if (doSearch) {
            doSearch();
        }

        return true;
    } catch (error) {
        console.error('등급 수정 실패:', error);
        swal.swalAlert('등급 수정에 실패했습니다.', 'error');
        return false;
    }
};

/**
 * 등급 삭제
 */
export const deleteGrade = async (
    grade_code: string,
    doSearch?: () => void
): Promise<boolean> => {
    try {
        const response = await http.delete(`${gradeApi.deleteGradeURL}?grade_code=${grade_code}`);

        if (response.data && response.data.data) {
            const data: GradeDeleteResponse = response.data.data;
            if (data.deleted) {
                swal.swalAlert('등급이 삭제되었습니다.', 'success');

                if (doSearch) {
                    doSearch();
                }
                return true;
            }
        }

        swal.swalAlert('등급 삭제에 실패했습니다.', 'error');
        return false;
    } catch (error) {
        console.error('등급 삭제 실패:', error);
        swal.swalAlert('등급 삭제에 실패했습니다.', 'error');
        return false;
    }
};

/**
 * 등급별 유저 목록 조회
 */
export const getUsersByGrade = async (
    grade_code: string
): Promise<UsersByGradeResponse | null> => {
    try {
        const response = await http.get(`${gradeApi.getUsersByGradeURL}?grade_code=${grade_code}`);

        if (response.data && response.data.data) {
            return response.data.data as UsersByGradeResponse;
        }

        return null;
    } catch (error) {
        console.error('등급별 유저 조회 실패:', error);
        swal.swalAlert('등급별 유저 목록을 불러오는데 실패했습니다.', 'error');
        return null;
    }
};
