import http from '@/api/_config/http';
const proxyURL = '/api/review';
export const getCsReviewListURL = `${proxyURL}/cs-reviews`;
export const updateCsReviewURL = `${proxyURL}/modify-cs-review`;
export const getDumyReviewListURL = `${proxyURL}/cs-review-dumies`;
export const updateDumyReviewURL = `${proxyURL}/modify-cs-review-dumy`;


// 리뷰 개별 조회
export async function getCsReview(idx) {
    return http.get(proxyURL+'/cs-review/'+idx);
}

// 리뷰 삭제
export async function deleteCsReview(idx) {
    return http.delete(proxyURL+'/'+idx);
}

// 리뷰 목록 조회
export async function getCsReviewList(data) {
    return http.post(getCsReviewListURL, data);
}

// 리뷰 목록 조회
export async function updateCsReview(data) {
    return http.patch(updateCsReviewURL, data);
}



// 더미 리뷰 개별 조회
export async function getDumyReview(idx) {
    return http.get(proxyURL+'/cs-review-dumy/'+idx);
}

// 더미 리뷰 삭제
export async function deleteDumyReview(idx) {
    return http.delete(proxyURL+'/cs-review-dumy/'+idx);
}

// 더미 리뷰 목록 조회
export async function getDumyReviewList(data) {
    return http.post(getDumyReviewListURL, data);
}

// 더미 리뷰 목록 조회
export async function updateDumyReview(data) {
    return http.patch(updateDumyReviewURL, data);
}


