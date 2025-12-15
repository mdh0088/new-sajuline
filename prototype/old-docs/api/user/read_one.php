<?php
// required headers
header("Access-Control-Allow-Origin: *");
header("Content-Type: application/json; charset=UTF-8");
header("Access-Control-Allow-Headers: access");
header("Access-Control-Allow-Methods: GET");
header("Access-Control-Allow-Credentials: true");

// files needed to connect to database
include_once $_SERVER['DOCUMENT_ROOT'].'/api/config/database.php';
include_once $_SERVER['DOCUMENT_ROOT'].'/api/objects/user.php';

// get database connection
$database = new Database();
$db = $database->getConnection();

// instantiate product object
$user = new User($db);

// set ID property of record to read
$user->IDX = isset($_GET['idx']) ? $_GET['idx'] : die();

// read the details of product to be edited
$user->readOne();

if($user->IDX!=null){

    // create array
    $user_arr =array(
        "IDX"         => $user -> IDX,
        "NAME"        => $user -> NAME,
        "NICK_NAME"   => $user -> NICK_NAME,
        "USER_ID"     => $user -> USER_ID,
        "PASSWORD"    => $user -> PASSWORD,
        "EMAIL"       => $user -> EMAIL,
        "PHONE"       => $user -> PHONE,
        "JOIN_TYPE"   => $user -> JOIN_TYPE,
        "REGIST_DATE" => $user -> REGIST_DATE,
        "LAST_LOGIN"  => $user -> LAST_LOGIN
    );

    // set response code - 200 OK
    http_response_code(200);
    // make it json format
    echo json_encode($user_arr);
}
else{
    // set response code - 404 Not found
    http_response_code(404);

    // tell the user product does not exist
    echo json_encode(array("message" => "User does not exist."));
}
?>
