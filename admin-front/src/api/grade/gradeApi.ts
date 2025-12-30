// 등급 API endpoint 정의
const proxyURL = '/api/v1/grades';

export const getGradeListURL = `${proxyURL}/list`;
export const getGradeDetailURL = `${proxyURL}/detail`;
export const createGradeURL = `${proxyURL}/create`;
export const updateGradeURL = `${proxyURL}/update`;
export const deleteGradeURL = `${proxyURL}/delete`;
export const getUsersByGradeURL = `${proxyURL}/users`;

// 등급 변경 로그 관련
export const getGradeChangeLogsListURL = `${proxyURL}/change-logs/list`;
export const executeMonthlyGradeUpdateURL = `${proxyURL}/monthly-update`;
