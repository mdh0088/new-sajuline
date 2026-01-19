<?php

use PHPMailer\PHPMailer\PHPMailer;
use PHPMailer\PHPMailer\Exception;
use PHPMailer\PHPMailer\SMTP;

class Utilities{

    private $conn;

    // constructor
    public function __construct($db){
        $this->conn = $db;
    }

    public function getPaging($page, $total_rows, $records_per_page, $page_url){

        // paging array
        $paging_arr=array();

        // button for first page
        $paging_arr["first"] = $page>1 ? "{$page_url}page=1" : "";

        // count all products in the database to calculate total pages
        $total_pages = ceil($total_rows / $records_per_page);

        // range of links to show
        $range = 2;

        // display links to 'range of pages' around 'current page'
        $initial_num = $page - $range;
        $condition_limit_num = ($page + $range)  + 1;

        $paging_arr['pages']=array();
        $page_count=0;

        for($x=$initial_num; $x<$condition_limit_num; $x++){
            // be sure '$x is greater than 0' AND 'less than or equal to the $total_pages'
            if(($x > 0) && ($x <= $total_pages)){
                $paging_arr['pages'][$page_count]["page"]=$x;
                $paging_arr['pages'][$page_count]["url"]="{$page_url}page={$x}";
                $paging_arr['pages'][$page_count]["current_page"] = $x==$page ? "yes" : "no";

                $page_count++;
            }
        }

        // button for last page
        $paging_arr["last"] = $page<$total_pages ? "{$page_url}page={$total_pages}" : "";

        // json format
        return $paging_arr;
    }

    /* 데이터 유무 확인용 TRUE/FALSE 리턴 */
    function chkTableInfoByObj($tbl, $obj) {
        $query =
            "
            select 
                *
            from ".$tbl." where 1=1
           ";

        foreach ($obj as $key => $value) {
            $query .= "and ".$key." = '".$value."' ";
        }


        $stmt = $this->conn->prepare( $query );
        $stmt->execute();
        return ($stmt->rowCount() > 0) ? true : false;
    }

    /* 데이터 유무 확인용 TRUE/FALSE 리턴 */
    function chkTableInfoByValue($tbl, $col, $val) {
        $query =
            "
        select * from ".$tbl." where ".$col." = '".$val."'
      ";


        $stmt = $this->conn->prepare( $query );
        $stmt->execute();
        return ($stmt->rowCount() > 0) ? true : false;
    }

    // 1개 리턴용
    function readOne($tbl,$obj){
        $query =

            "
            SELECT
                *
            FROM " . $tbl . " WHERE 1=1
            ";

        foreach ($obj as $key => $value) {
            $query .= "and ".$key." = '".$value."' ";
        }


        $stmt = $this->conn->prepare( $query );
        $stmt->execute();
        $row = $stmt->fetch(PDO::FETCH_ASSOC);

        return $row;
    }

    function readAll($tbl,$obj){
        $query =

            "
            SELECT
                *
            FROM " . $tbl . " WHERE 1=1
            ";

        foreach ($obj as $key => $value) {
            $query .= "and ".$key." = '".$value."' ";
        }


        //echo $query;
        $stmt = $this->conn->prepare( $query );
        $stmt->execute();

        $list = [];
        while ($row = $stmt->fetch(PDO::FETCH_ASSOC)) {
            $list[] = $row;
        }
        return $list;
    }

    // create new user record
    function addLoginLog($USER_IDX,$TYPE){

        $IP = $_SERVER['REMOTE_ADDR'];
        $OS = $_SERVER['HTTP_USER_AGENT'];
        // insert query
        $query =
            "
                INSERT INTO TBL_LOG_USER_LOGIN SET
                USER_IDX        = '".$USER_IDX."'
                , IP            = '".$IP."'
                , TYPE          = '".$TYPE."'
                , OS            = '".$OS."'
                , YEAR          = DATE_FORMAT(NOW(), '%Y')
                , MONDTH        = DATE_FORMAT(NOW(), '%m')
                , DAY           = DATE_FORMAT(NOW(), '%d')
                , REGIST_DATE   = NOW()
            ";

        if($this->conn->prepare($query)->execute()){
            return true;
        }
        return false;
    }

    function isEmpty($value) {
        return (!isset($value) || empty(trim($value)));
    }

    function reArrayFiles($file_post) {
        $file_ary = array();
        $file_count = count($file_post['name']);
        $file_keys = array_keys($file_post);
        for ($i=0; $i<$file_count; $i++) {
            foreach ($file_keys as $key) {
                $file_ary[$i][$key] = $file_post[$key][$i];
            }
        }
        return $file_ary;
    }

    function leaveSqlLog($query,$fnc_name,$loc){
        $current_timestamp = time();
        $current_time = date('Y-m-d H:i:s', $current_timestamp);

        $startToken = '--- START ('.$current_time.') ---';
        $endToken = '--- END ('.$current_time.') --'. "\n";
        $logData = $startToken . "\n";
        $logData .= "fnc_name : ".$fnc_name. "\n";
        $logData .= $query . "\n";
        $logData .= $endToken . "\n";

        $logFilePath = $_SERVER['DOCUMENT_ROOT'].'/log/sql/point/' . date('Ymd') . '.txt';
        file_put_contents($logFilePath, $logData, FILE_APPEND);
    }

    function sendMail($email, $body, $title) {
        
        require_once $_SERVER['DOCUMENT_ROOT'].'/config/mail/PHPMailer-master/src/Exception.php';
        require_once $_SERVER['DOCUMENT_ROOT'].'/config/mail/PHPMailer-master/src/PHPMailer.php';
        require_once $_SERVER['DOCUMENT_ROOT'].'/config/mail/PHPMailer-master/src/SMTP.php';


        $mail = new PHPMailer(true);

        try {
            $mail->isSMTP();
            $mail->Host        = 'smtp.cafe24.com';
            $mail->SMTPAuth    = true;
            $mail->Username    = 'help@sajutarot.com';
            $mail->Password    = 'tkwnfh12!';
            $mail->SMTPSecure  = PHPMailer::ENCRYPTION_STARTTLS;
            $mail->Port        = 587;
            $mail->setFrom('help@sajutarot.com', '사주라인');
            $mail->addAddress($email, $email);
            $mail->isHTML(true);
            $mail->Subject     = $title;
            $mail->Body        = $body;
            $mail->CharSet     = 'UTF-8';

            if($mail->send()){
                return true;
            }else{
                return false;
            }
        } catch (Exception $e) {
            return false;
        }
    }


    function generatePassword() {
        $length = 8;
        $chars = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*()-_=+';
        $password = '';
        $chars_length = strlen($chars) - 1;
        $has_uppercase = false;
        $has_lowercase = false;
        $has_number = false;
        $has_special = false;

        while (strlen($password) < $length) {
            $rand = mt_rand(0, $chars_length);
            $char = $chars[$rand];
            $password .= $char;

            if (ctype_upper($char)) {
                $has_uppercase = true;
            } else if (ctype_lower($char)) {
                $has_lowercase = true;
            } else if (ctype_digit($char)) {
                $has_number = true;
            } else if (preg_match('/[!@#$%^&*()-_=+]/', $char)) {
                $has_special = true;
            }
        }

        // Ensure that password contains at least one uppercase letter, one lowercase letter,
        // one number, and one special character.
        if (!$has_uppercase || !$has_lowercase || !$has_number || !$has_special) {
            return generatePassword();
        }

        return $password;
    }


    function utf8ize($data) {
        if (is_array($data)) {
            foreach ($data as $key => $value) {
                if ($key === 'm_name' || $key === 'm_nickname') {
                    $data[$key] = mb_convert_encoding($value, 'UTF-8', 'CP949');
                } else {
                    $data[$key] = utf8ize($value);
                }
            }
        }
        return $data;
    }


    function update_last_login($idx,$table){


        $query =
            "
                UPDATE $table SET
                LAST_LOGIN  = NOW()
                WHERE IDX = '".htmlspecialchars(strip_tags($idx))."'
            ";


        if($this->conn->prepare($query)->execute()){
            return true;
        }
        return false;
    }
    
}
?>
