/**
 * 마일리지 상품 API
 * 백엔드 API: /api/v1/mileage
 */
import http from '@/api/_config/http';

const proxyURL = '/api/v1/mileage';

// API URL 상수
export const getMileageProductListURL = `${proxyURL}/list`;
export const getMileageProductDetailURL = `${proxyURL}`;
export const createMileageProductURL = `${proxyURL}/create`;
export const updateMileageProductURL = `${proxyURL}`;
export const deleteMileageProductURL = `${proxyURL}`;

/**
 * 마일리지 상품 목록 조회 (페이징)
 */
export async function getMileageProductList(params: { page: number; limit: number }) {
    return http.get(getMileageProductListURL, { params });
}

/**
 * 마일리지 상품 상세 조회
 */
export async function getMileageProductDetail(mileage_id: number) {
    return http.get(`${getMileageProductDetailURL}/${mileage_id}`);
}

/**
 * 마일리지 상품 생성
 */
export async function createMileageProduct(data: any, formData: FormData) {
    return http.post(createMileageProductURL, data, {
        headers: {
            'Content-Type': 'multipart/form-data',
        },
        params: {
            'dataType': 'formData'
        },
        env: {
            FormData: formData
        } as any
    });
}

/**
 * 마일리지 상품 수정
 */
export async function updateMileageProduct(mileage_id: number, data: any, formData: FormData) {
    return http.put(`${updateMileageProductURL}/${mileage_id}`, data, {
        headers: {
            'Content-Type': 'multipart/form-data',
        },
        params: {
            'dataType': 'formData'
        },
        env: {
            FormData: formData
        } as any
    });
}

/**
 * 마일리지 상품 삭제
 */
export async function deleteMileageProduct(mileage_id: number) {
    return http.delete(`${deleteMileageProductURL}/${mileage_id}`);
}
