import axios from 'axios';
import * as swal from '@/commonUtils/swal';
import * as crypto from '@/commonUtils/crypto';

const instance = axios.create({});
instance.defaults.headers.common['Access-Control-Allow-Origin'] = '*';
instance.defaults.timeout = 120000;
instance.defaults.headers.post['Content-Type'] = 'application/json';
// PATCH는 FormData도 사용하므로 기본값 설정하지 않음 (axios가 자동 감지)
// instance.defaults.headers.patch['Content-Type'] = 'application/json';
// instance.defaults.headers.post['Content-Type'] =
//     'application/x-www-form-urlencoded';

// 캐싱 방지
instance.defaults.headers.get['Cache-Control'] = 'no-cache';
instance.defaults.headers.get['Pragma'] = 'no-cache';

// 요청 인터셉터 추가
const excludedUrls = ['/auth/admin/login', '/auth/counselor/login']; // 인증 불필요 URL

instance.interceptors.request.use(
    async function (config) {
        // 쿠키 기반 인증: HttpOnly 쿠키가 자동으로 전송됨
        // Authorization 헤더 설정 불필요

        // managerId 자동 추가 (로그인된 경우)
        const adminInfoStr = localStorage.getItem('adminInfo');
        let managerId = '';

        if (adminInfoStr) {
            try {
                const adminInfo = JSON.parse(adminInfoStr);
                managerId = adminInfo.user_id || '';
            } catch (error) {
                console.error('Failed to parse admin info:', error);
            }
        }

        // 추가 변수 적용
        if (config.params) {
            if(config.params['dataType'] === 'formData'){

                let formData = config.env.FormData; // 파일을 미리 담은 formData를 가져옴
                // JSON 데이터를 Blob 형태로 FormData에 추가
                formData.append("json_data", JSON.stringify(config.data));
/*
                // 이미지 파일 추가
                if (config.data.imgUpload) {
                    formData.append("imgUpload", config.data.imgUpload);
                }
                if (config.data.img1Upload) {
                    formData.append("img1Upload", config.data.img1Upload);
                }
                if (config.data.img2Upload) {
                    formData.append("img2Upload", config.data.img2Upload);
                }
                if (config.data.img3Upload) {
                    formData.append("img3Upload", config.data.img3Upload);
                }
                if (config.data.img4Upload) {
                    formData.append("img4Upload", config.data.img4Upload);
                }
                if (config.data.img5Upload) {
                    formData.append("img5Upload", config.data.img5Upload);
                }*/

                config.data = formData;
            }
        } else {
            if (config.data && managerId) {
                // FormData인 경우 JSON 변환하지 않음
                if (config.data instanceof FormData) {
                    config.data.append('managerId', managerId);
                } else {
                    if (typeof config.data === 'string') {
                        config.data = JSON.parse(config.data); // JSON 문자열인 경우 객체로 변환
                    }
                    config.data.managerId = managerId;
                    config.data = JSON.stringify(config.data);
                }
            }
        }

        console.log('config>>',config)
        return config;
    },
    function (error) {
        return Promise.reject(error);
    }
);

// 응답 인터셉터 추가
/*
instance.interceptors.response.use(
    async function (response) {
        const responseData = response.data;
        const responseCode = responseData.code;
        //console.log('responseCode >>>', responseCode); // 응답 코드 확인용
        //console.log('responseData >>>', responseData); // 응답 데이터 확인용
        if (
            responseCode != null &&
            responseCode != 'undefined' &&
            responseCode != '' &&
            responseCode == -402
        ) {
            await jwtTokenIvaild();
        } else if (responseCode == 0) {
            const token = responseData.token;
            sessionStorage.setItem('userToken', token);
        }

        // 응답 데이터를 처리
        return response;
    },
    function (error) {
        // 응답 오류가 발생했을 때 수행할 작업
        return Promise.reject(error);
    }
);
 */

const jwtTokenIvaild = async () => {
    const msg = '세션이 만료되었습니다. 계속하려면 다시 로그인 하세요.';
    const swalResult = await swal.swalConfirmWithNoCancel(msg, 'error');
    // localStorage의 관리자 정보 삭제 (쿠키는 백엔드에서 자동 삭제됨)
    localStorage.removeItem('adminInfo');
    if (swalResult.isConfirmed) {
        location.href = '/login';
        return;
    }
};

export default instance;
