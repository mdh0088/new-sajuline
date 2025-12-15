<?php
/*
	@ 카카오 로그인 REST API 샘플
	© 2022 REDINFO <webmaster@redinfo.co.kr>
*/
session_start();
class kakaoRestAPI{


    // <수정필요> REST API 키값 : kakao developers > 내 애플리케이션 > 요약정보 > 앱 키 > REST API 키\
    var $restapi_key = 'd350fd6d69f21fb2a55646f17cf969f4';

    // <수정필요> 리다렉트 URL : kakao developers > 내 애플리케이션 > 제품설정 > 카카오 로그인 > Redirect URI
    var $redirect_uri = 'https://sajutarot.com/api/social/kakao_login.php';

    // <수정필요> 카카오 로그인 인증 후 이동할 페이지
    var $result_uri = '/app/user/join_sns_callback?join_type=kakao';

    // api 사용가능 여부
    var $auth_apply = false;

    // 디버깅시 결과 볼지 여부 (true or false)
    var $debug_view = true;

    // 디버깅시 결과 테스트 (true or false)
    var $debug_txt = '';

    // 요청 URL 정의
    var $request_url = array(
        'code'=>'https://kauth.kakao.com/oauth/authorize?response_type=code&client_id={REST_API_KEY}&redirect_uri={REDIRECT_URI}', // get
        'token'=>'https://kauth.kakao.com/oauth/token', // 토큰 받기 // (only post)
        'userInfo'=>'https://kapi.kakao.com/v2/user/me', // 사용자 정보 가져오기(get or post)
        'logout'=>'https://kapi.kakao.com/v1/user/logout', // 사용자 로그아웃 가져오기(only post)
    );


    /*생성자*/
    function __construct(){
        if( empty($this->restapi_key)){ return $this->debug('restapi_key 키값 누락',__LINE__); }
        if( empty($this->redirect_uri)){ return $this->debug('redirect_uri 값 누락',__LINE__); }

        // request code url 치환자 정의
        $this->request_url['code'] = str_replace(array('{REST_API_KEY}','{REDIRECT_URI}'),array($this->restapi_key,urlencode($this->redirect_uri)),$this->request_url['code']);

        // api 사용가능 여부
        $this->auth_apply = true;

    }

    /*token요청*/
    function getToken($code){
        // code 는 header 로 요청되기때문에 반드시 출력 전에 실행
        if($this->auth_apply !== true){ return $this->debug("카카오 로그인 API를 호출할 수 없습니다.",__LINE__); }
        if(empty($code)){ return $this->debug("인가코드가 누락되었습니다.",__LINE__); }

        // URL에서 데이터를 추출하여 쿼리문 생성
        $postfields = array('grant_type'=>'authorization_code','client_id'=>$this->restapi_key,'redirect_uri'=>$this->redirect_uri,'code'=>$code);
        $url = $this->request_url['token']."?".http_build_query($postfields);
        $ch = curl_init();
        curl_setopt($ch, CURLOPT_URL, $url);
        curl_setopt($ch, CURLOPT_SSL_VERIFYPEER, FALSE);
        curl_setopt($ch, CURLOPT_SSL_VERIFYHOST, 0);
        curl_setopt($ch, CURLOPT_USERAGENT, $_SERVER['HTTP_USER_AGENT']);
        curl_setopt($ch, CURLOPT_RETURNTRANSFER, 1);
        curl_setopt($ch, CURLOPT_POST, 1);
        curl_setopt($ch, CURLOPT_POSTFIELDS, $postfields);
        $data = curl_exec($ch);
        if (curl_error($ch)){ return $this->debug('통신에러 ('.curl_errno( $ch ).') '.curl_error($ch),__LINE__);}
        curl_close($ch);
        return $data;
    }


    /*사용자정보호출*/
    function getUserInfo($access_token){

        // code 는 header 로 요청되기때문에 반드시 출력 전에 실행
        if($this->auth_apply !== true){ return $this->debug("카카오 로그인 API를 호출할 수 없습니다.",__LINE__); }
        if(empty($access_token)){ return $this->debug("인증코드가 누락되었습니다.",__LINE__); }

        // URL에서 데이터를 추출하여 쿼리문 생성
        $url = $this->request_url['userInfo'];
        $headers = array("Authorization: Bearer ".$access_token);
        $ch = curl_init();
        curl_setopt($ch, CURLOPT_URL, $url);
        curl_setopt($ch, CURLOPT_SSL_VERIFYPEER, FALSE);
        curl_setopt($ch, CURLOPT_SSL_VERIFYHOST, 0);
        curl_setopt($ch, CURLOPT_USERAGENT, $_SERVER['HTTP_USER_AGENT']);
        curl_setopt($ch, CURLOPT_RETURNTRANSFER, 1);
        curl_setopt($ch, CURLOPT_POST, 1);
        curl_setopt($ch, CURLOPT_HTTPHEADER, $headers);
        curl_setopt($ch, CURLOPT_POSTFIELDS, $postfields);
        $data = curl_exec($ch);
        if (curl_error($ch)){ return $this->debug('통신에러 ('.curl_errno( $ch ).') '.curl_error($ch),__LINE__);}
        curl_close($ch);
        return $data;
    }

    /*로그아웃*/
    function getLogout($access_token){

        // code 는 header 로 요청되기때문에 반드시 출력 전에 실행
        if($this->auth_apply !== true){ return $this->debug("카카오 로그인 API를 호출할 수 없습니다.",__LINE__); }
        if(empty($access_token)){ return $this->debug("인증코드가 누락되었습니다.",__LINE__); }

        // URL에서 데이터를 추출하여 쿼리문 생성
        $url = $this->request_url['logout'];
        $headers = array("Authorization: Bearer ".$access_token);
        $ch = curl_init();
        curl_setopt($ch, CURLOPT_URL, $url);
        curl_setopt($ch, CURLOPT_SSL_VERIFYPEER, FALSE);
        curl_setopt($ch, CURLOPT_SSL_VERIFYHOST, 0);
        curl_setopt($ch, CURLOPT_USERAGENT, $_SERVER['HTTP_USER_AGENT']);
        curl_setopt($ch, CURLOPT_RETURNTRANSFER, 1);
        curl_setopt($ch, CURLOPT_POST, 1);
        curl_setopt($ch, CURLOPT_HTTPHEADER, $headers);
        curl_setopt($ch, CURLOPT_POSTFIELDS, $postfields);
        $data = curl_exec($ch);
        if (curl_error($ch)){ return $this->debug('통신에러 ('.curl_errno( $ch ).') '.curl_error($ch),__LINE__);}
        curl_close($ch);
        return $data;
    }


    /*디버깅*/
    function debug($msg,$code){
        ob_start();
        echo "[".$code."] ".$msg;
        $this->debug_txt = ob_get_clean();
        if( $this->debug_view === true){ echo $this->debug_txt; }
        return false;
    }
}
