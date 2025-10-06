import http from '@/api/_config/http';
const proxyURL = '/api/exhibition';

export const getExhibitionListURL = `${proxyURL}/exhibitions`;
export const createExhibitionURL = `${proxyURL}/create-exhibition`;
export const updateExhibitionURL = `${proxyURL}/modify-exhibition`;

// 기획전 개별 조회
export async function getExhibition(idx) {
    return http.get(proxyURL+'/'+idx);
}

// 기획전 삭제
export async function deleteExhibition(idx) {
    return http.delete(proxyURL+'/'+idx);
}

// 기획전 삭제
export async function deleteExhibitionReply(idx) {
    return http.delete(proxyURL+'/reply/'+idx);
}

// 기획전 목록 조회
export async function getExhibitionList(data) {
    return http.post(getExhibitionListURL, data);
}

// 기획전 생성
export async function createExhibition(data, formData) {
    return http.post(createExhibitionURL, data, {
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
// 기획전 수정
export async function updateExhibition(data, formData) {
    return http.patch(updateExhibitionURL, data, {
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

