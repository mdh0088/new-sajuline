<?php
// 'user' object
class Recruit{

    // database connection and table name
    private $conn;
    private $table_name = "TBL_CS";


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

    function update_approval($obj){


        // insert query
        $query =
            "
                UPDATE TBL_CS SET
                APPROVAL_YN = 'Y'
                , CODE      = '".htmlspecialchars(strip_tags($obj->CODE))."'
                , CS_DATE   = NOW()
                WHERE IDX = '".htmlspecialchars(strip_tags($obj->IDX))."'
            ";


        if($this->conn->prepare($query)->execute()){
            return true;
        }
        return false;
    }
}
