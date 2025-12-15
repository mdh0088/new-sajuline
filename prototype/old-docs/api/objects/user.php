<?php
// 'user' object
class User{

    // database connection and table name
    private $conn;
    private $table_name = "TBL_USER";

    // object properties
    public $IDX;
    public $NAME;
    public $NICK_NAME;
    public $USER_ID;
    public $PASSWORD;
    public $EMAIL;
    public $PHONE;
    public $USER_STATUS;
    public $JOIN_TYPE;
    public $REGIST_DATE;
    public $LAST_LOGIN;

    // constructor
    public function __construct($db){
        $this->conn = $db;
    }

    
    function login(){
        
    }
    
    // create new user record
    function create(){

        $this->PASSWORD    = htmlspecialchars(strip_tags($this->PASSWORD));
        $password_hash = password_hash($this->PASSWORD, PASSWORD_BCRYPT);

        // insert query
        $query =
            "
                INSERT INTO " . $this->table_name . " SET
                NAME            = '".htmlspecialchars(strip_tags($this->NAME))."'
                , NICK_NAME     = '".htmlspecialchars(strip_tags($this->NICK_NAME))."'
                , USER_ID       = '".htmlspecialchars(strip_tags($this->USER_ID))."'
                , PASSWORD      = '".$password_hash."'
                , EMAIL         = '".htmlspecialchars(strip_tags($this->EMAIL))."'
                , PHONE         = '".htmlspecialchars(strip_tags($this->PHONE))."'
                , JOIN_TYPE     = '".htmlspecialchars(strip_tags($this->JOIN_TYPE))."'
                , REGIST_DATE   = NOW()
                , LAST_LOGIN    = NOW()
            ";

        if($this->conn->prepare($query)->execute()){
            return true;
        }
        return false;
    }

    // check if given email exist in the database
    function emailExists(){

        // query to check if email exists
        $query =
            "
                SELECT 
                    id
                     , firstname
                     , lastname
                     , password
                FROM " . $this->table_name . "  WHERE 
                    email = '".htmlspecialchars(strip_tags($this->email))."'
                LIMIT 0,1
            ";

        // prepare the query
        $stmt = $this->conn->prepare( $query );

        // execute the query
        $stmt->execute();

        // get number of rows
        $num = $stmt->rowCount();

        // if email exists, assign values to object properties for easy access and use for php sessions
        if($num>0){

            // get record details / values
            $row = $stmt->fetch(PDO::FETCH_ASSOC);

            // assign values to object properties
            $this->id = $row['id'];
            $this->firstname = $row['firstname'];
            $this->lastname = $row['lastname'];
            $this->password = $row['password'];

            // return true because email exists in the database
            return true;
        }

        // return false if email does not exist in the database
        return false;
    }


    // read products
    function read(){

        // select all query
        $query = " SELECT * FROM " . $this->table_name . "   ";

        // prepare query statement
        return $this->conn->prepare($query)->execute();
    }

    // used when filling up the update product form
    function readOne($obj){

        // query to read single record
        $query =

            "
            SELECT
                *
            FROM " . $this->table_name . " WHERE 1=1
            ";

        foreach ($obj as $key => $value) {
            $query .= "and ".$key." = '".$value."' ";
        }


        // prepare query statement
        $stmt = $this->conn->prepare( $query );
        // bind id of product to be updated
        // $stmt->bindParam(1, $this->IDX);
        // execute query
        $stmt->execute();
        // get retrieved row
        $row = $stmt->fetch(PDO::FETCH_ASSOC);


        // set values to object properties
        /*
        $this->IDX         = $row['IDX'];
        $this->NAME        = $row['NAME'];
        $this->NICK_NAME   = $row['NICK_NAME'];
        $this->USER_ID     = $row['USER_ID'];
        $this->PASSWORD    = $row['PASSWORD'];
        $this->EMAIL       = $row['EMAIL'];
        $this->PHONE       = $row['PHONE'];
        $this->JOIN_TYPE   = $row['JOIN_TYPE'];
        $this->REGIST_DATE = $row['REGIST_DATE'];
        $this->LAST_LOGIN  = $row['LAST_LOGIN'];
        */
        return $row;
    }

    // delete the user
    function delete(){

        // delete query
        $query = "DELETE FROM " . $this->table_name . " WHERE IDX = ?";

        // prepare query
        $stmt = $this->conn->prepare($query);

        // sanitize
        $this->IDX=htmlspecialchars(strip_tags($this->IDX));

        // bind id of record to delete
        $stmt->bindParam(1, $this->IDX);

        // execute query
        if($stmt->execute()){
            return true;
        }

        return false;
    }

    // search products
    function search($keywords){

        // select all query
        $query =
            "
            SELECT
                *
            FROM " . $this->table_name . "  WHERE
                NAME LIKE ? 
                OR NICK_NAME LIKE ? 
                OR USER_ID LIKE ?
           ";

        // prepare query statement
        $stmt = $this->conn->prepare($query);

        // sanitize
        $keywords=htmlspecialchars(strip_tags($keywords));
        $keywords = "%{$keywords}%";

        // bind
        $stmt->bindParam(1, $keywords);
        $stmt->bindParam(2, $keywords);
        $stmt->bindParam(3, $keywords);

        // execute query
        $stmt->execute();

        return $stmt;
    }

    // read products with pagination
    public function readPaging($from_record_num, $records_per_page){

        // select query
        $query =
            "
            SELECT
                *
            FROM " . $this->table_name . "
            ORDER BY IDX DESC
            LIMIT ?, ?
            ";

        // prepare query statement
        $stmt = $this->conn->prepare( $query );

        // bind variable values
        $stmt->bindParam(1, $from_record_num, PDO::PARAM_INT);
        $stmt->bindParam(2, $records_per_page, PDO::PARAM_INT);

        // execute query
        $stmt->execute();

        // return values from database
        return $stmt;
    }

    // used for paging products
    public function count(){
        $query = "SELECT COUNT(*) as total_rows FROM " . $this->table_name . "";

        $stmt = $this->conn->prepare( $query );
        $stmt->execute();
        $row = $stmt->fetch(PDO::FETCH_ASSOC);

        return $row['total_rows'];
    }


    // create new user record
    function insertUser($obj){

        $obj->PASSWORD    = htmlspecialchars(strip_tags($obj->PASSWORD));
        $password_hash = password_hash($obj->PASSWORD, PASSWORD_BCRYPT);

        // insert query
        $query =
            "
                INSERT INTO TBL_USER SET
                NICK_NAME     = '".htmlspecialchars(strip_tags($obj->NICK_NAME))."'
                , USER_ID       = '".htmlspecialchars(strip_tags($obj->USER_ID))."'
                , PASSWORD      = '".$password_hash."'
                , EMAIL         = '".htmlspecialchars(strip_tags($obj->EMAIL))."'
                , PHONE         = '".htmlspecialchars(strip_tags($obj->PHONE))."'
                , JOIN_TYPE     = '".htmlspecialchars(strip_tags($obj->JOIN_TYPE))."'
                , REGIST_DATE   = NOW()
                , LAST_LOGIN    = NOW()
            ";

        if($this->conn->prepare($query)->execute()){
            return true;
        }
        return false;
    }

    function find_user_by_idx($obj){
        $query =

            "
            SELECT
                IDX
                , USER_ID
                , NICK_NAME
                , PHONE
            FROM TBL_USER WHERE
                IDX = '".$obj->IDX."'
                AND USER_STATUS !=3
            ";

        $stmt = $this->conn->prepare( $query );
        $stmt->execute();

        $row = $stmt->fetch(PDO::FETCH_ASSOC);
        return $row;
    }

    function find_user_by_phone($obj){
        $query =

            "
            SELECT
                IDX
                , USER_ID
                , EMAIL
                , PHONE
                , JOIN_TYPE
            FROM TBL_USER WHERE
                PHONE = '".$obj->PHONE."'
                AND USER_STATUS !=3
            ";

        $stmt = $this->conn->prepare( $query );
        $stmt->execute();

        $row = $stmt->fetch(PDO::FETCH_ASSOC);
        return $row;
    }

    function find_user_by_phone_and_id($obj){
        $query =

            "
            SELECT
                IDX
                , USER_ID
                , EMAIL
                , PHONE
                , JOIN_TYPE
            FROM TBL_USER WHERE
                PHONE = '".$obj->PHONE."'
                and USER_ID = '".$obj->USER_ID."'
                AND USER_STATUS !=3
            ";

        $stmt = $this->conn->prepare( $query );
        $stmt->execute();

        $row = $stmt->fetch(PDO::FETCH_ASSOC);
        return $row;
    }

    function read_review_history($obj){
        $query =

            "
                SELECT
                    AA.IDX
                     
                   , BB.NICK_NAME AS USER_NICK_NAME
                   , AA.USER_CONT
                   , DATE_FORMAT(AA.USER_REGIST_DATE,'%Y.%m.%d') as USER_REGIST_DATE
                   
                   , CC.NICK_NAME AS CS_NICK_NAME
                   , CC.CODE
                   , AA.CS_CONT
                   , DATE_FORMAT(AA.CS_REGIST_DATE,'%Y.%m.%d') as CS_REGIST_DATE
                   
                FROM TBL_CS_REVIEW AA, TBL_USER BB, TBL_CS CC WHERE
                    AA.USER_IDX = '".$obj -> IDX."'
                    AND BB.USER_STATUS !=3
                    AND AA.USER_IDX = BB.IDX
                    AND AA.CS_IDX = CC.IDX
                    AND AA.SHOW_YN = 'Y'
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

    function read_faq_history($obj){
        $query =

            "
                SELECT
                    AA.IDX
                    , BB.NICK_NAME AS USER_NICK_NAME
                    , DATE_FORMAT(AA.USER_REGIST_DATE,'%y.%m.%d %H:%m') AS USER_REGIST_DATE
                    , AA.USER_CONT
                     
                    , CC.CODE
                    , CC.NICK_NAME AS CS_NICK_NAME
                    , DATE_FORMAT(AA.CS_REGIST_DATE,'%y.%m.%d %H:%m') AS CS_REGIST_DATE
                    , AA.CS_CONT
                    , CASE WHEN AA.CS_CONT IS NULL THEN 'Y' ELSE 'N' END AS IS_CHK
                FROM TBL_CS_FAQ AA, TBL_USER BB, TBL_CS CC WHERE
                    AA.USER_IDX = BB.IDX
                    AND BB.USER_STATUS !=3                                         
                    AND AA.CS_IDX = CC.IDX
                    AND AA.USER_IDX = '".$obj -> IDX."'
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

    // create new user record
    function update($obj){

        $obj->PASSWORD    = htmlspecialchars(strip_tags($obj->PASSWORD));
        $password_hash = password_hash($obj->PASSWORD, PASSWORD_BCRYPT);

        // insert query
        $query =
            "
                UPDATE TBL_USER SET
                 UPDATE_DATE   = NOW()
            ";

        if ($obj->PASSWORD != '') {
            $query .= "
                , PASSWORD      = '".$password_hash."'
            ";
        }
        $query .=" WHERE IDX =".$obj->IDX;


        if($this->conn->prepare($query)->execute()){
            return true;
        }
        return false;
    }

    function update_pw($obj){

        $obj->PASSWORD    = htmlspecialchars(strip_tags($obj->PASSWORD));
        $password_hash = password_hash($obj->PASSWORD, PASSWORD_BCRYPT);

        // insert query
        $query =
            "
                UPDATE TBL_USER SET
                 PASSWORD      = '".$password_hash."'
                , UPDATE_DATE   = NOW()
                WHERE IDX =".$obj->IDX."
            ";

        if($this->conn->prepare($query)->execute()){
            return true;
        }
        return false;
    }


    function read_charge_info($obj){
        $query =

            "
                 SELECT
                 	date_format(TRANSACTION_DATE,'%y.%m.%d') AS TRANSACTION_DATE
                    , PRODUCT_NAME
                    , AMOUNT
                    , CASE
                        WHEN PAY_TYPE = 'SUCCESS' THEN '성공'
                        WHEN PAY_TYPE = 'CANCEL' THEN '취소'
                        WHEN PAY_TYPE = 'HOLD' THEN '입금대기'
                        WHEN PAY_TYPE = 'FAIL' THEN '실패' 
                      END AS PAY_TYPE
                FROM TBL_USER_TRADE WHERE
                    USER_IDX= ".$obj->IDX."
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

    function read_admin_faq_info($user_idx){
        $query =

            "
                SELECT
                    AA.IDX
                   , BB.NICK_NAME AS USER_NICK_NAME
                   , AA.USER_CONT
                   , AA.USER_TITLE
                   , DATE_FORMAT(AA.USER_REGIST_DATE,'%Y.%m.%d') as USER_REGIST_DATE
                   , AA.ADMIN_CONT
                   , DATE_FORMAT(AA.ADMIN_REGIST_DATE,'%Y.%m.%d') as ADMIN_REGIST_DATE
            
                   
                FROM TBL_ADMIN_FAQ AA, TBL_USER BB WHERE
                    AA.USER_IDX = BB.IDX
                    AND AA.USER_IDX = '".$user_idx."'
                    AND BB.USER_STATUS !=3                               
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

    function doFaq($obj){


        $title = strip_tags($obj->TITLE);
        $title = htmlentities($title, ENT_QUOTES);

        $cont = strip_tags($obj->CONT);
        $cont = htmlentities($cont, ENT_QUOTES);

        // insert query
        $query =
            "
                INSERT INTO TBL_ADMIN_FAQ SET
                USER_IDX            = '".htmlspecialchars(strip_tags($obj->USER_IDX))."'
                , USER_TITLE    =       '".$title."'
                , USER_CONT              = '".$cont."'
                , USER_REGIST_DATE       = NOW()
            ";


        if($this->conn->prepare($query)->execute()){
            return true;
        }
        return false;
    }

    function admin_user_list(){
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
                    USER_STATUS !='3'
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

    function admin_user_info($idx){
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
                , CASE 
                    WHEN USER_STATUS = '1' THEN '활성'
                    WHEN USER_STATUS = '2' THEN '휴면'
                    WHEN USER_STATUS = '3' THEN '탈퇴'
                  END AS USER_STATUS
            FROM TBL_USER WHERE
                IDX = '".$idx."'
            ";

        $stmt = $this->conn->prepare( $query );
        $stmt->execute();

        $row = $stmt->fetch(PDO::FETCH_ASSOC);
        return $row;
    }

    function delete_user($obj){


        $query =
            "
                UPDATE TBL_USER SET
                 NICK_NAME = ''
                , USER_ID  = CONCAT('WithDrawal@',USER_ID)
                , PASSWORD = ''
                , EMAIL    = CONCAT('WithDrawal@',EMAIL)
                , PHONE    = ''
                , USER_STATUS = 3
                , JOIN_TYPE = ''
                WHERE IDX =".$obj->IDX."
            ";

        if($this->conn->prepare($query)->execute()){
            return true;
        }
        return false;
    }

    function add_delete_log($obj){


        // insert query
        $query =
            "
                INSERT INTO TBL_USER_EX SET
                    USER_IDX    = '".$obj['IDX']."'
                    , USER_ID   = '".$obj['USER_ID']."'
                    , NICK_NAME = '".$obj['NICK_NAME']."'
                    , PHONE = '".$obj['PHONE']."'
                    , EMAIL = '".$obj['EMAIL']."'
                    , REGIST_DATE = NOW()
            ";

        if($this->conn->prepare($query)->execute()){
            return true;
        }
        return false;
    }


    function get_ex_info($phone){
        $query =

            "
            SELECT
                MAX(REGIST_DATE)
                , DATEDIFF(NOW(), MAX(REGIST_DATE)) AS ex_day
            FROM TBL_USER_EX WHERE
                PHONE ='".$phone."'
            ";

        $stmt = $this->conn->prepare( $query );
        $stmt->execute();

        $row = $stmt->fetch(PDO::FETCH_ASSOC);
        return $row;
    }

    function add_event_log($event_idx,$user_idx,$info,$point){


        // insert query
        $query =
            "
                INSERT INTO TBL_EVENT_LOG SET
                    EVENT_IDX    = '".$event_idx."'
                    , USER_IDX   = '".$user_idx."'
                    , INFO = '".$info."'
                    , POINT = '".$point."'
                    , REGIST_DATE = NOW()
            ";

        if($this->conn->prepare($query)->execute()){
            return true;
        }
        return false;
    }


    function read_dumy_user(){
        $query =

            "
                SELECT
                   *
                FROM TBL_USER where
                   	LEFT(USER_ID,'4') ='dumy'
                   	ORDER BY IDX
            ";



        $stmt = $this->conn->prepare( $query );
        $stmt->execute();

        $list = [];
        while ($row = $stmt->fetch(PDO::FETCH_ASSOC)) {
            $list[] = $row;
        }

        return $list;
    }

    function read_bookmark($user_idx){
        $query =

            "
                SELECT 
                    AA.IDX
                    , AA.IMG
                    ,CASE 
                        WHEN AA.TYPE = 1 THEN '타로'
                        WHEN AA.TYPE = 2 THEN '신점'
                        WHEN AA.TYPE = 3 THEN '역학'
                        WHEN AA.TYPE = 4 THEN '사주'
                    END AS TYPE
                   ,CASE WHEN AA.CS_DATE >= DATE_SUB(NOW(), INTERVAL 30 DAY) 
                         THEN '신규'
                         ELSE '기존'
                    END AS CHK_NEW
                   , AA.NICK_NAME
                   , AA.CODE
                   , AA.AFTER_AMOUNT
                   , AA.GRADE
                   , STATUS
                FROM TBL_CS AA, TBL_USER_BOOKMARK BB WHERE
                	  AA.IDX = BB.CS_IDX
                	  AND BB.USER_IDX ='".$user_idx."'
                    AND AA.APPROVAL_YN = 'Y'         
                    AND AA.SHOW_YN = 'Y'
                    AND (AA.STATUS = 1 or AA.STATUS = 2)
                    ORDER BY AA.STATUS, RAND()
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
