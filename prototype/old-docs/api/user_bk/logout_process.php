<?php
require_once($_SERVER['DOCUMENT_ROOT']."/config/db/init.php");
require_once($_SERVER['DOCUMENT_ROOT']."/src/dao/user.php");
require_once($_SERVER['DOCUMENT_ROOT']."/src/util/common.php");

error_reporting( E_ALL );
ini_set( "display_errors", 1 );


echo session_destroy();
?>
