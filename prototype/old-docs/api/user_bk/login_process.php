<?php
require_once($_SERVER['DOCUMENT_ROOT']."/config/db/init.php");
require_once($_SERVER['DOCUMENT_ROOT']."/src/dao/user.php");
require_once($_SERVER['DOCUMENT_ROOT']."/src/util/common.php");

error_reporting( E_ALL );
ini_set( "display_errors", 1 );

$User = new User;
$usrObj = json_decode($_POST['usrObj']);

$return_obj = new stdClass();
$return_obj -> isSuc        =   "";
$return_obj -> msg          =   "";

echo json_encode($User -> doLoginByUser($usrObj->USER_ID,$usrObj->PASSWORD));

?>
