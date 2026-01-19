<?php

session_start();
class naverRestAPI{

    var $client_id      = "UbulJR6fs_MM2G5QGMFC"; // 실제 운영 key
    var $client_secret  = "nnfCqQCL13";
    var $redirect_uri   = "http://localhost:3000/naver_login.php"; // ./naver_login.php
    var $result_uri     = './join_sns_callback?join_type=naver';

    // api 사용가능 여부
    var $auth_apply = false;

    // 디버깅시 결과 볼지 여부 (true or false)
    var $debug_view = true;

    // 디버깅시 결과 테스트 (true or false)
    var $debug_txt = '';

    // 요청 URL 정의
    var $request_url = array(
        'code'      =>  'https://nid.naver.com/oauth2.0/authorize?response_type=code&client_id={CLIENT_ID}&redirect_uri={REDIRECT_URI}&state=RAMDOM_STATE',
        'token'     =>  'https://nid.naver.com/oauth2.0/token', // 토큰 받기 // (only post)
        'userinfo'  =>  'https://openapi.naver.com/v1/nid/me',
        'logout'    =>  'https://nid.naver.com/oauth2.0/token',
    );


    /*생성자*/
    function __construct(){
        if( empty($this->client_id)){ return $this->debug('client_id 키값 누락',__LINE__); }
        if( empty($this->client_secret)){ return $this->debug('client_secret 키값 누락',__LINE__); }
        if( empty($this->redirect_uri)){ return $this->debug('redirect_uri 값 누락',__LINE__); }

        $this->request_url['code'] = str_replace(array('{CLIENT_ID}','{REDIRECT_URI}'),array($this->client_id,urlencode($this->redirect_uri)),$this->request_url['code']);

        // api 사용가능 여부
        $this->auth_apply = true;

    }

    /*token요청*/
    function getToken($code,$state){
        // code 는 header 로 요청되기때문에 반드시 출력 전에 실행
        if($this->auth_apply !== true){ return $this->debug("카카오 로그인 API를 호출할 수 없습니다.",__LINE__); }
        if(empty($code)){ return $this->debug("인가코드가 누락되었습니다.",__LINE__); }

        // URL에서 데이터를 추출하여 쿼리문 생성
        $postfields = array('grant_type'=>'authorization_code','client_id'=>$this->client_id,'client_secret'=>$this->client_secret, 'redirect_uri'=>$this->redirect_uri,'code'=>$code,'state'=>$state);
        $url = $this->request_url['token']."?".http_build_query($postfields);

        //echo "urk :".$url;
        $is_post = false;

        $ch = curl_init();

        curl_setopt($ch, CURLOPT_URL, $url);
        curl_setopt($ch, CURLOPT_POST, $is_post);
        curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);

        $data = curl_exec($ch);

        if (curl_error($ch)){ return $this->debug('통신에러 ('.curl_errno( $ch ).') '.curl_error($ch),__LINE__);}
        curl_close($ch);

        return $data;
    }

    function getUserInfo($access_token){
        // code 는 header 로 요청되기때문에 반드시 출력 전에 실행
        if($this->auth_apply !== true){ return $this->debug("네이버 로그인 API를 호출할 수 없습니다.",__LINE__); }
        if(empty($access_token)){ return $this->debug("인증코드가 누락되었습니다.",__LINE__); }


        // URL에서 데이터를 추출하여 쿼리문 생성
        $url = $this->request_url['userinfo'];
        $headers = array("Authorization: Bearer ".$access_token);

        $is_post = false;
        $ch = curl_init();

        curl_setopt($ch, CURLOPT_URL, $url);
        curl_setopt($ch, CURLOPT_POST, $is_post);
        curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
        curl_setopt($ch, CURLOPT_HTTPHEADER, $headers);


        $data = curl_exec($ch);
        if (curl_error($ch)){ return $this->debug('통신에러 ('.curl_errno( $ch ).') '.curl_error($ch),__LINE__);}
        curl_close($ch);
        return $data;
    }

    function getLogout($access_token){
        // code 는 header 로 요청되기때문에 반드시 출력 전에 실행
        if($this->auth_apply !== true){ return $this->debug("네이버 로그인 API를 호출할 수 없습니다.",__LINE__); }
        if(empty($access_token)){ return $this->debug("인증코드가 누락되었습니다.",__LINE__); }

        $postfields = array('grant_type'=>'delete','client_id'=>$this->client_id,'client_secret'=>$this->client_secret, 'access_token'=>$access_token,'service_provider'=>'NAVER');
        $url = $this->request_url['logout']."?".http_build_query($postfields);

        $is_post = false;

        $ch = curl_init();

        curl_setopt($ch, CURLOPT_URL, $url);
        curl_setopt($ch, CURLOPT_POST, $is_post);
        curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);

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
?>
