
//로그인 버튼 세팅
//document.addEventListener('DOMContentLoaded', () => {
    const kko_key = 'd350fd6d69f21fb2a55646f17cf969f4';
    const kko_redirect_uri = 'https://sajutarot.com/api/social/kakao_login.php';
    const kko_code = 'https://kauth.kakao.com/oauth/authorize?response_type=code&client_id='+kko_key+'&redirect_uri='+kko_redirect_uri;

    const naver_key = 'UbulJR6fs_MM2G5QGMFC';
    const naver_redirect_url = 'https://sajutarot.com/api/social/naver_login.php';
    const naver_code = 'https://nid.naver.com/oauth2.0/authorize?response_type=code&client_id='+naver_key+'&redirect_uri='+naver_redirect_url+'&state=RAMDOM_STATE';

//    document.querySelector("#naver_login").setAttribute('href',naver_code);
//    document.querySelector("#kakao_login").setAttribute('href',kko_code);
//})
