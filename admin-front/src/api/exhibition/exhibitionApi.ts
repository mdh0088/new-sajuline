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
    // FormData에 각 필드를 개별적으로 추가
    Object.keys(data).forEach(key => {
        if (data[key] !== null && data[key] !== undefined) {
            formData.append(key, data[key]);
        }
    });

    return http.post(createExhibitionURL, formData, {
        headers: {
            'Content-Type': 'multipart/form-data',
        }
    });
}
// 기획전 수정
export async function updateExhibition(data, formData) {
    // FormData에 각 필드를 개별적으로 추가
    Object.keys(data).forEach(key => {
        if (data[key] !== null && data[key] !== undefined) {
            formData.append(key, data[key]);
        }
    });

    return http.patch(updateExhibitionURL, formData, {
        headers: {
            'Content-Type': 'multipart/form-data',
        }
    });
}

