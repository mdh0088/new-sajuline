import * as paymentApi from '@/api/payment/paymentApi';
import * as swal from '@/commonUtils/swal';
import http from '@/api/_config/http';
import {Ref} from "vue";
import type {
    PaymentListParams,
    PaymentWithUserItem,
    PaymentDetailResponse
} from '@/types/payment';

/**
 * 결제 목록 조회
 */
export const getPaymentsList = async (
    searchOptions: Ref<Array<SearchOptions>>,
    tableOptions: Ref<TableOptions<any>>
): Promise<void> => {
    tableOptions.value.isLoading = true;

    try {
        // searchOptions에서 파라미터 추출
        const searchTypeOption = searchOptions.value.optionsList.find(opt => opt.key === 'search_type');
        const searchNameOption = searchOptions.value.optionsList.find(opt => opt.key === 'search_name');
        const paymentMethodOption = searchOptions.value.optionsList.find(opt => opt.key === 'payment_method');
        const paymentStatusOption = searchOptions.value.optionsList.find(opt => opt.key === 'payment_status');
        const amountOption = searchOptions.value.optionsList.find(opt => opt.key === 'amount');
        const dateValueOption = searchOptions.value.optionsList.find(opt => opt.key === 'date_value');

        // API 파라미터 구성
        const searchNameValue = searchNameOption?.value?.trim();
        const amountValue = amountOption?.value ? Number(amountOption.value) : undefined;

        const params: PaymentListParams = {
            page: tableOptions.value.currentPage || 1,
            limit: tableOptions.value.rowPage || 10,
            search_type: searchTypeOption?.value === 'all' ? 'all' : (searchTypeOption?.value || 'all'),
            search_name: searchNameValue || undefined,
            payment_method: paymentMethodOption?.value === 'all' ? undefined : paymentMethodOption?.value,
            payment_status: paymentStatusOption?.value === 'all' ? undefined : paymentStatusOption?.value,
            amount: amountValue,
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

        if (params.payment_method) {
            queryParams.append('payment_method', params.payment_method);
        }

        if (params.payment_status) {
            queryParams.append('payment_status', params.payment_status);
        }

        if (params.amount) {
            queryParams.append('amount', params.amount.toString());
        }

        if (params.start_dt) {
            queryParams.append('start_dt', params.start_dt);
        }

        if (params.end_dt) {
            queryParams.append('end_dt', params.end_dt);
        }

        // API 호출
        const response = await http.get(`${paymentApi.getPaymentListURL}?${queryParams.toString()}`);

        // 백엔드 응답: { data: [...], meta: {...} }
        if (response.data) {
            // 데이터 평탄화: payment와 user를 최상위 레벨로 합침
            const flattenedData = response.data.data.map((item: PaymentWithUserItem) => {
                const amount = Number(item.payment.amount || 0);
                return {
                    payment_id: String(item.payment.payment_id || ''),
                    order_no: String(item.payment.order_no || ''),
                    user_id: String(item.payment.user_id || ''),
                    amount: amount,
                    payment_method: String(item.payment.payment_method || ''),
                    payment_status: String(item.payment.payment_status || ''),
                    paid_at: item.payment.paid_at || null,
                    created_at: item.payment.created_at || null,
                    // 원본 데이터도 유지 (상세보기용)
                    payment: item.payment,
                    user: item.user
                };
            });

            tableOptions.value.items = flattenedData;
            tableOptions.value.totalCnt = response.data.meta?.pagination?.total || 0;
        }

    } catch (error) {
        console.error('결제 목록 조회 실패:', error);
        swal.swalAlert('결제 목록을 불러오는데 실패했습니다.', 'error');
    } finally {
        tableOptions.value.isLoading = false;
    }
};

/**
 * 결제 상세 정보 조회
 */
export const getPaymentDetail = async (
    payment_id: number,
    isLoading: Ref<boolean>
): Promise<PaymentDetailResponse | null> => {
    try {
        isLoading.value = true;

        const response = await http.get(`${paymentApi.getPaymentDetailURL}?payment_id=${payment_id}`);

        if (response.data && response.data.data) {
            return response.data.data;
        }

        return null;
    } catch (error) {
        console.error('결제 상세 조회 실패:', error);
        swal.swalAlert('결제 상세 정보를 불러오는데 실패했습니다.', 'error');
        return null;
    } finally {
        isLoading.value = false;
    }
};

/**
 * 결제 취소
 */
export const cancelPayment = async (
    payment_id: number,
    refreshCallback?: () => Promise<void>
): Promise<boolean> => {
    try {
        // 확인 팝업
        const confirmed = await swal.swalConfirm(
            '결제를 취소하시겠습니까?',
            '취소된 결제는 복구할 수 없습니다.',
            'warning'
        );

        if (!confirmed) {
            return false;
        }

        // API 호출
        const response = await http.post(`${paymentApi.cancelPaymentURL}?payment_id=${payment_id}`);

        if (response.data && response.data.success) {
            await swal.swalAlert('결제가 취소되었습니다.', 'success');

            // 목록 새로고침
            if (refreshCallback) {
                await refreshCallback();
            }

            return true;
        } else {
            await swal.swalAlert('결제 취소에 실패했습니다.', 'error');
            return false;
        }
    } catch (error: any) {
        console.error('결제 취소 실패:', error);
        const errorMessage = error.response?.data?.message || '결제 취소 중 오류가 발생했습니다.';
        await swal.swalAlert(errorMessage, 'error');
        return false;
    }
};
