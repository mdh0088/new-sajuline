import * as productApi from '@/api/product/productApi';
import * as swal from '@/commonUtils/swal';
import http from '@/api/_config/http';
import { Ref } from 'vue';
import type {
    PointProductItem,
    PointProductListResponse,
    PointProductCreateRequest,
    PointProductUpdateRequest,
    PointProductDeleteResponse,
} from '@/types/product';

/**
 * 포인트 상품 목록 조회
 */
export const getProductList = async (
    productList: Ref<PointProductItem[]>,
    isLoading: Ref<boolean>
): Promise<void> => {
    isLoading.value = true;

    try {
        const response = await http.get(productApi.getProductListURL);

        if (response.data && response.data.data) {
            const data: PointProductListResponse = response.data.data;
            productList.value = data.items;
        }
    } catch (error) {
        console.error('포인트 상품 목록 조회 실패:', error);
        swal.swalAlert('포인트 상품 목록을 불러오는데 실패했습니다.', 'error');
    } finally {
        isLoading.value = false;
    }
};

/**
 * 포인트 상품 생성
 */
export const createProduct = async (
    productData: PointProductCreateRequest,
    isLoading: Ref<boolean>
): Promise<boolean> => {
    try {
        isLoading.value = true;

        const response = await http.post(productApi.createProductURL, productData);

        if (response.data && response.data.success) {
            return true;
        }

        return false;
    } catch (error) {
        console.error('포인트 상품 생성 실패:', error);
        swal.swalAlert('포인트 상품 생성에 실패했습니다.', 'error');
        return false;
    } finally {
        isLoading.value = false;
    }
};

/**
 * 포인트 상품 수정
 */
export const updateProduct = async (
    productData: PointProductUpdateRequest,
    isLoading: Ref<boolean>
): Promise<boolean> => {
    try {
        isLoading.value = true;

        const response = await http.post(productApi.updateProductURL, productData);

        if (response.data && response.data.success) {
            return true;
        }

        return false;
    } catch (error) {
        console.error('포인트 상품 수정 실패:', error);
        swal.swalAlert('포인트 상품 수정에 실패했습니다.', 'error');
        return false;
    } finally {
        isLoading.value = false;
    }
};

/**
 * 포인트 상품 삭제
 */
export const deleteProductById = async (
    product_id: number,
    isLoading: Ref<boolean>
): Promise<boolean> => {
    try {
        isLoading.value = true;

        const response = await http.delete(`${productApi.deleteProductURL}?product_id=${product_id}`);

        if (response.data && response.data.data) {
            const data: PointProductDeleteResponse = response.data.data;
            if (data.updated) {
                return true;
            }
        }

        return false;
    } catch (error) {
        console.error('포인트 상품 삭제 실패:', error);
        swal.swalAlert('포인트 상품 삭제에 실패했습니다.', 'error');
        return false;
    } finally {
        isLoading.value = false;
    }
};
