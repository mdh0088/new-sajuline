import http from '@/api/_config/http';
import {modifyCounselorURL} from "@/api/counselor/counselorApi";
const proxyURL = '/api/banner';

export const getBannerListURL = `${proxyURL}/banners`;
export const getBannerOrderNoURL = `${proxyURL}/getBannerOrderNo`;
export const createBannerURL = `${proxyURL}/create-banner`;
export const updateBannerURL = `${proxyURL}/modify-banner`;

// 배너 개별 조회
export async function getBanner(idx) {
    return http.get(proxyURL+'/'+idx);
}

// 배너 삭제
export async function deleteBanner(idx) {
    return http.delete(proxyURL+'/'+idx);
}

// 배너 목록 조회
export async function getBannerList(data) {
    return http.post(getBannerListURL, data);
}


// 배너 생성
export async function createBanner(data, formData) {
    return http.post(createBannerURL, data, {
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

// 배너수 정
export async function updateBanner(data, formData) {
    return http.patch(updateBannerURL, data, {
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

// 배너 목록 조회
export async function getBannerOrderNo() {
    return http.post(getBannerOrderNoURL);
}

