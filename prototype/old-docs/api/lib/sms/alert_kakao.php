<?php
/*

*/
class kakaoAlert{

    var $host_url = 'https://jupiter.lunasoft.co.kr/api/AlimTalk/message/send';
    var $api_key = 'k39eeqzaqa8g6lwvnix33j2fftquxcuv4vkli02y';
    var $site_id = 'sajuro';
    //var $site_id = '@sajutarot';
    //var $template_id = '_NrvUxj';
    //var $template_id = '50047';


    // 요청 URL 정의
    var $request_url = array(
        'code'=>'https://kauth.kakao.com/oauth/authorize?response_type=code&client_id={REST_API_KEY}&redirect_uri={REDIRECT_URI}', // get
        'token'=>'https://kauth.kakao.com/oauth/token', // 토큰 받기 // (only post)
        'userInfo'=>'https://kapi.kakao.com/v2/user/me', // 사용자 정보 가져오기(get or post)
        'logout'=>'https://kapi.kakao.com/v1/user/logout', // 사용자 로그아웃 가져오기(only post)
    );


    //상담사 접속 알림
    function cs_login_alert($phone,$user_nick_name,$cs_idx){
        $msg = "#{사주로 상담사 접속 알림 안내}\n\n".$user_nick_name." 선생님 현재 상담가능 합니다.\n\n접속 알림을 해둔 다른 고객님이 계시므로\n상담을 원하시면 서둘러주세요.\n*해당 알림은 1회성 알림으로\n다시 접속알림이 필요하신 분은 재설정 해주세요.";
        $pc_link = "https://https://sajutarot.com/app/cs/cs_detail?idx=".$cs_idx;
        $mo_link = "https://https://sajutarot.com/app/cs/cs_detail?idx=".$cs_idx;

        $template_id = '50047';

        return $this->sendSMS($template_id,$phone,$msg,trim($msg),$pc_link,$mo_link);
    }

    //게시글 알림 (상담사)
    function cs_faq_alert($phone){
        $msg ="선생님에게 상담문의글이 작성되었습니다.\n확인하시어 답변or접속 부탁드립니다.";

        $pc_link = "https://sajutarot.com/app/cs/mypage";
        $mo_link = "https://sajutarot.com/app/cs/mypage";

        $template_id = '50046';

        return $this->sendSMS($template_id,$phone,$msg,$msg,$pc_link,$mo_link);
    }

    //게시글 알림 (고객)
    function user_faq_alert($phone,$user_nick_name){
        $msg =$user_nick_name."님의 후기/문의글에 답변이 작성되었습니다.\n확인하시고 상담or접속알림 설정하시기 바랍니다.";

        $pc_link = "https://sajutarot.com/app/user/mypage";
        $mo_link = "https://sajutarot.com/app/user/mypage";

        $template_id = '50045';

        return $this->sendSMS($template_id,$phone,$msg,$msg,$pc_link,$mo_link);
    }

    //무통장 입금 완료_수동
    function user_virtual_alert($phone,$user_nick_name,$regist_date,$amount,$order_no,$product_name){
        $site_nm = "사주타로";
        $url = "https://sajutarot.com/app/user/history_charge";
        $msg=$user_nick_name." 고객님의 입금 금액 확인되었습니다.\n\n결제일 : ".$regist_date."\n입금금액 : ".$amount."원\n주문번호 : ".$order_no."\n상품명 : ".$product_name."\n\n".$site_nm." ".$url;

        $pc_link = "";
        $mo_link = "";

        $template_id = '50044';

        return $this->sendSMS($template_id,$phone,$msg,$msg,$pc_link,$mo_link);
    }

    //입금 요청 수동
    function user_money_request_alert($phone,$user_nick_name,$amount,$bank,$account,$depositor,$regist_date,$product_name){
        $msg=$user_nick_name." 고객님의 주문하신 상품이 미입금 상태입니다.\n해당 계좌로 미입금시 주문 자동취소됩니다.\n\n금액 : ".$amount."원\n입금계좌 : ".$bank." ".$account."\n예금주 : ".$depositor."\n주문일 : ".$regist_date."\n상품명 : ".$product_name;

        $pc_link = "";
        $mo_link = "";

        $template_id = '50043';

        return $this->sendSMS($template_id,$phone,$msg,$msg,$pc_link,$mo_link);
    }

    //결제 완료
    function user_charge_confirm_alert($phone,$user_nick_name,$order_no, $product_name, $amount, $point){
        $msg=$user_nick_name." 고객님의 소중한 주문 안내드립니다.\n주문번호 : ".$order_no."\n주문상품 : ".$product_name."\n금액 : ".$amount."원\n포인트 : ".$point;

        $pc_link = "";
        $mo_link = "";

        $template_id = '50042';

        return $this->sendSMS($template_id,$phone,$msg,$msg,$pc_link,$mo_link);
    }

    //회원 가입 수동
    function user_join_alert($phone,$nick_name){
        $msg=$nick_name."님의 회원가입을 감사드립니다.\n즉시 사용가능한 10,000포인트가 지급되었습니다.\n\n해당 포인트는 추가결제 없이 사용가능한 포인트이며\n원하시는 선생님과 상담을 하실 수 있습니다.\n지급해드린 포인트가 모두 소진되면 자동으로 통화종료됩니다.\n아래 버튼을 클릭하시면 이용방법이 안내되어 있습니다.\n\n이 메시지는 고객님의 동의에 의해 지급된 회원가입 혜택 지급 메시지입니다.";

        $pc_link = "https://sajutarot.com/app/charge/guide";
        $mo_link = "https://sajutarot.com/app/charge/guide";

        $template_id = '50041';

        return $this->sendSMS($template_id,$phone,$msg,$msg,$pc_link,$mo_link);
    }



    /**
    reserve_time : 예약 발송 시 발송 시간, “reserve_time”:”2019-06-01 00:00:00”, 현재로선 사용 X
    custom_key :  알림톡/SMS/LMS 성공 실패 여부 확인 시 unique key, 현재로선 사용 X, 사용한다면 USER ID로 대체
    app_user_id : USER_ID로 대체
     */
    //$custom_key
    function sendSMS($template_id, $tel_num, $msg_content, $sms_content, $url_pc, $url_mobile) {

        $current_time = date('YmdHis');
        $no             = $current_time;
        $url = $this->host_url;
        $use_sms = 1;
        $data = array(
            'userid' => $this->site_id,
            'api_key' => $this->api_key,
            'template_id' => $template_id,
            'messages' => array(
                array(
                    'no' => $no,
                    'tel_num' => $tel_num,
                    //'reserve_time' => $reserve_time,
                    //'custom_key' => $custom_key,
                    'msg_content' => $msg_content,
                    'sms_content' => $sms_content,
                    'use_sms' => $use_sms,
                    //'app_user_id' => $app_user_id,
                    'btn_url' => array(
                        array(
                            'url_pc' => $url_pc,
                            'url_mobile' => $url_mobile
                            //'scheme_android' => $scheme_android,
                            //'scheme_ios' => $scheme_ios
                        )
                    )
                )
            )
        );

        $jsonData = json_encode($data);
        $headers = array(
            'Content-type: application/json'
        );

        $is_post = true;
        $ch = curl_init();

        curl_setopt($ch, CURLOPT_URL, $url);
        curl_setopt($ch, CURLOPT_POST, $is_post);
        curl_setopt($ch, CURLOPT_POSTFIELDS, $jsonData);
        curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
        curl_setopt($ch, CURLOPT_HTTPHEADER, $headers);

        $response = curl_exec($ch);
/*        if (curl_error($ch)) {
            // Handle errors if any
            echo 'Error: (' . curl_errno($ch) . ') ' . curl_error($ch);
        } else {
            echo $response;
        }*/

        curl_close($ch);

        $result = json_decode($response);
        if ($result->code == '0'){
            $obj = array("isSuc" => TRUE,"no"=>$no,"code"=>$result->code,"cont"=>$msg_content,"template"=>$template_id);
            return $obj;
        } else {
            $obj = array("isSuc" => FALSE,"no"=>$no,"code"=>$result->code,"template"=>$template_id);
            return $obj;
        }

        //return $response;
    }
}
