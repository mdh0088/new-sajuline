import http from '@/api/_config/http';
const proxyURL = '/api/popup';

export const getPopupListURL = `${proxyURL}/popups`;
export const createPopupURL = `${proxyURL}/create-popup`;
export const updatePopupURL = `${proxyURL}/modify-popup`;
export const getPopupOrderNoURL = `${proxyURL}/getPopupOrderNo`;

// 팝업 개별 조회
export async function getPopup(idx) {
    return http.get(proxyURL+'/'+idx);
}

// 팝업 삭제
export async function deletePopup(idx) {
    return http.delete(proxyURL+'/'+idx);
}

// 팝업 목록 조회
export async function getPopupList(data) {
    return http.post(getPopupListURL, data);
}

// 팝업 생성
export async function createPopup(data, formData) {
    return http.post(createPopupURL, data, {
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
// 팝업 정
export async function updatePopup(data, formData) {
    return http.patch(updatePopupURL, data, {
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
export async function getPopupOrderNo() {
    return http.post(getPopupOrderNoURL);
}


