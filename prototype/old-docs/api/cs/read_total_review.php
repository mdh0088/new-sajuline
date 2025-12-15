<?php
// required headers
header("Access-Control-Allow-Origin: *");
header("Content-Type: application/json; charset=UTF-8");

// files needed to connect to database
include_once $_SERVER['DOCUMENT_ROOT'].'/api/config/ars_database.php';
include_once $_SERVER['DOCUMENT_ROOT'].'/api/objects/ars.php';
include_once $_SERVER['DOCUMENT_ROOT'].'/api/config/database.php';
include_once $_SERVER['DOCUMENT_ROOT'].'/api/objects/cs.php';
include_once $_SERVER['DOCUMENT_ROOT'].'/api/shared/errorlog.php';

// get database connection
$ars_database   = new ARS_database(); $ars_db = $ars_database->getConnection();
$ars            = new ARS($ars_db);
$database = new Database();
$db = $database->getConnection();

// instantiate product object
$cs = new Counselor($db);
$data = json_decode($_POST["searchObj"]);

$per_page = 5;
$page = $data -> PAGE;
$data->page = $page * $per_page;

$cs_list = $cs->read_whole_review($data);
$total_page = $cs->read_whole_review_cnt();
$last_page = ceil($total_page['CNT'] / $per_page);


if (count($cs_list) > 0) {
    foreach ($cs_list as $key => $value) {
        if ($cs_list[$key]['CHATLOG_IDX'] != ''){
            $ars_info = $ars->getChatlogByChatIdx($cs_list[$key]['CHATLOG_IDX']);
            $cs_list[$key]['CHAT_TIME']=$ars_info['chat_time'];
        }
    }
}

// query products
echo json_encode(array("list" => $cs_list,"callback"=>"","last_page"=>$last_page,"isSuc"=>TRUE));
http_response_code(200);

