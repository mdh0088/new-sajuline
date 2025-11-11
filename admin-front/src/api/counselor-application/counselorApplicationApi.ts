// 상담사 신청 API endpoint 정의
const proxyURL = '/api/v1/counselor-applications';

export const getCounselorApplicationsListURL = `${proxyURL}/list`;
export const getCounselorApplicationDetailURL = `${proxyURL}/detail`;
export const updateCounselorApplicationURL = (application_id: number) => `${proxyURL}/${application_id}`;
export const updateCounselorApplicationStatusURL = (application_id: number) => `${proxyURL}/${application_id}/status`;
