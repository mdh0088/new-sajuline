<?php
// 'user' object
class Admin{

    // database connection and table name
    private $conn;


    // constructor
    public function __construct($db){
        $this->conn = $db;
    }


    function update_dumy_user_id($obj){


        // insert query
        $query =
            "
                UPDATE TBL_CS_REVIEW_DUMY SET
                        USER_ID = '".$obj->UPDATE_USER_ID."'
                where 
                    USER_ID = '".$obj->USER_ID."'
            ";


        if($this->conn->prepare($query)->execute()){
            return true;
        }
        return false;
    }


    function read_admin_search_list(){
        $query=
            "
            SELECT
                T1.KEYWORD,
                COUNT(*) AS keyword_count
            FROM TBL_LOG_SEARCH T1
            LEFT JOIN TBL_LOG_SEARCH_FILTER T2 ON T1.KEYWORD = T2.KEYWORD
            WHERE
                (T1.USER_TYPE = 'USER'  or T1.USER_TYPE = 'COMMON')
              AND T2.KEYWORD IS NULL
            GROUP BY T1.KEYWORD
            ORDER BY keyword_count DESC

            ";

        $stmt = $this->conn->prepare( $query );
        $stmt->execute();

        $list = [];
        while ($row = $stmt->fetch(PDO::FETCH_ASSOC)) {
            $list[] = $row;
        }
        return $list;
    }

    function update_search_keyword($obj){


        // insert query
        $query =
            "
                UPDATE TBL_LOG_SEARCH SET
                        KEYWORD = '".$obj->UPT_KEYWORD."'
                where
                    KEYWORD = '".$obj->REAL_KEYWORD."'
            ";


        if($this->conn->prepare($query)->execute()){
            return true;
        }
        return false;
    }

    function update_search_keyword_filter($obj){


        // insert query
        $query =
            "
                INSERT INTO TBL_LOG_SEARCH_FILTER (KEYWORD)
                VALUES ('".$obj->UPT_KEYWORD."')
                ON DUPLICATE KEY UPDATE
                    KEYWORD = VALUES(KEYWORD)
            ";


        if($this->conn->prepare($query)->execute()){
            return true;
        }
        return false;
    }

    function read_admin_search_filter_list(){
        $query=
            "
            SELECT
                *
             FROM TBL_LOG_SEARCH_FILTER
                ORDER BY KEYWORD

            ";

        $stmt = $this->conn->prepare( $query );
        $stmt->execute();

        $list = [];
        while ($row = $stmt->fetch(PDO::FETCH_ASSOC)) {
            $list[] = $row;
        }
        return $list;
    }


    function delete_filter_keyword($obj){
        $query=
            "
            DELETE FROM TBL_LOG_SEARCH_FILTER WHERE IDX = '".$obj->IDX."'
            ";

        if($this->conn->prepare($query)->execute()){
            return true;
        }
        return false;
    }

    function read_admin_cs_notice_list(){
        $query=
            "
            SELECT
                *
             FROM TBL_CS_NOTICE
                ORDER BY REGIST_DATE DESC

            ";

        $stmt = $this->conn->prepare( $query );
        $stmt->execute();

        $list = [];
        while ($row = $stmt->fetch(PDO::FETCH_ASSOC)) {
            $list[] = $row;
        }
        return $list;
    }



    function save_notice($obj){

        $cont = strip_tags($obj->CONT);
        $cont = htmlentities($cont, ENT_QUOTES);

        // insert query
        $query =
            "
                INSERT INTO TBL_CS_NOTICE SET
                TITLE            = '".htmlspecialchars(strip_tags($obj->TITLE))."'
                , CONT              = '".$cont."'
                , REGIST_DATE       = NOW()
    
            ";


        if($this->conn->prepare($query)->execute()){
            return true;
        }
        return false;
    }

    function update_notice($obj){

        $cont = strip_tags($obj->CONT);
        $cont = htmlentities($cont, ENT_QUOTES);

        // insert query
        $query =
            "
                UPDATE TBL_CS_NOTICE SET
                        TITLE = '".$obj->TITLE."',
                        CONT = '".$cont."',
                        UPDASTE_DATE = NOW()
                where
                    IDX = '".$obj->IDX."'
            ";


        if($this->conn->prepare($query)->execute()){
            return true;
        }
        return false;
    }

    function read_cs_faq(){
        $query=
            "
                SELECT
                    AA.IDX
                    , AA.CS_IDX
                    , BB.NAME
                    , BB.NICK_NAME
                    , CS_CONT
                    , DATE_FORMAT(CS_REGIST_DATE,'%Y-%m-%d') AS CS_REGIST_DATE
                    , ADMIN_CONT
                    , DATE_FORMAT(ADMIN_REGIST_DATE,'%Y-%m-%d') AS ADMIN_REGIST_DATE
                FROM TBL_CS_ADMIN_FAQ AA, TBL_CS BB WHERE
                    AA.CS_IDX = BB.IDX
                    ORDER BY CS_REGIST_DATE DESC
            ";

        $stmt = $this->conn->prepare( $query );
        $stmt->execute();

        $list = [];
        while ($row = $stmt->fetch(PDO::FETCH_ASSOC)) {
            $list[] = $row;
        }
        return $list;
    }

    function update_cs_faq($obj){

        $cont = strip_tags($obj->CONT);
        $cont = htmlentities($cont, ENT_QUOTES);

        // insert query
        $query =
            "
                UPDATE TBL_CS_ADMIN_FAQ SET
                        ADMIN_CONT = '".$cont."',
                        ADMIN_REGIST_DATE = NOW()
                where
                    IDX = '".$obj->IDX."'
            ";



        if($this->conn->prepare($query)->execute()){
            return true;
        }
        return false;
    }

    function read_user_faq(){
        $query=
            "
                SELECT
                    AA.IDX
                    , AA.USER_IDX
                    , BB.NICK_NAME
                    , BB.USER_ID
                    , AA.USER_TITLE
                    , AA.USER_CONT
                    , DATE_FORMAT(USER_REGIST_DATE,'%Y-%m-%d') AS USER_REGIST_DATE
                    , AA.ADMIN_CONT
                   , DATE_FORMAT(AA.ADMIN_REGIST_DATE,'%Y-%m-%d') AS ADMIN_REGIST_DATE
                FROM TBL_ADMIN_FAQ AA, TBL_USER BB WHERE
                   AA.USER_IDX = BB.IDX
                   AND BB.USER_STATUS != 3
                   ORDER BY USER_REGIST_DATE DESC
            ";

        $stmt = $this->conn->prepare( $query );
        $stmt->execute();

        $list = [];
        while ($row = $stmt->fetch(PDO::FETCH_ASSOC)) {
            $list[] = $row;
        }
        return $list;
    }

    function update_user_faq($obj){

        $cont = strip_tags($obj->CONT);
        $cont = htmlentities($cont, ENT_QUOTES);

        // insert query
        $query =
            "
                UPDATE TBL_ADMIN_FAQ SET
                        ADMIN_CONT = '".$cont."',
                        ADMIN_REGIST_DATE = NOW()
                where
                    IDX = '".$obj->IDX."'
            ";



        if($this->conn->prepare($query)->execute()){
            return true;
        }
        return false;
    }

    function admin_user_out_list(){
        $query =

            "
                SELECT
                    IDX
                    , NICK_NAME
                    , USER_ID
                    , EMAIL
                    , PHONE
                    , CASE 
                        WHEN JOIN_TYPE = 'common' THEN '일반'
                        WHEN JOIN_TYPE = 'kakao' THEN '카카오'
                        WHEN JOIN_TYPE = 'naver' THEN '네이버'
                      END AS JOIN_TYPE
                    , DATE_FORMAT(REGIST_DATE,'%Y.%m.%d') AS REGIST_DATE
                    , LAST_LOGIN
                FROM TBL_USER where
                    USER_STATUS ='3'
                    ORDER BY REGIST_DATE DESC
            ";



        $stmt = $this->conn->prepare( $query );
        $stmt->execute();

        $list = [];
        while ($row = $stmt->fetch(PDO::FETCH_ASSOC)) {
            $list[] = $row;
        }

        return $list;
    }

    function update_cs_review($obj){

        $cont = strip_tags($obj->CONT);
        $cont = htmlentities($cont, ENT_QUOTES);

        // insert query
        $query =
            "
                UPDATE TBL_CS_REVIEW SET
                        CS_CONT = '".$cont."',
                        CS_REGIST_DATE = NOW()
                where
                    IDX = '".$obj->IDX."'
            ";



        if($this->conn->prepare($query)->execute()){
            return true;
        }
        return false;
    }

    function read_admin_faq_list(){
        $query =

            "
                SELECT
                    AA.IDX
                    , BB.USER_ID
                    , BB.NICK_NAME AS USER_NICK_NAME
                    , AA.USER_CONT
                    , DATE_FORMAT(AA.USER_REGIST_DATE,'%Y-%m-%d') as USER_REGIST_DATE
                    , CC.IDX AS CS_IDX
                    , CC.CODE
                    , CC.NICK_NAME AS CS_NICK_NAME
                    , AA.CS_CONT
                    , DATE_FORMAT(AA.CS_REGIST_DATE,'%Y-%m-%d') as CS_REGIST_DATE
                FROM TBL_CS_FAQ AA, TBL_USER BB, TBL_CS CC WHERE
                    AA.USER_IDX = BB.IDX
                    AND AA.CS_IDX =CC.IDX
                    ORDER BY AA.USER_REGIST_DATE DESC
            ";


        $stmt = $this->conn->prepare( $query );
        $stmt->execute();

        $list = [];
        while ($row = $stmt->fetch(PDO::FETCH_ASSOC)) {
            $list[] = $row;
        }

        return $list;
    }

    function update_cs_user_faq($obj){

        $cont = strip_tags($obj->CONT);
        $cont = htmlentities($cont, ENT_QUOTES);

        // insert query
        $query =
            "
                UPDATE TBL_CS_FAQ SET
                        CS_CONT = '".$cont."',
                        CS_REGIST_DATE = NOW()
                where
                    IDX = '".$obj->IDX."'
            ";



        if($this->conn->prepare($query)->execute()){
            return true;
        }
        return false;
    }

    function read_user_kakao_alert($obj){
        $query =

            "
                SELECT
                    AA.*
                    , CC.NAME
                FROM TBL_KAKAO_ALARM_HISTORY AA, TBL_USER BB, TBL_KAKAO_ALARM_TEMPLATE CC WHERE
                    AA.USER_IDX = BB.IDX
                    AND AA.CODE = CC.CODE
                    AND BB.IDX = ".$obj->IDX."
            ";


        $stmt = $this->conn->prepare( $query );
        $stmt->execute();

        $list = [];
        while ($row = $stmt->fetch(PDO::FETCH_ASSOC)) {
            $list[] = $row;
        }

        return $list;
    }

    function read_admin_alarm_list(){
        $query =

            "
                SELECT
                    CASE
                        WHEN USER_TYPE ='USER' AND BB.USER_STATUS!='3' THEN BB.NICK_NAME
                        WHEN BB.USER_STATUS = '3' THEN '탈퇴회원'
                        ELSE CC.NICK_NAME END AS NICK_NAME
                    , AA.USER_TYPE
                    , BB.USER_STATUS
                    , DD.NAME AS TEMPLATE_NAME
                    , AA.SEND_CONT
                    , AA.REGIST_DATE
                FROM TBL_KAKAO_ALARM_HISTORY AA
                    LEFT JOIN TBL_USER BB ON AA.USER_TYPE='USER' AND AA.USER_IDX = BB.IDX
                    LEFT JOIN TBL_CS CC ON AA.USER_TYPE='CS' AND AA.USER_IDX = CC.IDX
                    LEFT JOIN TBL_KAKAO_ALARM_TEMPLATE DD ON AA.CODE = DD.CODE
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
    function read_cs_out_list(){
        $query =

            "
            SELECT
                *
            FROM TBL_CS WHERE 
                OUT_YN = 'Y'
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

    function delete_cs($obj){


        // insert query
        $query =
            "
                UPDATE TBL_CS SET
                   OUT_YN   = 'Y'
                  , APPROVAL_YN = 'N'
                  , SHOW_YN = 'N'
                  , OUT_DATE = NOW()
                WHERE IDX =".$obj->IDX."
            ";

        if($this->conn->prepare($query)->execute()){
            return true;
        }
        return false;
    }

    // 1개 리턴용
    function read_cs(){
        $query =

            "
            SELECT
                *
            FROM TBL_CS WHERE 
                APPROVAL_YN='Y'
                and OUT_YN ='N'
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

    function update_review_hide($obj){


        // insert query
        $query =
            "
                UPDATE TBL_CS_REVIEW SET
                  SHOW_YN = 'N'
                WHERE IDX =".$obj->IDX."
            ";

        if($this->conn->prepare($query)->execute()){
            return true;
        }
        return false;
    }

    function read_hide_review_list(){
        $query =

            "
                SELECT
                    AA.IDX
                    , BB.USER_ID
                    , BB.NICK_NAME AS USER_NICK_NAME
                    , AA.USER_CONT
                    , DATE_FORMAT(AA.USER_REGIST_DATE,'%Y-%m-%d') as USER_REGIST_DATE
                    , CC.IDX AS CS_IDX
                    , CC.CODE
                    , CC.NICK_NAME AS CS_NICK_NAME
                    , AA.CS_CONT
                    , DATE_FORMAT(AA.CS_REGIST_DATE,'%Y-%m-%d') as CS_REGIST_DATE
                FROM TBL_CS_REVIEW AA, TBL_USER BB, TBL_CS CC WHERE
                    AA.USER_IDX = BB.IDX
                    AND AA.SHOW_YN ='N'
                    AND AA.CS_IDX =CC.IDX
                    ORDER BY AA.USER_REGIST_DATE DESC
            ";


        $stmt = $this->conn->prepare( $query );
        $stmt->execute();

        $list = [];
        while ($row = $stmt->fetch(PDO::FETCH_ASSOC)) {
            $list[] = $row;
        }

        return $list;
    }

    function read_cs_access_info(){
        $query =

            "
            SELECT
                *
            FROM TBL_CS WHERE
                APPROVAL_YN = 'Y'
                AND OUT_YN = 'N'
                AND SHOW_YN = 'Y'
            ";

        $stmt = $this->conn->prepare( $query );
        $stmt->execute();

        $list = [];
        while ($row = $stmt->fetch(PDO::FETCH_ASSOC)) {
            $list[] = $row;
        }
        return $list;
    }

    function read_daily_trade_info(){
        $query =

            "
            SELECT 
                'DAILY' AS SalesType,
                 IFNULL(FORMAT(SUM(amount), 0),0) AS Sales
            FROM 
                TBL_USER_TRADE 
            WHERE 
                PAY_TYPE = 'SUCCESS' AND DATE(TRANSACTION_DATE) = CURDATE()
            
            UNION ALL
            
            SELECT 
                'MONTHLY' AS SalesType,
                FORMAT(SUM(amount), 0) AS Sales
            FROM 
                TBL_USER_TRADE 
            WHERE 
                PAY_TYPE = 'SUCCESS' AND MONTH(TRANSACTION_DATE) = MONTH(CURDATE()) AND YEAR(TRANSACTION_DATE) = YEAR(CURDATE())
            
            UNION ALL
            
            SELECT 
                'YEARLY' AS SalesType,
                FORMAT(SUM(amount), 0) AS Sales
            FROM 
                TBL_USER_TRADE 
            WHERE 
                PAY_TYPE = 'SUCCESS' AND YEAR(TRANSACTION_DATE) = YEAR(CURDATE());
            ";

        $stmt = $this->conn->prepare( $query );
        $stmt->execute();

        $list = [];
        while ($row = $stmt->fetch(PDO::FETCH_ASSOC)) {
            $list[] = $row;
        }
        return $list;
    }

    function read_trade_info_day($target_month){
        $query =

            "
            SELECT 
                DAY(TRANSACTION_DATE) AS SEARCH_TYPE, 
                SUM(amount) AS Sales
            FROM 
                TBL_USER_TRADE 
            WHERE 
                PAY_TYPE = 'SUCCESS' 
                AND YEAR(TRANSACTION_DATE) = YEAR(CURDATE()) 
                AND MONTH(TRANSACTION_DATE) = ".$target_month."
            GROUP BY 
                DAY(TRANSACTION_DATE)
                ORDER BY SEARCH_TYPE
            ";
        $stmt = $this->conn->prepare( $query );
        $stmt->execute();

        $list = [];
        while ($row = $stmt->fetch(PDO::FETCH_ASSOC)) {
            $list[] = $row;
        }
        return $list;
    }

    function read_trade_info_month($target_year){
        $query =

            "
            SELECT 
                MONTH(TRANSACTION_DATE) AS SEARCH_TYPE, 
                SUM(amount) AS Sales
            FROM 
                TBL_USER_TRADE 
            WHERE 
                PAY_TYPE = 'SUCCESS' 
                AND YEAR(TRANSACTION_DATE) = ".$target_year."
            GROUP BY 
                MONTH(TRANSACTION_DATE)
                ORDER BY SEARCH_TYPE
            ";

        $stmt = $this->conn->prepare( $query );
        $stmt->execute();

        $list = [];
        while ($row = $stmt->fetch(PDO::FETCH_ASSOC)) {
            $list[] = $row;
        }
        return $list;
    }

    function read_trade_info_year(){
        $query =

            "
            SELECT 
                YEAR(TRANSACTION_DATE) AS SEARCH_TYPE, 
                SUM(amount) AS Sales
            FROM 
                TBL_USER_TRADE 
            WHERE 
                PAY_TYPE = 'SUCCESS' 
            GROUP BY 
                YEAR(TRANSACTION_DATE)
                ORDER BY SEARCH_TYPE
            ";

        $stmt = $this->conn->prepare( $query );
        $stmt->execute();

        $list = [];
        while ($row = $stmt->fetch(PDO::FETCH_ASSOC)) {
            $list[] = $row;
        }
        return $list;
    }
}
