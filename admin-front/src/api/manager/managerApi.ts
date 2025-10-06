import http from '@/api/_config/http';
const proxyURL = '/api/manager';
export const modifyMnagerURL = `${proxyURL}/modify-manager`;

// 로그인 처리
export async function modifyMnager(data) {
    return http.patch(modifyMnagerURL, data);
}