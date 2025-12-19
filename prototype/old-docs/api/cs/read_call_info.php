<?php
// required headers
header("Access-Control-Allow-Origin: *");
header("Content-Type: application/json; charset=UTF-8");

// files needed to connect to database
include_once $_SERVER['DOCUMENT_ROOT'].'/api/config/database.php';
include_once $_SERVER['DOCUMENT_ROOT'].'/api/config/ars_database.php';
include_once $_SERVER['DOCUMENT_ROOT'].'/api/objects/ars.php';
include_once $_SERVER['DOCUMENT_ROOT'].'/api/objects/cs.php';
include_once $_SERVER['DOCUMENT_ROOT'].'/api/shared/utilities.php';
include_once $_SERVER['DOCUMENT_ROOT'].'/api/shared/errorlog.php';


$ars_database   = new ARS_database(); $ars_db = $ars_database->getConnection();
$ars            = new ARS($ars_db);
$database       = new Database(); $db = $database->getConnection();
$utilities      = new Utilities($db);

// instantiate product object
$cs = new Counselor($db);
$data =  json_decode($_POST["csObj"]);
session_start();

if (isset($_SESSION['IS_CS'])){
    if ($_SESSION['IS_CS']=='Y') {
        echo json_encode(array("isSuc"=>FALSE));
        http_response_code(200);
        exit;
    }
}


if(!isset($_SESSION['IDX'])){
    $cs_info = $cs ->read_cs_info_call($data->IDX);

    $direct_phone = '060-800-1300';
    $phone_value = '1300';
    if ($cs_info['GRADE'] == 'GOLD'){
        $direct_phone = '060-800-1500';
        $phone_value = '1500';
    }

    $str =
        '
                 <div class="inBox">
                    <div class="popCont">
                        <div class="csAppTop">
                            <div class="csBox">
                                <div class="flBox">
                                    <div class="ibox">
                                        <img id="IMG" src="/app/assets/upload/cs/'.$cs_info['IMG'].'">
                                    </div>
                                    <div class="tbox">
                                        <div class="tagBox">
                                            <span class="cate bg1">'.$cs_info['TYPE'].'</span>
                                        </div>
                                        <div class="owner">
                                            <span>'.$cs_info['NICK_NAME'].'</span>
                                            <span>'.$cs_info['CODE'].'번</span>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                        <div class="csAppMid needLogin">
                            <strong>회원 혜택</strong>
                            <p class="txt01">아직 회원이 아니신가요?</p>
                            <p class="txt02">
                                회원가입/로그인하시면 더 많은 사주로만의 혜택(이벤트, 알림)을<br>
                                누리실 수 있습니다.
                            </p>
                            <a href="/app/user/login">포인트 상담 회원가입&로그인</a>
                        </div>
                        <div class="csAppBottom">
                            <div class="callBox" onclick="location.href=`tel:'.$direct_phone.'`;">
                                <img src="/app/assets/img/contents/ico-call.png">
                                <strong>060상담</strong> (060-800-'.$phone_value.')
                            </div>
                            <p class="txt01">

                                060상담(후불)&nbsp <b>'.$phone_value.'원</b>(30초)
                            </p>
                            <p class="txt02">
                                상담안내<br>
                                전화상담 연결 후, 고유번호 <span>'.$cs_info['CODE'].'</span>번 누르세요.
                            </p>
                        </div>
                    </div>
                    <a href="javascript:void(0)" onclick="fn_layer_close(`csApplicationPop`);">닫기</a>
                </div>
            </div>
        ';

    $cs_info['cont'] = $str;
    echo json_encode(array("csObj" => $cs_info,"callback"=>"","isSuc"=>TRUE));
    http_response_code(200);

} else {
    $user_id = $_SESSION['USER_ID'];
    $cs_info = $cs ->read_cs_info_call($data->IDX);
    $ars_info = $ars -> getUserInfoById($user_id);
    $cs_info['u_point'] = $ars_info['u_point'];
    $cs_info['LEFT_TIME'] = round($cs_info['u_point'] / $cs_info['AFTER_AMOUNT'] / 2);

    $direct_phone = '060-800-1300';
    $phone_value = '1300';
    if ($cs_info['GRADE'] == 'GOLD'){
        $direct_phone = '060-800-1500';
        $phone_value = '1500';
    }

    $str =
        '
                 <div class="inBox">
                    <div class="popCont">
                        <div class="csAppTop">
                            <div class="csBox">
                                <div class="flBox">
                                    <div class="ibox">
                                        <img id="IMG" src="/app/assets/upload/cs/'.$cs_info['IMG'].'">
                                    </div>
                                    <div class="tbox">
                                        <div class="tagBox">
                                            <span class="cate bg1">'.$cs_info['TYPE'].'</span>
                                        </div>
                                        <div class="owner">
                                            <span>'.$cs_info['NICK_NAME'].'</span>
                                            <span>'.$cs_info['CODE'].'번</span>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                        
                        <div class="csAppMid login">
                            <div class="pbox" onclick="callByPoint(\'' . $cs_info['CODE'] . '\',\'' . $user_id . '\')">
                                <span>P</span>
                                <p><strong>포인트 상담</strong> (02-6209-0808)</p>
                            </div>
                            <div class="ptxt">
                                포인트상담(선불)&nbsp <b>'.$cs_info['AFTER_AMOUNT'].'P</b>(30초)
                            </div>
                            <div class="ptxt2">
                            <p align="center">전화연결시 선택한 선생님과 바로연결됩니다.</p>
                            </div>
                            <div class="cbox">
                                <div class="info">
                                    <p>보유 포인트 <strong>'.$cs_info['u_point'].'P</strong></p>
                                    <p>상담 가능 시간 <strong>'.$cs_info['LEFT_TIME'].'분</strong></p>
                                </div>
                                <a href="/app/charge/point"><span>포인트 충전</span></a>
                            </div>
                        </div>
                        <div class="csAppBottom">
                        <details>
                        <summary>060후불 상담 이용하기</summary><br>
                            <div class="callBox" onclick="location.href=`tel:'.$direct_phone.'`;">
                                <img src="/app/assets/img/contents/ico-call.png">
                                <strong>060상담</strong> (060-800-'.$phone_value.')
                            </div>
                            <p class="txt01">
                                060상담(후불)&nbsp <b>'.$phone_value.'원</b>(30초)
                            </p>
                            <p class="txt02">
                                상담안내<br>
                                전화상담 연결 후, 고유번호 <span>'.$cs_info['CODE'].'</span>번 누르세요.
                            </p>
                        </div>
                    </div>
                    </details>
                    <a href="javascript:void(0)" onclick="fn_layer_close(`csApplicationPop`);">닫기</a>
                </div>
            </div>
        ';

    $cs_info['cont'] = $str;
    echo json_encode(array("csObj" => $cs_info,"callback"=>"","isSuc"=>TRUE));
    http_response_code(200);
}





