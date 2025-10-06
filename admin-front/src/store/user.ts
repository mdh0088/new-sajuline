import {defineStore} from "pinia";
import {computed, ref} from 'vue';
import type { AdminInfo } from '@/types/auth';

/**
 * 사용자 스토어 (쿠키 기반 인증)
 * - 토큰은 HttpOnly 쿠키로 관리 (백엔드에서 자동 설정/삭제)
 * - 사용자 정보만 localStorage에 저장 (보안 강화)
 */
export const useUserStore = defineStore('user', () => {

    // localStorage에서 사용자 정보 읽기 (토큰은 쿠키로 관리)
    const userInfo = ref<AdminInfo | null>(
        localStorage.getItem('adminInfo')
            ? JSON.parse(localStorage.getItem('adminInfo')!)
            : null
    );

    const isLoggedIn = computed(() => userInfo.value !== null);

    const getUserInfo = computed(() => userInfo.value);

    /**
     * 로그인 성공 시 사용자 정보 저장
     * - 토큰은 백엔드의 HttpOnly 쿠키로 자동 설정됨
     * @param adminInfo - 관리자 정보 (user_id, email, nickname)
     */
    const setLogin = (adminInfo: AdminInfo) => {
        userInfo.value = adminInfo;
        localStorage.setItem('adminInfo', JSON.stringify(adminInfo));
    };

    /**
     * 로그아웃 처리
     * - localStorage의 사용자 정보 삭제
     * - 토큰은 백엔드 logout API 호출 시 쿠키에서 자동 삭제됨
     */
    const setLogout = () => {
        userInfo.value = null;
        localStorage.removeItem('adminInfo');
    };

    /**
     * 로그인 상태 체크
     * - 쿠키 기반 인증이므로 API 호출 시 백엔드에서 검증
     * - localStorage에 adminInfo가 있으면 로그인 상태로 간주
     */
    const checkLoginStatus = () => {
        const storedInfo = localStorage.getItem('adminInfo');
        if (!storedInfo) {
            setLogout();
            return false;
        }
        return true;
    };

    return {
        isLoggedIn,
        getUserInfo,
        setLogin,
        setLogout,
        checkLoginStatus
    }
},
    {
        persist: false
    });
