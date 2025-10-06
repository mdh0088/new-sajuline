import * as swal from '@/commonUtils/swal';
import { useUserStore } from '@/store/user';
import { adminLogin } from '@/api/auth/authApi';
import type { LoginRequest } from '@/types/auth';

/**
 * 관리자 로그인 처리
 * - admin-backend의 /auth/admin/login API 호출
 * - 쿠키 기반 인증 (HttpOnly 쿠키 자동 설정)
 * @param router - Vue Router 인스턴스
 * @param loginInfo - 로그인 정보 (user_id, password)
 */
export const doLogin = async (router: any, loginInfo: { value: LoginRequest }) => {
    const userStore = useUserStore();

    try {
        // admin-backend의 /auth/admin/login API 호출
        const response = await adminLogin(loginInfo.value);

        console.log('Login response:', response);

        // axios 응답 구조: response.data에 실제 백엔드 응답이 있음
        const backendResponse = response.data;

        if (backendResponse.success && backendResponse.data) {
            // 사용자 정보 저장 (토큰은 쿠키로 자동 설정됨)
            userStore.setLogin({
                user_id: backendResponse.data.user_id,
                email: backendResponse.data.email,
                nickname: backendResponse.data.nickname
            });

            // 대시보드로 이동
            router.push('/dashboard');
        } else {
            // 로그인 실패
            const errorMessage = backendResponse.error?.message || backendResponse.message || '로그인에 실패했습니다.';
            swal.swalAlert(errorMessage, 'error');
        }
    } catch (error: any) {
        console.error('Login error:', error);

        // 에러 메시지 추출
        const errorMessage = error.response?.data?.error?.message
            || error.response?.data?.message
            || '로그인 중 오류가 발생했습니다.';

        swal.swalAlert(errorMessage, 'error');
    }
};