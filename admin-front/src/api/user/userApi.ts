// 사용자 API endpoint 정의
const proxyURL = '/api/v1/users';

export const getUsersListURL = `${proxyURL}/list`;
export const getUserDetailURL = `${proxyURL}/detail`;
export const updateUserURL = `${proxyURL}/update`;
export const adjustUserPointsURL = `${proxyURL}/points/adjust`;
export const getUserNotificationLogsURL = `${proxyURL}/notification-logs`;
export const getMileageUseLogsURL = `${proxyURL}/mileage/use-logs`;
export const getMileageEarnLogsURL = `${proxyURL}/mileage/earn-logs`;
