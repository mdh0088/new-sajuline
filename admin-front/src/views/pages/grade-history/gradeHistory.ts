/**
 * 등급 변경 이력 관리 서비스 함수
 * 백엔드 API: /api/v1/grades/change-logs/list
 */

import http from '@/api/_config/http';
import http_json from '@/api/_config/http_json';
import * as gradeApi from '@/api/grade/gradeApi';
import * as swal from '@/commonUtils/swal';

export interface GradeChangeLogItem {
    log_id: number;
    user_id: string;
    grade_before: string;
    grade_after: string;
    purchase_amount: number;
    change_reason: string;
    admin_id: number | null;
    created_at: string;
}

export interface GradeChangeLogListResponse {
    logs: GradeChangeLogItem[];
    total: number;
    page: number;
    size: number;
}

export interface MonthlyGradeUpdateRequest {
    target_year?: number;
    target_month?: number;
    dry_run: boolean;
}

export interface MonthlyGradeUpdateResponse {
    target_year: number;
    target_month: number;
    total_active_users: number;
    total_processed: number;
    total_upgraded: number;
    total_downgraded: number;
    total_unchanged: number;
    dry_run: boolean;
    executed_at: string;
    results: Array<{
        user_id: string;
        grade_before: string;
        grade_after: string;
        purchase_amount: number;
        is_changed: boolean;
    }>;
}

/**
 * 등급 변경 로그 목록 조회
 */
export const getGradeChangeLogsList = async (searchOptions: any, tableOptions: any) => {
    try {
        tableOptions.value.isLoading = true;

        // 검색 파라미터 추출
        const year = searchOptions.value.getOptionByKey('year')?.value;
        const month = searchOptions.value.getOptionByKey('month')?.value;
        const user_id = searchOptions.value.getOptionByKey('user_id')?.value;
        const change_reason = searchOptions.value.getOptionByKey('change_reason')?.value;

        const params: any = {
            page: tableOptions.value.currentPage,
            size: tableOptions.value.rowPage
        };

        // 연도는 항상 전달
        if (year) {
            params.year = year;
        }

        // 월은 값이 있을 때만 전달
        if (month !== '' && month !== null && month !== undefined) {
            params.month = month;
        }

        // 사용자 ID
        if (user_id) {
            params.user_id = user_id;
        }

        // 변경 사유
        if (change_reason) {
            params.change_reason = change_reason;
        }

        const response = await http.get(gradeApi.getGradeChangeLogsListURL, { params });

        if (response.data.success) {
            const data: GradeChangeLogListResponse = response.data.data;
            tableOptions.value.items = data.logs;
            tableOptions.value.totalCnt = data.total;
        }
    } catch (error: any) {
        console.error('등급 변경 로그 목록 조회 실패:', error);
        await swal.swalAlert(error.response?.data?.message || '목록 조회 중 오류가 발생했습니다.', 'error');
    } finally {
        tableOptions.value.isLoading = false;
    }
};

/**
 * 월별 등급 업데이트 실행
 */
export const executeMonthlyGradeUpdate = async (
    targetYear: number,
    targetMonth: number,
    dryRun: boolean = false,
    doSearch?: () => void
): Promise<MonthlyGradeUpdateResponse | null> => {
    try {
        const confirmMessage = dryRun
            ? `${targetYear}년 ${targetMonth}월 기준 등급 업데이트를 테스트 실행하시겠습니까?\n(실제 데이터는 변경되지 않습니다)`
            : `${targetYear}년 ${targetMonth}월 기준 등급 업데이트를 실행하시겠습니까?\n\n주의: 실제 사용자 등급이 변경됩니다!`;

        const result = await swal.swalConfirm(confirmMessage, dryRun ? 'info' : 'warning');
        if (!result.isConfirmed) {
            return null;
        }

        const payload: MonthlyGradeUpdateRequest = {
            target_year: targetYear,
            target_month: targetMonth,
            dry_run: dryRun
        };

        const response = await http_json.post(gradeApi.executeMonthlyGradeUpdateURL, payload);

        if (response.data.success) {
            const data: MonthlyGradeUpdateResponse = response.data.data;

            const resultMessage = dryRun
                ? `[테스트 결과]\n전체 사용자: ${data.total_active_users}명\n등급 상승: ${data.total_upgraded}명\n등급 하락: ${data.total_downgraded}명\n등급 유지: ${data.total_unchanged}명`
                : `등급 업데이트가 완료되었습니다.\n\n등급 상승: ${data.total_upgraded}명\n등급 하락: ${data.total_downgraded}명\n등급 유지: ${data.total_unchanged}명`;

            await swal.swalAlert(resultMessage, 'success');

            // 목록 새로고침
            if (doSearch) {
                await doSearch();
            }

            return data;
        }

        return null;
    } catch (error: any) {
        console.error('월별 등급 업데이트 실행 실패:', error);
        await swal.swalAlert(error.response?.data?.message || '등급 업데이트 중 오류가 발생했습니다.', 'error');
        return null;
    }
};
