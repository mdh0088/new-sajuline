<?php
/*
try {
    // Your script or function code here
    error_reporting(E_ALL);

    ini_set('log_errors', 1);
    $logFile = $_SERVER['DOCUMENT_ROOT'].'/log/php-errors-' . date('Y-m-d') . '.log';
    ini_set('error_log', $logFile); // set log file path

    error_log("Error start ==============================================================================================");
    if(!empty($_REQUEST)){
        $requestData = http_build_query($_REQUEST);
        error_log("[" . date('Y-m-d H:i:s') . "] \n#Error page: " . $_SERVER['PHP_SELF'] . ".\n#Error data: \n " . urldecode($requestData)."\n", 3, $logFile);
    }else{
        error_log("[" . date('Y-m-d H:i:s') . "] \n#Error page: " . $_SERVER['PHP_SELF'] . ".\n", 3, $logFile);
    }
    //your code here
} catch (Exception $e) {
    error_log("[" . date('Y-m-d H:i:s') . "] \n#Error message: " . $e->getMessage() . ".\n#Error page: " . $_SERVER['PHP_SELF'] . ".\n", 3, $logFile);
    error_log("Error end ==============================================================================================");
}

//rest of the code
*/

error_reporting(E_ALL);
//ini_set("display_errors", 1);
ini_set('log_errors', 1);
$logFile = $_SERVER['DOCUMENT_ROOT'].'/log/error/php-errors-' . date('Y-m-d') . '.log';
ini_set('error_log', $logFile); // set log file path
if (file_exists($logFile)) {
    $errorLog = file_get_contents($logFile);
    //echo $errorLog;
}

