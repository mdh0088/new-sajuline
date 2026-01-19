<?php

// Connect to the database

include_once $_SERVER['DOCUMENT_ROOT'].'/api/config/database.php';
$database = new Database();
$db = $database->getConnection();

// Get the IP address, device type, URL, date, user agent, device type, browser type, and OS type
    $ip = $_SERVER['REMOTE_ADDR'];
    $device = $_SERVER['HTTP_USER_AGENT'];
    $url = $_SERVER['HTTP_REFERER'];
    $date = date('Y-m-d H:i:s');

// Determine if the device is a computer or a mobile device
    $device_type = (preg_match('/mobile/i', $device)) ? 'Mobile' : 'Computer';
if (!isset($_COOKIE['visitor_log'])) {
// Get the browser type
    if (preg_match('/MSIE/i', $device)) {
        $browser = 'Internet Explorer';
    } elseif (preg_match('/Firefox/i', $device)) {
        $browser = 'Mozilla Firefox';
    } elseif (preg_match('/Chrome/i', $device)) {
        $browser = 'Google Chrome';
    } elseif (preg_match('/Safari/i', $device)) {
        $browser = 'Apple Safari';
    } elseif (preg_match('/Opera/i', $device)) {
        $browser = 'Opera';
    } elseif (preg_match('/NAVER/i', $device)) {
        $browser = 'Naver';
    } elseif (preg_match('/KAKAO/i', $device)) {
        $browser = 'Kakao';
    } elseif (preg_match('/SamsungBrowser/i', $device)) {
        $browser = 'Samsung';
    } else {
        $browser = 'Other';
    }

// Get the OS type
    if (preg_match('/Windows/i', $device)) {
        $os = 'Windows';
    } elseif (preg_match('/Mac/i', $device)) {
        $os = 'Mac';
    } elseif (preg_match('/Linux/i', $device)) {
        $os = 'Linux';
    } else {
        $os = 'Other';
    }

// Insert the log into the database
    $sql = "INSERT INTO TBL_LOG_DAILY (IP, URL, REGIST_DATE, USER_AGENT, DEVICE_TYPE, BROWSER, OS_TYPE)
VALUES ('$ip', '$url', '$date', '$device', '$device_type', '$browser', '$os')";

    $db->prepare($sql)->execute();
    //setcookie('visitor_log', $ip, time() + (60 * 60 * 24 * 365));
    setcookie('visitor_ip', $ip, time() + 3600);

}

?>
