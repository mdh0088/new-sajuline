// 상담사 API endpoint 정의
const proxyURL = '/api/v1/counselors';

export const getCounselorsListURL = `${proxyURL}/list`;
export const getCounselorsAllURL = `${proxyURL}/all`;  // 전체 상담사 목록 (셀렉트박스용)
export const getCounselorDetailURL = `${proxyURL}/detail`;
export const updateCounselorURL = (counselor_id: string) => `${proxyURL}/${counselor_id}`;
export const updateCounselorShowURL = (counselor_id: string) => `${proxyURL}/${counselor_id}/show`;
export const updateCounselorStateURL = `${proxyURL}/state`;
