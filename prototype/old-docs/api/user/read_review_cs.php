<?php
// required headers
header("Access-Control-Allow-Origin: *");
header("Content-Type: application/json; charset=UTF-8");

// files needed to connect to database
include_once $_SERVER['DOCUMENT_ROOT'].'/api/config/database.php';
include_once $_SERVER['DOCUMENT_ROOT'].'/api/config/ars_database.php';
include_once $_SERVER['DOCUMENT_ROOT'].'/api/objects/ars.php';
include_once $_SERVER['DOCUMENT_ROOT'].'/api/objects/user.php';
include_once $_SERVER['DOCUMENT_ROOT'].'/api/objects/cs.php';
include_once $_SERVER['DOCUMENT_ROOT'].'/api/shared/utilities.php';
include_once $_SERVER['DOCUMENT_ROOT'].'/api/shared/errorlog.php';


$ars_database   = new ARS_database(); $ars_db = $ars_database->getConnection();
$ars            = new ARS($ars_db);
$database       = new Database(); $db = $database->getConnection();
$utilities      = new Utilities($db);

// instantiate product object
$cs = new Counselor($db);
$data =  json_decode($_POST["reviewObj"]);
$month = $data -> MONTH;

session_start();
$user_idx = $_SESSION['IDX'];
$user_id = $_SESSION['USER_ID'];
//$chatlist = $cs->read_review_by_useridx($user_idx,$month);
$ars_chat_list = $ars -> getChatlogByIdForUser($user_id,$month);


if (count($ars_chat_list) > 0) {
    foreach ($ars_chat_list as $key => $value) {
        $ars_chat_list[$key]['csInfo']=$cs->getCsInfoByCode($ars_chat_list[$key]['m_code']);
        $ars_chat_list[$key]['review_info']=$cs->getReviewInfoChatIdx($ars_chat_list[$key]['idx']);

/*        $ars_data = $ars-> getChatLogForReview($ars_chat_list[$key]['CHATLOG_IDX']);
        $ars_chat_list[$key]['chat_day'] = $ars_data['chat_day'];
        $ars_chat_list[$key]['chat_time'] = $ars_data['chat_time'];
        $ars_chat_list[$key]['usepoint'] = $ars_data['usepoint'];
        $ars_chat_list[$key]['chat_type'] = $ars_data['chat_type'];*/

    }
}



//print_r($chatlist);

// query products
echo json_encode(array("list" => $ars_chat_list,"callback"=>"","isSuc"=>TRUE), JSON_UNESCAPED_UNICODE);
http_response_code(200);

