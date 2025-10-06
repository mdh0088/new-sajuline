import http from '@/api/_config/http';
const proxyURL = '/api/kakaoAlarm';


// 등급 개별 조회
export async function getUserKakaoAlarmHistory(idx: number) {
    return http.get(proxyURL+'/'+idx);
}
