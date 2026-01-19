<?php

class SMS{

    // database connection and table name
    private $conn;


    // constructor
    public function __construct($db){
        $this->conn = $db;
    }


    //, USER_ID       = '".htmlspecialchars(strip_tags($obj->USER_ID))."'
    // create new user record
    function create($obj){

        $career = strip_tags($obj->CAREER);
        $career = htmlentities($career, ENT_QUOTES);

        $greeting = strip_tags($obj->GREETING);
        $greeting = htmlentities($greeting, ENT_QUOTES);

        // insert query
        $query =
            "
                INSERT INTO TBL_CS SET
                TYPE            = '".htmlspecialchars(strip_tags($obj->TYPE))."'
                , NICK_NAME     = '".htmlspecialchars(strip_tags($obj->NICK_NAME))."'
                , NAME          = '".htmlspecialchars(strip_tags($obj->NAME))."'
                , PHONE         = '".htmlspecialchars(strip_tags($obj->PHONE))."'
                , EMAIL         = '".htmlspecialchars(strip_tags($obj->EMAIL))."'
                , SHORT_INFO     = '".htmlspecialchars(strip_tags($obj->SHORT_INFO))."'
                , GREETING      = '".$greeting."'
                , CAREER        = '".$career."'
                , CS_KEYWORD    = '".htmlspecialchars(strip_tags($obj->keywords))."'
                , IMG1          = '".htmlspecialchars(strip_tags($obj->IMG1))."'
                , IMG2          = '".htmlspecialchars(strip_tags($obj->IMG2))."'
                , IMG3          = '".htmlspecialchars(strip_tags($obj->IMG3))."'
                , IMG4          = '".htmlspecialchars(strip_tags($obj->IMG4))."'
                , IMG5          = '".htmlspecialchars(strip_tags($obj->IMG5))."'
                , RECRUIT_DATE  = NOW()
            ";


        if($this->conn->prepare($query)->execute()){
            return true;
        }
        return false;
    }

    // 1개 리턴용
    function read(){
        $query =

            "
            SELECT
                *
            FROM TBL_CS WHERE 
                APPROVAL_YN='N'
            ORDER BY RECRUIT_DATE DESC
            ";

        $stmt = $this->conn->prepare( $query );
        $stmt->execute();

        $list = [];
        while ($row = $stmt->fetch(PDO::FETCH_ASSOC)) {
            $list[] = $row;
        }
        return $list;
    }


    // 1개 리턴용
    function readOne($idx){
        $query =

            "
            SELECT
                *
            FROM TBL_CS WHERE 
                APPROVAL_YN='N'
                AND IDX = '".$idx."'
            ORDER BY RECRUIT_DATE DESC
            ";

        $stmt = $this->conn->prepare( $query );
        $stmt->execute();
        $row = $stmt->fetch(PDO::FETCH_ASSOC);

        return $row;
    }

    function add_history($obj){

        // insert query
        $query =
            "
                INSERT INTO TBL_KAKAO_ALARM_HISTORY SET
                USER_TYPE            = '".$obj['USER_TYPE']."'
                , USER_IDX           = '".$obj['USER_IDX']."'
                , NO                 = '".$obj['NO']."'
                , CODE               = '".$obj['CODE']."'
                , SEND_CONT          = '".$obj['CONT']."'
                , RESULT_CODE        = '".$obj['RESULT_CODE']."'
                , REGIST_DATE        = NOW()
            ";


        if($this->conn->prepare($query)->execute()){
            return true;
        }
        return false;
    }

    function add_alert_list($obj){

        // insert query
        $query =
            "
                INSERT INTO TBL_KAKAO_ALARM_WAIT_LIST SET
                USER_IDX            = '".$obj->USER_IDX."'
                , CS_IDX           = '".$obj->CS_IDX."'
                , REGIST_DATE        = NOW()
            ";


        if($this->conn->prepare($query)->execute()){
            return true;
        }
        return false;
    }


    function read_wait_list($cs_idx){


        $query=
            "
            SELECT
                BB.NICK_NAME AS USER_NICK_NAME
                , CC.NICK_NAME AS CS_NICK_NAME
                , BB.PHONE
                , AA.CS_IDX
                , AA.USER_IDX
            FROM TBL_KAKAO_ALARM_WAIT_LIST AA, TBL_USER BB, TBL_CS CC WHERE
                AA.USER_IDX = BB.IDX
                AND AA.CS_IDX = CC.IDX
                AND AA.CS_IDX = '".$cs_idx."'
                AND BB.USER_STATUS = '1'
            ";


        $stmt = $this->conn->prepare( $query );
        $stmt->execute();

        $list = [];
        while ($row = $stmt->fetch(PDO::FETCH_ASSOC)) {
            $list[] = $row;
        }

        return $list;
    }

    function delete_wait_list($user_idx,$cs_idx){


        $query =
            "
                delete from TBL_KAKAO_ALARM_WAIT_LIST where USER_IDX = '".$user_idx."' AND CS_IDX = '".$cs_idx."'
            ";


        if($this->conn->prepare($query)->execute()){
            return true;
        }
        return false;
    }
}
