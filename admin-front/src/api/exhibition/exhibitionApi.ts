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
    console.log('Creating exhibition with data:', data);
    Object.keys(data).forEach(key => {
        if (data[key] !== null && data[key] !== undefined) {
            console.log(`Appending ${key}:`, data[key], typeof data[key]);
            // Boolean 값은 문자열로 명시적 변환
            let value = data[key];
            if (typeof value === 'boolean') {
                value = value.toString();
            }
            formData.append(key, value);
        }
    });

    // FormData 내용 확인
    for (let pair of formData.entries()) {
        console.log(pair[0] + ': ' + pair[1]);
    }

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
            // Boolean 값은 문자열로 명시적 변환
            let value = data[key];
            if (typeof value === 'boolean') {
                value = value.toString();
            }
            formData.append(key, value);
        }
    });

    return http.patch(updateExhibitionURL, formData, {
        headers: {
            'Content-Type': 'multipart/form-data',
        }
    });
}

