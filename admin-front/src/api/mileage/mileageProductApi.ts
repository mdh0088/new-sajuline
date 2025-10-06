import http from '@/api/_config/http';
const proxyURL = '/api/mileage';

export const getMileageProductListURL = `${proxyURL}/mileage-products`;
export const createMileageProductURL = `${proxyURL}/create-mileage-product`;
export const updateMileageProductURL = `${proxyURL}/modify-mileage-product`;

export const getUserMileageSaveListURL = `${proxyURL}/user-mileage-save-list`;
export const getUserMileageUsageListURL = `${proxyURL}/user-mileage-usage-list`;


// 등급 개별 조회
export async function getMileageProduct(mileage_product_idx) {
    return http.get(proxyURL+'/mileage-product/'+mileage_product_idx);
}

// 등급 목록 조회
export async function getMileageProductList(data) {
    return http.post(getMileageProductListURL, data);
}

// 등급 생성
export async function createMileageProduct(data, formData) {
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

// 등급 수정
export async function updateMileageProduct(data, formData) {
    return http.patch(updateMileageProductURL, data, {
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

export async function getUserMileageSaveList(user_id:string) {
    return http.get(getUserMileageSaveListURL+'/'+user_id);
}

export async function getUserMileageUsageList(user_id:string) {
    return http.get(getUserMileageUsageListURL+'/'+user_id);
}

