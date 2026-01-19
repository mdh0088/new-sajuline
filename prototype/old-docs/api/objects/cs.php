<?php
// 'user' object
class Counselor{

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


        // insert query
        $query =
            "
                INSERT INTO TBL_CS SET
                TYPE            = '".htmlspecialchars(strip_tags($obj->TYPE))."'
                , NICK_NAME     = '".htmlspecialchars(strip_tags($obj->NICK_NAME))."'
                , NAME          = '".htmlspecialchars(strip_tags($obj->NAME))."'
                , PHONE         = '".htmlspecialchars(strip_tags($obj->PHONE))."'
                , EMAIL         = '".htmlspecialchars(strip_tags($obj->EMAIL))."'
                , ADDRESS       = '".htmlspecialchars(strip_tags($obj->ADDRESS))."'
                , SHORT_INFO     = '".htmlspecialchars(strip_tags($obj->SHORT_INFO))."'
                , GREETING      = '".htmlspecialchars(strip_tags($obj->GREETING))."'
                , CAREER        = '".htmlspecialchars(strip_tags($obj->CAREER))."'
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
                APPROVAL_YN='Y'
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

    function read_main($obj){
        $query=
            "
                select
                    *
                FROM 
                (	
                    SELECT
                        AA.IDX
                        , AA.NICK_NAME
                        , AA.IMG
                        , AA.TYPE
                        , AA.CODE
                        , AA.GRADE
                        , AA.SHORT_INFO
                        , AA.GREETING
                        , AA.CAREER
                        , AA.NOTICE
                        , AA.WORK_TIME
                        , AA.AFTER_AMOUNT
                        , AA.STATUS
                        , IFNULL(COUNT_REAL.CNT,0) + IFNULL(COUNT_DUMY.CNT,0) AS TOTAL_REVIEW_CNT
                        , COUNT_BOOK.CNT AS BOOK_CNT
                    FROM
                        TBL_CS AA
                    LEFT JOIN (
                        SELECT
                            CS_IDX,
                            COUNT(*) AS CNT
                        FROM
                            TBL_CS_REVIEW WHERE SHOW_YN = 'Y'
                        GROUP BY
                            CS_IDX) COUNT_REAL ON AA.IDX = COUNT_REAL.CS_IDX
                    LEFT JOIN (
                        SELECT
                            CS_IDX,
                            COUNT(*) AS CNT
                        FROM
                            TBL_CS_REVIEW_DUMY
                        WHERE
                            USER_REGIST_DATE <= NOW()
                        GROUP BY
                            CS_IDX) COUNT_DUMY ON AA.IDX = COUNT_DUMY.CS_IDX
                    LEFT JOIN (
                        SELECT
                            CS_IDX,
                            COUNT(*) AS CNT
                        FROM
                            TBL_USER_BOOKMARK
                ";
                if ($obj->TYPE=='bookmark') {
                    $query .= " WHERE TBL_USER_BOOKMARK.USER_IDX = '".$obj->USER_IDX."' ";
                }

                $query .="
                        GROUP BY
                            CS_IDX) COUNT_BOOK ON AA.IDX = COUNT_BOOK.CS_IDX
                    WHERE
                        AA.APPROVAL_YN = 'Y'
                        AND AA.SHOW_YN = 'Y'
                ";
                if ($obj->TYPE=='all') {
                    $query.=" ORDER BY 
                     CASE 
                       WHEN STATUS = 2 THEN 1 
                       WHEN STATUS = 1 THEN 2 
                       ELSE 3 
                     END ,RAND()";
                } else if($obj->TYPE=='reco') {
                    $query.="  AND (STATUS=1 OR STATUS=3) ORDER BY STATUS,RAND() ";
                } else if($obj->TYPE=='new') {
                    $query .= "  and NEW_YN = 'Y' AND (STATUS=1 OR STATUS=3) ORDER BY STATUS,RAND()";
                } else if($obj->TYPE=='bookmark') {
                    $query .= "  AND COUNT_BOOK.CNT > 0 ORDER BY STATUS,RAND()";
                }

                $query .= " ) T1 ";

                if ($obj->ORDER_TYPE=='review') {
                    $query.=" ORDER BY TOTAL_REVIEW_CNT DESC";
                } else if($obj->ORDER_TYPE=='bookmark') {
                    $query.=" ORDER BY BOOK_CNT DESC";
                } else if($obj->ORDER_TYPE=='point') {
                    $query.=" ORDER BY AFTER_AMOUNT DESC";
                }

        //$query.="  ORDER BY STATUS,RAND()";


        //echo $query;
        $stmt = $this->conn->prepare( $query );
        $stmt->execute();

        $list = [];
        /*
        while ($row = $stmt->fetch(PDO::FETCH_ASSOC)) {
            $list[] = $row;
        }
        */
        while ($row = $stmt->fetch(PDO::FETCH_ASSOC)) {
           //$review_list = $this->read_main_review($row['IDX']);
           //$row['review_list'] = $review_list;
           $list[] = $row;
        }
        return $list;
    }

    function read_main_review($cs_idx){
        /*
        $query =

            "
            SELECT
                AA.USER_CONT
                , BB.NICK_NAME
            FROM TBL_CS_REVIEW AA, TBL_USER BB WHERE
                CS_IDX ='".$cs_idx."'
                AND BB.USER_STATUS !=3
                AND AA.USER_IDX = BB.IDX
            ORDER BY USER_REGIST_DATE DESC
            limit 3
            ";
        */
        $query=
            "
            SELECT
                IDX
                , CS_IDX
                , NICK_NAME
                , USER_CONT
                , USER_REGIST_DATE AS REAL_USER_REGIST_DATE
                , DATE_FORMAT(USER_REGIST_DATE,'%Y.%m.%d') as USER_REGIST_DATE
                , CS_NICK_NAME
                , CODE
                , CS_CONT 
                , DATE_FORMAT(CS_REGIST_DATE,'%Y.%m.%d') as CS_REGIST_DATE
            FROM (
            (SELECT
                 AA.IDX
                , CC.IDX AS CS_IDX
                , BB.NICK_NAME AS NICK_NAME
                , AA.USER_CONT
                , AA.USER_REGIST_DATE
                
                , CC.NICK_NAME AS CS_NICK_NAME
                , CC.CODE
                , AA.CS_CONT
                , AA.CS_REGIST_DATE
            FROM TBL_CS_REVIEW AA, TBL_USER BB, TBL_CS CC
            WHERE
                 AA.CS_IDX = '".$cs_idx."'
                 AND BB.USER_STATUS !=3
                 AND AA.USER_IDX = BB.IDX
                 AND AA.CS_IDX = CC.IDX
                 AND AA.SHOW_YN = 'Y'
                 ORDER BY AA.USER_REGIST_DATE DESC
                 LIMIT 3
            
            )
            
            UNION ALL
            
            (SELECT * FROM
                (SELECT
                    AA.IDX
                    , BB.IDX AS CS_IDX
                    , AA.USER_ID AS NICK_NAME
                    , AA.USER_CONT
                    , AA.USER_REGIST_DATE
                    , BB.NICK_NAME AS CS_NICK_NAME
                    , BB.CODE
                    , AA.CS_CONT
                    , AA.CS_REGIST_DATE
                FROM TBL_CS_REVIEW_DUMY AA, TBL_CS BB
                WHERE
                     AA.CS_IDX = '".$cs_idx."'
                     AND AA.CS_IDX = BB.IDX
                    AND AA.USER_REGIST_DATE <= NOW()
                ORDER BY USER_REGIST_DATE DESC
                LIMIT 3) subquery
            )
            ) T1 
            ORDER BY REAL_USER_REGIST_DATE DESC
            LIMIT 3
            ";

        $stmt = $this->conn->prepare( $query );
        $stmt->execute();

        $list = [];
        while ($row = $stmt->fetch(PDO::FETCH_ASSOC)) {
            $list[] = $row;
        }
        return $list;
    }

    function read_main_review_list(){
        /*
        $query =

            "
            SELECT
                AA.IDX
                , AA.USER_CONT
                , BB.NICK_NAME
                , AA.CS_IDX
            FROM TBL_CS_REVIEW AA, TBL_USER BB WHERE
                AA.USER_IDX = BB.IDX
                AND BB.USER_STATUS !=3
                AND AA.USER_CONT IS NOT NULL
                AND AA.USER_CONT != ''
            ORDER BY USER_REGIST_DATE DESC
            limit 5
            ";
        */


        $query=
            "
            SELECT
                 IDX
                , CS_IDX
                , NICK_NAME
                , USER_CONT
                , USER_REGIST_DATE AS REAL_USER_REGIST_DATE
                , DATE_FORMAT(USER_REGIST_DATE,'%Y.%m.%d') as USER_REGIST_DATE
                , CS_NICK_NAME
                , CODE
                , CS_CONT 
                , DATE_FORMAT(CS_REGIST_DATE,'%Y.%m.%d') as CS_REGIST_DATE
            FROM (
            (SELECT
                 AA.IDX
                 , AA.CS_IDX
                , BB.NICK_NAME AS NICK_NAME
                , AA.USER_CONT
                , AA.USER_REGIST_DATE
                
                , CC.NICK_NAME AS CS_NICK_NAME
                , CC.CODE
                , AA.CS_CONT
                , AA.CS_REGIST_DATE
            FROM TBL_CS_REVIEW AA, TBL_USER BB, TBL_CS CC
            WHERE
                 BB.USER_STATUS !=3
                 AND AA.USER_IDX = BB.IDX
                 AND AA.CS_IDX = CC.IDX
                 AND AA.USER_CONT IS NOT NULL
                 AND AA.USER_CONT != ''   
                 AND AA.SHOW_YN = 'Y'
                 ORDER BY AA.USER_REGIST_DATE DESC
            
            )
            
            UNION ALL
            
            (SELECT * FROM
                (SELECT
                    AA.IDX
                    , AA.CS_IDX
                    , AA.USER_ID AS NICK_NAME
                    , AA.USER_CONT
                    , AA.USER_REGIST_DATE
                    , BB.NICK_NAME AS CS_NICK_NAME
                    , BB.CODE
                    , AA.CS_CONT
                    , AA.CS_REGIST_DATE
                FROM TBL_CS_REVIEW_DUMY AA, TBL_CS BB
                WHERE
                     AA.CS_IDX = BB.IDX
                    AND AA.REGIST_DATE <= NOW()
                     AND AA.USER_CONT IS NOT NULL
                     AND AA.USER_CONT != ''                  
                ORDER BY USER_REGIST_DATE DESC) subquery
            )
            ) T1 
            ORDER BY REAL_USER_REGIST_DATE DESC
            LIMIT 3
            ";

        $stmt = $this->conn->prepare( $query );
        $stmt->execute();

        $list = [];
        while ($row = $stmt->fetch(PDO::FETCH_ASSOC)) {
            $list[] = $row;
        }
        return $list;
    }


    function read_detail($obj){

        $query =

            "
            SELECT
                IDX
                , NICK_NAME
                , IMG
                , TYPE
                , CS_KEYWORD
                , CODE
                , GRADE
                , SHORT_INFO
                , NOTICE
                , GREETING  
                , CAREER
                , WORK_TIME
                , STATUS
            FROM TBL_CS WHERE 
                APPROVAL_YN='Y'
                and SHOW_YN = 'Y'
                and IDX = '".$obj -> IDX."'
            ";



        $stmt = $this->conn->prepare( $query );
        $stmt->execute();

        $row = $stmt->fetch(PDO::FETCH_ASSOC);

        $review_cnt = $this->read_cs_review_cnt($row['IDX']);
        $row['review_cnt'] = $review_cnt;

        $faq_cnt = $this->read_cs_faq_cnt($row['IDX']);
        $row['faq_cnt'] = $faq_cnt;

        return $row;
    }

    function read_cs_review_cnt($idx){
        /*
        $query =

            "
            SELECT
                count(*) as CNT
            FROM TBL_CS_REVIEW WHERE
                CS_IDX = '".$idx."'
            ";
        */


        $query=
            "
            SELECT
                count(*) as CNT
            FROM (
            (SELECT
                 AA.IDX
                  
                , BB.NICK_NAME AS USER_NICK_NAME
                , AA.USER_CONT
                , DATE_FORMAT(AA.USER_REGIST_DATE,'%Y.%m.%d') as USER_REGIST_DATE
                
                , CC.NICK_NAME AS CS_NICK_NAME
                , CC.CODE
                , AA.CS_CONT
                , DATE_FORMAT(AA.CS_REGIST_DATE,'%Y.%m.%d') as CS_REGIST_DATE
            FROM TBL_CS_REVIEW AA, TBL_USER BB, TBL_CS CC
            WHERE
                 AA.CS_IDX = '".$idx."'
                 AND BB.USER_STATUS !=3
                 AND AA.USER_IDX = BB.IDX
                 AND AA.CS_IDX = CC.IDX
                 AND AA.SHOW_YN = 'Y'
                 ORDER BY AA.USER_REGIST_DATE DESC
            
            )
            
            UNION ALL
            
            (SELECT * FROM
                (SELECT
                    AA.IDX
                    , AA.USER_ID AS USER_NICK_NAME
                    , AA.USER_CONT
                    , DATE_FORMAT(AA.USER_REGIST_DATE,'%Y.%m.%d') as USER_REGIST_DATE
                    , BB.NICK_NAME AS CS_NICK_NAME
                    , BB.CODE
                    , AA.CS_CONT
                    , DATE_FORMAT(AA.CS_REGIST_DATE,'%Y.%m.%d') as CS_REGIST_DATE
                FROM TBL_CS_REVIEW_DUMY AA, TBL_CS BB
                WHERE
                     AA.CS_IDX = '".$idx."'
                     AND AA.CS_IDX = BB.IDX
                    AND AA.REGIST_DATE <= NOW()
                ORDER BY USER_REGIST_DATE DESC) subquery
            )
            ) T1 
            ORDER BY USER_REGIST_DATE DESC
            ";


        $stmt = $this->conn->prepare( $query );
        $stmt->execute();

        $row = $stmt->fetch(PDO::FETCH_ASSOC);
        return $row;
    }

    function read_cs_faq_cnt($idx){

        $query =

            "
            SELECT
                count(*) as CNT
            FROM TBL_CS_FAQ WHERE
                CS_IDX = '".$idx."'
            ";




        $stmt = $this->conn->prepare( $query );
        $stmt->execute();

        $row = $stmt->fetch(PDO::FETCH_ASSOC);
        return $row;
    }


    function read_review($obj){
        /*
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
                    AA.CS_IDX = '".$obj -> IDX."'
                    AND BB.USER_STATUS !=3
                    AND AA.USER_IDX = BB.IDX
                    AND AA.CS_IDX = CC.IDX
                    ORDER BY AA.USER_REGIST_DATE DESC
                    LIMIT ".$obj->page.",5

            ";
        */


        $query=
            "
            SELECT
                IDX
                , USER_NICK_NAME
                , USER_CONT
                , USER_REGIST_DATE AS REAL_USER_REGIST_DATE
                , DATE_FORMAT(USER_REGIST_DATE,'%Y.%m.%d') AS USER_REGIST_DATE
                , CS_NICK_NAME
                , CODE
                , CS_CONT  
                , DATE_FORMAT(CS_REGIST_DATE,'%Y.%m.%d') AS CS_REGIST_DATE
            FROM (
            (SELECT
                 AA.IDX
                  
                , BB.NICK_NAME AS USER_NICK_NAME
                , AA.USER_CONT
                , AA.USER_REGIST_DATE
                
                , CC.NICK_NAME AS CS_NICK_NAME
                , CC.CODE
                , AA.CS_CONT
                , AA.CS_REGIST_DATE
            FROM TBL_CS_REVIEW AA, TBL_USER BB, TBL_CS CC
            WHERE
                 AA.CS_IDX = '".$obj -> IDX."'
                 AND BB.USER_STATUS !=3
                 AND AA.USER_IDX = BB.IDX
                 AND AA.CS_IDX = CC.IDX
                 AND AA.SHOW_YN = 'Y'
                 ORDER BY AA.USER_REGIST_DATE DESC
            
            )
            
            UNION ALL
            
            (SELECT * FROM
                (SELECT
                    AA.IDX
                    , AA.USER_ID AS USER_NICK_NAME
                    , AA.USER_CONT
                    , AA.USER_REGIST_DATE
                    , BB.NICK_NAME AS CS_NICK_NAME
                    , BB.CODE
                    , AA.CS_CONT
                    , AA.CS_REGIST_DATE
                FROM TBL_CS_REVIEW_DUMY AA, TBL_CS BB
                WHERE
                     AA.CS_IDX = '".$obj -> IDX."'
                     AND AA.CS_IDX = BB.IDX
                    AND AA.REGIST_DATE <= NOW()
                ORDER BY USER_REGIST_DATE DESC) subquery
            )
            ) T1 
            ORDER BY REAL_USER_REGIST_DATE DESC
            LIMIT ".$obj->page.",5
            ";



        $stmt = $this->conn->prepare( $query );
        $stmt->execute();

        $list = [];
        while ($row = $stmt->fetch(PDO::FETCH_ASSOC)) {
            $list[] = $row;
        }

        return $list;
    }


    function read_faq($obj){
        $query =

            "
                SELECT
                    AA.IDX
                    , BB.NICK_NAME AS USER_NICK_NAME
                    , DATE_FORMAT(AA.USER_REGIST_DATE,'%y.%m.%d') AS USER_REGIST_DATE
                    , CC.CODE
                    , CC.NICK_NAME AS CS_NICK_NAME
                    , DATE_FORMAT(AA.CS_REGIST_DATE,'%y.%m.%d') AS CS_REGIST_DATE
                    , CASE WHEN AA.CS_CONT IS NULL THEN 'Y' ELSE 'N' END AS IS_CHK
                FROM TBL_CS_FAQ AA, TBL_USER BB, TBL_CS CC WHERE
                    AA.USER_IDX = BB.IDX
                    AND BB.USER_STATUS !=3                                         
                    AND AA.CS_IDX = CC.IDX
                    AND AA.CS_IDX = '".$obj -> IDX."'
                    ORDER BY AA.USER_REGIST_DATE DESC
                    LIMIT ".$obj->page.",5
            ";
        $stmt = $this->conn->prepare( $query );
        $stmt->execute();

        $list = [];
        while ($row = $stmt->fetch(PDO::FETCH_ASSOC)) {
            $list[] = $row;
        }

        return $list;
    }


    function read_faq_total_page($idx){
        $query =

            "
            SELECT
                count(*) as CNT
            FROM TBL_CS_FAQ WHERE
                CS_IDX = '".$idx."'
            ";

        $stmt = $this->conn->prepare( $query );
        $stmt->execute();

        $row = $stmt->fetch(PDO::FETCH_ASSOC);
        return $row;
    }


    // 1개 리턴용
    function readOne($idx){
        $query =

            "
            SELECT
                *
            FROM TBL_CS WHERE 
                APPROVAL_YN='Y'
                and IDX = ".$idx."
            ORDER BY CS_DATE DESC
            ";

        $stmt = $this->conn->prepare( $query );
        $stmt->execute();

        $row = $stmt->fetch(PDO::FETCH_ASSOC);
        return $row;
    }

    function update_approval($obj){


        $query =
            "
                UPDATE TBL_CS SET
                APPROVAL_YN     = 'Y'
                , CS_DATE  = NOW()
                WHERE IDX = '".htmlspecialchars(strip_tags($obj->IDX))."'
            ";


        if($this->conn->prepare($query)->execute()){
            return true;
        }
        return false;
    }

    function update($obj){


        $notice = strip_tags($obj->NOTICE);
        $notice = htmlentities($notice, ENT_QUOTES);

        $career = strip_tags($obj->CAREER);
        $career = htmlentities($career, ENT_QUOTES);

        $greeting = strip_tags($obj->GREETING);
        $greeting = htmlentities($greeting, ENT_QUOTES);

        // insert query
        $query =
            "
                UPDATE TBL_CS SET
                    NAME            = '".htmlspecialchars(strip_tags($obj->NAME))."'
                    , NICK_NAME       = '".htmlspecialchars(strip_tags($obj->NICK_NAME))."'
                    , IMG             = '".htmlspecialchars(strip_tags($obj->IMG))."'
                    , CS_KEYWORD      = '".htmlspecialchars(strip_tags($obj->keywords))."'
                    , STATUS          = '".htmlspecialchars(strip_tags($obj->STATUS))."'
                    , CODE            = '".htmlspecialchars(strip_tags($obj->CODE))."'
                    , GRADE           = '".htmlspecialchars(strip_tags($obj->GRADE))."'
                    , TYPE            = '".htmlspecialchars(strip_tags($obj->TYPE))."'
                    , SHORT_INFO      = '".htmlspecialchars(strip_tags($obj->SHORT_INFO))."'
                    , NOTICE          = '".$notice."'
                    , GREETING        = '".$greeting."'
                    , CAREER          = '".$career."'
                    , WORK_TIME       = '".htmlspecialchars(strip_tags($obj->WORK_TIME))."'
                    , AFTER_AMOUNT    = ".$obj->AFTER_AMOUNT."
                    , SHOW_YN         = '".htmlspecialchars(strip_tags($obj->SHOW_YN))."'
                    , NEW_YN         = '".htmlspecialchars(strip_tags($obj->NEW_YN))."'
                    , UPDATE_DATE     = NOW()
                where 
                    IDX = ".$obj->IDX."
            ";


        if($this->conn->prepare($query)->execute()){
            return true;
        }
        return false;
    }

    function update_pw($obj){

        $obj->PASSWORD    = htmlspecialchars(strip_tags($obj->PASSWORD));
        $password_hash = password_hash($obj->PASSWORD, PASSWORD_BCRYPT);

        $query =
            "
                UPDATE TBL_CS SET
                    PASSWORD      = '".$password_hash."'
                WHERE IDX = '".$obj->IDX."'
            ";


        if($this->conn->prepare($query)->execute()){
            return true;
        }
        return false;
    }

    function doReport($obj){

        $cont = strip_tags($obj->CONT);
        $cont = htmlentities($cont, ENT_QUOTES);

        // insert query
        $query =
            "
                INSERT INTO TBL_CS_REPORT SET
                USER_IDX            = '".htmlspecialchars(strip_tags($obj->USER_IDX))."'
                , TYPE              = '".htmlspecialchars(strip_tags($obj->TYPE))."'
                , CONT              = '".$cont."'
                , REVIEW_IDX        = '".htmlspecialchars(strip_tags($obj->IDX))."'
                , REGIST_DATE       = NOW()
    
            ";


        if($this->conn->prepare($query)->execute()){
            return true;
        }
        return false;
    }

    function doFaq($obj){

        $cont = strip_tags($obj->CONT);
        $cont = htmlentities($cont, ENT_QUOTES);

        // insert query
        $query =
            "
                INSERT INTO TBL_CS_FAQ SET
                USER_IDX            = '".htmlspecialchars(strip_tags($obj->USER_IDX))."'
                , CS_IDX            = '".htmlspecialchars(strip_tags($obj->IDX))."'
                , USER_CONT              = '".$cont."'
                , USER_REGIST_DATE       = NOW()
            ";


        if($this->conn->prepare($query)->execute()){
            return true;
        }
        return false;
    }

    function read_search($obj){
        $query =

            "
            SELECT
                *
            FROM TBL_CS WHERE
                (NICK_NAME LIKE '%".$obj->SEARCH_NAME."%'
                OR CS_KEYWORD LIKE '%".$obj->SEARCH_NAME."%'
                OR SHORT_INFO LIKE '%".$obj->SEARCH_NAME."%')
                AND APPROVAL_YN = 'Y'
                AND SHOW_YN ='Y'
                ORDER BY STATUS, CS_DATE DESC
            ";

        $stmt = $this->conn->prepare( $query );
        $stmt->execute();

        $list = [];
        while ($row = $stmt->fetch(PDO::FETCH_ASSOC)) {
            $list[] = $row;
        }

        return $list;
    }

    /**
    상담 후기 쿼리
     * 더미 쿼리랑 같이 노출, 만약 상담 후기가 10개를 먼저 채우고
     * 10개 이하라면 더미 쿼리가 10개를 마저 채움
     */
    function read_recent_reivew(){

        $query =

            "
            SELECT
                IMG
                , CS_NICK_NAME
                , CODE
                , USER_NICK_NAME
                , IDX
                , USER_IDX
                , CS_IDX
                , USER_CONT
                , DATE_FORMAT(USER_REGIST_DATE,'%Y-%m-%d') AS USER_REGIST_DATE
                , USER_REGIST_DATE AS REAL_USER_REGIST_DATE
                , CHATLOG_IDX
                , CHAT_TIME
            FROM (
            (SELECT
                BB.IMG
                , BB.NICK_NAME AS CS_NICK_NAME
                , BB.CODE
                , CC.NICK_NAME AS USER_NICK_NAME
                , AA.IDX
                , AA.USER_IDX
                , AA.CS_IDX
                , AA.USER_CONT
                , USER_REGIST_DATE
                , AA.CHATLOG_IDX
                , '' AS CHAT_TIME
            FROM TBL_CS_REVIEW AA, TBL_CS BB, TBL_USER CC
            WHERE
                AA.CS_IDX = BB.IDX
                AND CC.USER_STATUS != 3
                AND AA.USER_IDX = CC.IDX
                AND AA.SHOW_YN = 'Y'
            ORDER BY USER_REGIST_DATE DESC
            )
            
            UNION ALL
            
            (SELECT * FROM
                (SELECT
                    BB.IMG
                    , BB.NICK_NAME AS CS_NICK_NAME
                    , BB.CODE
                    , AA.USER_ID AS USER_NICK_NAME
                    , AA.IDX
                    , '' AS USER_IDX
                    , AA.CS_IDX
                    , AA.USER_CONT
                    , USER_REGIST_DATE
                    , NULL AS CHATLOG_IDX
                    , AA.CHAT_TIME
                FROM TBL_CS_REVIEW_DUMY AA, TBL_CS BB
                WHERE
                    AA.CS_IDX = BB.IDX
                    AND AA.REGIST_DATE <= NOW()
                ORDER BY USER_REGIST_DATE DESC) subquery
            )
            ) T1
            ORDER BY REAL_USER_REGIST_DATE DESC
            LIMIT 10
            ";
            /*
        $query =
        "
            SELECT
                BB.IMG
                , BB.NICK_NAME AS CS_NICK_NAME
                , BB.CODE
                , CC.NICK_NAME AS USER_NICK_NAME
                , AA.IDX
                , AA.USER_IDX
                , AA.CS_IDX
                , AA.USER_CONT
                , DATE_FORMAT(AA.USER_REGIST_DATE,'%Y.%m.%d') AS USER_REGIST_DATE
                , AA.CHATLOG_IDX
                , '' AS CHAT_TIME
            FROM TBL_CS_REVIEW AA, TBL_CS BB, TBL_USER CC
            WHERE
                AA.CS_IDX = BB.IDX
                AND CC.USER_STATUS != 3
                AND AA.USER_IDX = CC.IDX
            ORDER BY USER_REGIST_DATE DESC
        ";
            */


        $stmt = $this->conn->prepare( $query );
        $stmt->execute();

        $list = [];
        while ($row = $stmt->fetch(PDO::FETCH_ASSOC)) {
            $list[] = $row;
        }

        return $list;
    }

    function read_whole_review($obj){

        $query =

            "
            SELECT
                   IMG
                    , CS_NICK_NAME
                    , CODE
                    , USER_NICK_NAME
                    , IDX
                    , USER_IDX
                    , CS_IDX
                    , USER_CONT
                    , DATE_FORMAT(USER_REGIST_DATE,'%Y-%m-%d') AS USER_REGIST_DATE
                    , USER_REGIST_DATE AS REAL_USER_REGIST_DATE
                    , CHATLOG_IDX
                    , CHAT_TIME
            FROM (
            (SELECT
                BB.IMG
                , BB.NICK_NAME AS CS_NICK_NAME
                , BB.CODE
                , CC.NICK_NAME AS USER_NICK_NAME
                , AA.IDX
                , AA.USER_IDX
                , AA.CS_IDX
                , AA.USER_CONT
                , USER_REGIST_DATE
                , AA.CHATLOG_IDX
                , '' AS CHAT_TIME
            FROM TBL_CS_REVIEW AA, TBL_CS BB, TBL_USER CC
            WHERE
                AA.CS_IDX = BB.IDX
                AND CC.USER_STATUS != 3
                AND AA.USER_IDX = CC.IDX
                AND AA.SHOW_YN = 'Y'
            ORDER BY USER_REGIST_DATE DESC
            )
            
            UNION ALL
            
            (SELECT * FROM
                (SELECT
                    BB.IMG
                    , BB.NICK_NAME AS CS_NICK_NAME
                    , BB.CODE
                    , AA.USER_ID AS USER_NICK_NAME
                    , AA.IDX
                    , '' AS USER_IDX
                    , AA.CS_IDX
                    , AA.USER_CONT
                    , USER_REGIST_DATE
                    , NULL AS CHATLOG_IDX
                    , AA.CHAT_TIME
                FROM TBL_CS_REVIEW_DUMY AA, TBL_CS BB
                WHERE
                    AA.CS_IDX = BB.IDX
                    AND AA.REGIST_DATE <= NOW()
                ORDER BY USER_REGIST_DATE DESC) subquery
            )
            
            ) T1
            ORDER BY REAL_USER_REGIST_DATE DESC
            LIMIT ".$obj->page.",5
            ";


        $stmt = $this->conn->prepare( $query );
        $stmt->execute();

        $list = [];
        while ($row = $stmt->fetch(PDO::FETCH_ASSOC)) {
            $list[] = $row;
        }

        return $list;
    }

    function read_whole_review_cnt(){

        $query =

            "
            SELECT
                count(*) as CNT
            FROM (
            (SELECT
                BB.IMG
                , BB.NICK_NAME AS CS_NICK_NAME
                , BB.CODE
                , CC.NICK_NAME AS USER_NICK_NAME
                , AA.IDX
                , AA.USER_IDX
                , AA.CS_IDX
                , AA.USER_CONT
                , DATE_FORMAT(AA.USER_REGIST_DATE,'%Y.%m.%d') AS USER_REGIST_DATE
                , AA.CHATLOG_IDX
                , '' AS CHAT_TIME
            FROM TBL_CS_REVIEW AA, TBL_CS BB, TBL_USER CC
            WHERE
                AA.CS_IDX = BB.IDX
                AND CC.USER_STATUS != 3
                AND AA.USER_IDX = CC.IDX
                AND AA.SHOW_YN = 'Y'
            ORDER BY USER_REGIST_DATE DESC
            )
            
            UNION ALL
            
            (SELECT * FROM
                (SELECT
                    BB.IMG
                    , BB.NICK_NAME AS CS_NICK_NAME
                    , BB.CODE
                    , AA.USER_ID AS USER_NICK_NAME
                    , AA.IDX
                    , '' AS USER_IDX
                    , AA.CS_IDX
                    , AA.USER_CONT
                    , DATE_FORMAT(AA.USER_REGIST_DATE,'%Y.%m.%d') AS USER_REGIST_DATE
                    , NULL AS CHATLOG_IDX
                    , AA.CHAT_TIME
                FROM TBL_CS_REVIEW_DUMY AA, TBL_CS BB
                WHERE
                    AA.CS_IDX = BB.IDX
                    AND AA.REGIST_DATE <= NOW()
                ORDER BY USER_REGIST_DATE DESC) subquery
            )
            ) T1
            ORDER BY USER_REGIST_DATE DESC
            ";


        $stmt = $this->conn->prepare( $query );
        $stmt->execute();

        $row = $stmt->fetch(PDO::FETCH_ASSOC);

        return $row;
    }


    function read_keyword(){
/*        $query =

            "
            SELECT
                *
            FROM TBL_CS_SEARCH_KEYWORD
            ";*/

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
            LIMIT 10
            ";

        $stmt = $this->conn->prepare( $query );
        $stmt->execute();

        $list = [];
        while ($row = $stmt->fetch(PDO::FETCH_ASSOC)) {
            $list[] = $row;
        }

        return $list;
    }

    function read_quick(){
        $query =

            "
                SELECT 
                    IDX
                    , IMG
                    ,CASE 
                        WHEN TYPE = 1 THEN '타로'
                        WHEN TYPE = 2 THEN '신점'
                        WHEN TYPE = 3 THEN '역학'
                        WHEN TYPE = 4 THEN '사주'
                    END AS TYPE
                   ,CASE WHEN CS_DATE >= DATE_SUB(NOW(), INTERVAL 30 DAY) 
                         THEN '신규'
                         ELSE '기존'
                    END AS CHK_NEW
                   , NICK_NAME
                   , CODE
                   , AFTER_AMOUNT
                   , GRADE
                   , STATUS
                FROM TBL_CS WHERE
                    APPROVAL_YN = 'Y'         
                    AND SHOW_YN = 'Y'
                    AND (STATUS = 1 or STATUS = 2)
                    ORDER BY STATUS, RAND()
            ";

        $stmt = $this->conn->prepare( $query );
        $stmt->execute();

        $list = [];
        while ($row = $stmt->fetch(PDO::FETCH_ASSOC)) {
            $list[] = $row;
        }

        return $list;
    }


    function read_cs_by_type($obj){
        $query=
            "
            select
                *
            FROM 
            (	
                SELECT
                    AA.IDX
                    , AA.NICK_NAME
                    , AA.IMG
                    , AA.TYPE
                    , AA.CODE
                    , AA.GRADE
                    , AA.SHORT_INFO
                    , AA.GREETING
                    , AA.CAREER
                    , AA.NOTICE
                    , AA.WORK_TIME
                    , AA.AFTER_AMOUNT
                    , AA.STATUS
                    , IFNULL(COUNT_REAL.CNT,0) + IFNULL(COUNT_DUMY.CNT,0) AS TOTAL_REVIEW_CNT
                    , COUNT_BOOK.CNT AS BOOK_CNT
                FROM
                    TBL_CS AA
                LEFT JOIN (
                    SELECT
                        CS_IDX,
                        COUNT(*) AS CNT
                    FROM
                        TBL_CS_REVIEW WHERE SHOW_YN = 'Y'
                    GROUP BY
                        CS_IDX) COUNT_REAL ON AA.IDX = COUNT_REAL.CS_IDX
                LEFT JOIN (
                    SELECT
                        CS_IDX,
                        COUNT(*) AS CNT
                    FROM
                        TBL_CS_REVIEW_DUMY
                    WHERE
                        USER_REGIST_DATE <= NOW()
                    GROUP BY
                        CS_IDX) COUNT_DUMY ON AA.IDX = COUNT_DUMY.CS_IDX
                LEFT JOIN (
                    SELECT
                        CS_IDX,
                        COUNT(*) AS CNT
                    FROM
                        TBL_USER_BOOKMARK
                    GROUP BY
                        CS_IDX) COUNT_BOOK ON AA.IDX = COUNT_BOOK.CS_IDX
                WHERE
                    AA.APPROVAL_YN = 'Y'
                    AND AA.SHOW_YN = 'Y'
                    AND AA.TYPE = '".$obj->TYPE."'
            ";

        if($obj->STATUS!=''){
            $query.=  "  and AA.STATUS = $obj->STATUS ";
        }
        if($obj->CHK_NEW=='Y'){
            $query .= "  and AA.NEW_YN = 'Y' AND (AA.STATUS=1 OR AA.STATUS=3)";
        }
        $query.=  "  ORDER BY AA.STATUS, RAND() ";

        $query .= " ) T1 ";

        if ($obj->ORDER_TYPE=='review') {
            $query.=" ORDER BY TOTAL_REVIEW_CNT DESC";
        } else if($obj->ORDER_TYPE=='bookmark') {
            $query.=" ORDER BY BOOK_CNT DESC";
        } else if($obj->ORDER_TYPE=='point') {
            $query.=" ORDER BY AFTER_AMOUNT DESC";
        }

        $stmt = $this->conn->prepare( $query );
        $stmt->execute();

        $list = [];
        /*
        while ($row = $stmt->fetch(PDO::FETCH_ASSOC)) {
            $list[] = $row;
        }
        */
        while ($row = $stmt->fetch(PDO::FETCH_ASSOC)) {
            //$review_list = $this->read_main_review($row['IDX']);
            //$row['review_list'] = $review_list;
            $list[] = $row;
        }
        return $list;
    }


    function read_total_review(){
        $query =

            "
            SELECT
                BB.IMG
                , BB.NICK_NAME AS CS_NICK_NAME
                , BB.CODE
                , CC.NICK_NAME AS USER_NICK_NAME
                , AA.IDX
                , AA.USER_IDX
                , AA.CS_IDX
                , AA.USER_CONT
                , DATE_FORMAT(AA.USER_REGIST_DATE,'%Y.%m.%d') AS USER_REGIST_DATE
            FROM TBL_CS_REVIEW AA, TBL_CS BB, TBL_USER CC WHERE
                AA.CS_IDX = BB.IDX
                AND CC.USER_STATUS !=3                                            
                AND AA.USER_IDX = CC.IDX
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

    function getCsNickNameByCode($code){
        $query =

            "
            SELECT
                NICK_NAME
            FROM TBL_CS WHERE 
                CODE = '".$code."'
            ";

        $stmt = $this->conn->prepare( $query );
        $stmt->execute();

        $row = $stmt->fetch(PDO::FETCH_ASSOC);

        return $row['NICK_NAME'];
    }


    function addReview($obj){

        $cont = strip_tags($obj->USER_CONT);
        $cont = htmlentities($cont, ENT_QUOTES);

        // insert query
        $query =
            "
                INSERT INTO TBL_CS_REVIEW SET
                USER_IDX            = '".htmlspecialchars(strip_tags($obj->USER_IDX))."'
                , CS_IDX          = '".htmlspecialchars(strip_tags($obj->IDX))."'
                , CHATLOG_IDX       = '".htmlspecialchars(strip_tags($obj->CHAT_IDX))."'
                , USER_CONT              = '".$cont."'
                , USER_REGIST_DATE       = NOW()
            ";


        if($this->conn->prepare($query)->execute()){
            return true;
        }
        return false;
    }


    function read_review_by_useridx($user_idx,$month){
        $query =

            "
                SELECT
                    AA.IDX
                    , AA.USER_IDX
                    , AA.CS_IDX
                    , AA.CHATLOG_IDX
                    , BB.NICK_NAME
                    , BB.CODE
                    , BB.IMG
                    , CASE 
                        WHEN BB.TYPE = '1' THEN '타로'
                        WHEN BB.TYPE = '2' THEN '신점'
                        WHEN BB.TYPE = '3' THEN '역학'
                        WHEN BB.TYPE = '4' THEN '사주'
                     END AS TYPE
                     , CASE
                         WHEN AA.CS_CONT IS NULL OR AA.CS_CONT = '' THEN 'N'
                         ELSE 'Y' END IS_CHK
                     , DATE_FORMAT(USER_REGIST_DATE,'%Y.%m.%d') as USER_REGIST_DATE
                FROM TBL_CS_REVIEW AA, TBL_CS BB WHERE
                    AA.USER_IDX = ".$user_idx."
                    AND AA.CS_IDX = BB.IDX
                    AND AA.SHOW_YN = 'Y'
                    AND AA.USER_REGIST_DATE BETWEEN DATE_SUB(NOW(), INTERVAL ".$month." MONTH) AND NOW()

            ";



        $stmt = $this->conn->prepare( $query );
        $stmt->execute();

        $list = [];
        while ($row = $stmt->fetch(PDO::FETCH_ASSOC)) {
            $list[] = $row;
        }

        return $list;
    }

    function update_status($obj){


        $query =
            "
                UPDATE TBL_CS SET
                    STATUS = '".$obj->STATUS."'
                WHERE CODE = '".htmlspecialchars(strip_tags($obj->CODE))."'
            ";


        if($this->conn->prepare($query)->execute()){
            return true;
        }
        return false;
    }

    function getCsInfoByCode($code){
        $query =

            "
            SELECT
                *
            FROM TBL_CS WHERE
                CODE = '".$code."'
            ";


        $stmt = $this->conn->prepare( $query );
        $stmt->execute();

        $row = $stmt->fetch(PDO::FETCH_ASSOC);
        return $row;
    }

    function getReviewInfoChatIdx($idx){
        $query =

            "
            SELECT
                *
            FROM TBL_CS_REVIEW WHERE
                CHATLOG_IDX = '".$idx."'
                AND SHOW_YN = 'Y'
            ";


        $stmt = $this->conn->prepare( $query );
        $stmt->execute();

        $row = $stmt->fetch(PDO::FETCH_ASSOC);
        return $row;
    }

    function update_notice($obj){

        $notice = strip_tags($obj->NOTICE);
        $notice = htmlentities($notice, ENT_QUOTES);

        // insert query
        $query =
            "
                UPDATE TBL_CS SET
                    NOTICE          = '".$notice."'
                    , UPDATE_DATE     = NOW()
                where 
                    IDX = ".$obj->IDX."
            ";


        if($this->conn->prepare($query)->execute()){
            return true;
        }
        return false;
    }

    function update_work_time($obj){

        $worktime = strip_tags($obj->WORKTIME);
        $worktime = htmlentities($worktime, ENT_QUOTES);

        // insert query
        $query =
            "
                UPDATE TBL_CS SET
                    WORK_TIME          = '".$worktime."'
                    , UPDATE_DATE     = NOW()
                where 
                    IDX = ".$obj->IDX."
            ";


        echo $query;

        if($this->conn->prepare($query)->execute()){
            return true;
        }
        return false;
    }

    function update_greeting($obj){


        $greeting = strip_tags($obj->GREETING);
        $greeting = htmlentities($greeting, ENT_QUOTES);

        // insert query
        $query =
            "
                UPDATE TBL_CS SET
                    GREETING        = '".$greeting."'
                    , UPDATE_DATE     = NOW()
                where 
                    IDX = ".$obj->IDX."
            ";


        if($this->conn->prepare($query)->execute()){
            return true;
        }
        return false;
    }


    function read_cs_review_info($user_idx){
        /*
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
                    AA.CS_IDX = '".$user_idx."'
                    AND BB.USER_STATUS !=3
                    AND AA.USER_IDX = BB.IDX
                    AND AA.CS_IDX = CC.IDX
                    ORDER BY AA.USER_REGIST_DATE DESC
            ";
        */
        $query =
            "
               SELECT
                   IDX
                   , USER_NICK_NAME
                   , USER_CONT
                   , USER_REGIST_DATE AS REAL_USER_REGIST_DATE
                   , DATE_FORMAT(USER_REGIST_DATE,'%Y.%m.%d') AS USER_REGIST_DATE
                   , CS_NICK_NAME
                   , CODE
                   , CS_CONT  
                   , DATE_FORMAT(CS_REGIST_DATE,'%Y.%m.%d') AS CS_REGIST_DATE
                   , REVIEW_TYPE
               FROM (
               (SELECT
                    AA.IDX
                     
                   , BB.NICK_NAME AS USER_NICK_NAME
                   , AA.USER_CONT
                   , AA.USER_REGIST_DATE
                   
                   , CC.NICK_NAME AS CS_NICK_NAME
                   , CC.CODE
                   , AA.CS_CONT
                   , AA.CS_REGIST_DATE
                   , 'REAL' AS REVIEW_TYPE
               FROM TBL_CS_REVIEW AA, TBL_USER BB, TBL_CS CC
               WHERE
                    AA.CS_IDX = '".$user_idx."'
                    AND BB.USER_STATUS !=3
                    AND AA.USER_IDX = BB.IDX
                    AND AA.CS_IDX = CC.IDX
                    AND AA.SHOW_YN = 'Y'
                    ORDER BY AA.USER_REGIST_DATE DESC
               
               )
               
               UNION ALL
               
               (SELECT * FROM
                   (SELECT
                       AA.IDX
                       , AA.USER_ID AS USER_NICK_NAME
                       , AA.USER_CONT
                       , AA.USER_REGIST_DATE
                       , BB.NICK_NAME AS CS_NICK_NAME
                       , BB.CODE
                       , AA.CS_CONT
                       , AA.CS_REGIST_DATE
                       , 'DUMY' AS REVIEW_TYPE
                   FROM TBL_CS_REVIEW_DUMY AA, TBL_CS BB
                   WHERE
                        AA.CS_IDX = '".$user_idx."'
                        AND AA.CS_IDX = BB.IDX
                       AND AA.REGIST_DATE <= NOW()
                   ORDER BY USER_REGIST_DATE DESC) subquery
               )
               ) T1 
               ORDER BY REAL_USER_REGIST_DATE DESC
            ";

        $stmt = $this->conn->prepare( $query );
        $stmt->execute();

        $list = [];
        while ($row = $stmt->fetch(PDO::FETCH_ASSOC)) {
            $list[] = $row;
        }

        return $list;
    }


    function update_review_reply($obj){


        $reply = strip_tags($obj->REPLY);
        $reply = htmlentities($reply, ENT_QUOTES);

        // insert query
        $query =
            "
                UPDATE TBL_CS_REVIEW SET
                    CS_CONT        = '".$reply."'
                    , CS_REGIST_DATE     = NOW()
                where 
                    IDX = ".$obj->IDX."
            ";


        if($this->conn->prepare($query)->execute()){
            return true;
        }
        return false;
    }

    function update_review_dumy_reply($obj){


        $reply = strip_tags($obj->REPLY);
        $reply = htmlentities($reply, ENT_QUOTES);

        // insert query
        $query =
            "
                UPDATE TBL_CS_REVIEW_DUMY SET
                    CS_CONT        = '".$reply."'
                    , CS_REGIST_DATE     = NOW()
                where 
                    IDX = ".$obj->IDX."
            ";


        if($this->conn->prepare($query)->execute()){
            return true;
        }
        return false;
    }

    function read_cs_faq_info($user_idx){
        $query =

            "
                SELECT
                    AA.IDX
                     
                   , BB.NICK_NAME AS USER_NICK_NAME
                   , AA.USER_CONT
                   , DATE_FORMAT(AA.USER_REGIST_DATE,'%Y.%m.%d %H:%m') as USER_REGIST_DATE
                   
                   , CC.NICK_NAME AS CS_NICK_NAME
                   , CC.CODE
                   , AA.CS_CONT
                   , DATE_FORMAT(AA.CS_REGIST_DATE,'%Y.%m.%d %H:%m') as CS_REGIST_DATE
                   
                FROM TBL_CS_FAQ AA, TBL_USER BB, TBL_CS CC WHERE
                    AA.CS_IDX = '".$user_idx."'
                    AND BB.USER_STATUS !=3
                    AND AA.USER_IDX = BB.IDX
                    AND AA.CS_IDX = CC.IDX
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


    function update_faq_reply($obj){


        $reply = strip_tags($obj->REPLY);
        $reply = htmlentities($reply, ENT_QUOTES);

        // insert query
        $query =
            "
                UPDATE TBL_CS_FAQ SET
                    CS_CONT        = '".$reply."'
                    , CS_REGIST_DATE     = NOW()
                where 
                    IDX = ".$obj->IDX."
            ";


        if($this->conn->prepare($query)->execute()){
            return true;
        }
        return false;
    }

    function create_admin_faq($obj){


        $cont = strip_tags($obj->CONT);
        $cont = htmlentities($cont, ENT_QUOTES);


        // insert query
        $query =
            "
                INSERT INTO TBL_CS_ADMIN_FAQ SET
                CS_IDX            = '".htmlspecialchars(strip_tags($obj->CS_IDX))."'
                , CS_CONT              = '".$cont."'
                , CS_REGIST_DATE       = NOW()
    
            ";

        if($this->conn->prepare($query)->execute()){
            return true;
        }
        return false;
    }
    function read_admin_faq_info($user_idx){
        $query =

            "
                SELECT
                	 AA.IDX                
                    , BB.NICK_NAME AS CS_NICK_NAME
                    , (SELECT NICK_NAME FROM TBL_USER WHERE IDX = AA.ADMIN_IDX) AS ADMIN_NICK_NMAE
                    , BB.CODE
                    , AA.CS_CONT
                    , DATE_FORMAT(AA.CS_REGIST_DATE,'%Y.%m.%d') as CS_REGIST_DATE
                    , AA.ADMIN_CONT
                    , DATE_FORMAT(AA.ADMIN_REGIST_DATE,'%Y.%m.%d') as ADMIN_REGIST_DATE
                FROM TBL_CS_ADMIN_FAQ AA, TBL_CS BB WHERE
                    AA.CS_IDX = '".$user_idx."'
                    AND AA.CS_IDX = BB.IDX
                    ORDER BY AA.CS_REGIST_DATE DESC
            ";


        $stmt = $this->conn->prepare( $query );
        $stmt->execute();

        $list = [];
        while ($row = $stmt->fetch(PDO::FETCH_ASSOC)) {
            $list[] = $row;
        }

        return $list;
    }

    function read_notice_info(){
        $query =

            "
                SELECT
                	 IDX
                     , TITLE
                     , CONT
                    , DATE_FORMAT(REGIST_DATE,'%Y.%m.%d') as REGIST_DATE
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

    function read_notice_detail_info($idx){
        $query =

            "
                SELECT
                    cur.IDX,
                    cur.TITLE,
                    cur.CONT,
                    DATE_FORMAT(cur.REGIST_DATE, '%Y.%m.%d') as REGIST_DATE,
                    (
                        SELECT MAX(prev.IDX)
                        FROM TBL_CS_NOTICE prev
                        WHERE prev.IDX < cur.IDX
                    ) as PREV_IDX,
                    (
                        SELECT MIN(next.IDX)
                        FROM TBL_CS_NOTICE next
                        WHERE next.IDX > cur.IDX
                    ) as NEXT_IDX
                FROM TBL_CS_NOTICE cur WHERE
                    IDX = '".$idx."'                       
            ";


        $stmt = $this->conn->prepare( $query );
        $stmt->execute();

        $row = $stmt->fetch(PDO::FETCH_ASSOC);

        return $row;
    }

    function getCsList(){
        $query =

            "
               SELECT
                    *
                FROM TBL_CS WHERE
                    APPROVAL_YN='Y'
                    AND SHOW_YN='Y'
            ";


        $stmt = $this->conn->prepare( $query );
        $stmt->execute();

        $list = [];
        while ($row = $stmt->fetch(PDO::FETCH_ASSOC)) {
            $list[] = $row;
        }

        return $list;
    }

    function update_cs_status($idx, $status){


        $query =
            "
                UPDATE TBL_CS SET
                STATUS     = '".$status."'
                WHERE IDX = '".htmlspecialchars(strip_tags($idx))."'
            ";


        if($this->conn->prepare($query)->execute()){
            return true;
        }
        return false;
    }

    function read_cs_info_call($idx){
        $query =

            "
                SELECT
                    IDX
                    , NICK_NAME
                    , CASE 
                        WHEN TYPE = 1 THEN '타로'
                        WHEN TYPE = 2 THEN '신점'
                        WHEN TYPE = 3 THEN '역학'
                        WHEN TYPE = 4 THEN '사주'
                    END AS TYPE
                    , CODE
                    , IMG
                    , AFTER_AMOUNT
                    , BEFORE_AMOUNT
                    , GRADE
                FROM TBL_CS WHERE
                    IDX = '".$idx."'                       
            ";


        $stmt = $this->conn->prepare( $query );
        $stmt->execute();

        $row = $stmt->fetch(PDO::FETCH_ASSOC);

        return $row;
    }

    function insert_search_log($USER_CHK,$USER_IDX,$KEYWORD){


        // insert query
        $query =
            "
                INSERT INTO TBL_LOG_SEARCH SET
                USER_IDX            = '".$USER_IDX."'
                , USER_TYPE          = '".$USER_CHK."'
                , KEYWORD       = '".$KEYWORD."'
                , REGIST_DATE       = NOW()
            ";


        if($this->conn->prepare($query)->execute()){
            return true;
        }
        return false;
    }

    function read_admin_review_list(){
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
                    AND AA.SHOW_YN ='Y'
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

    function read_admin_dumy_user_list(){
        $query =

            "
                SELECT
                    *
                    , (SELECT COUNT(*) FROM TBL_CS_REVIEW_DUMY WHERE USER_ID = T1.USER_ID) AS CNT
                FROM (
                SELECT
                    DISTINCT(USER_ID)
                FROM TBL_CS_REVIEW_DUMY 
                ) T1
                ORDER BY CNT DESC
            ";


        $stmt = $this->conn->prepare( $query );
        $stmt->execute();

        $list = [];
        while ($row = $stmt->fetch(PDO::FETCH_ASSOC)) {
            $list[] = $row;
        }

        return $list;
    }

    function update_dumy_review($obj){


        $user_cont = strip_tags($obj->USER_CONT);
        $user_cont = htmlentities($user_cont, ENT_QUOTES);

        $cs_cont = strip_tags($obj->CS_CONT);
        $cs_cont = htmlentities($cs_cont, ENT_QUOTES);

        // insert query
        $query =
            "
                UPDATE TBL_CS_REVIEW_DUMY SET
                        USER_CONT		    = '".$user_cont."'
                        ,CS_IDX             = ".$obj->CS_IDX."
                        ,CS_CONT            = '".$cs_cont."'
                        ,REGIST_DATE        = '".$obj->REGIST_DATE."'
                        ,USER_REGIST_DATE   = '".$obj->REGIST_DATE."'
                        ,CHAT_TIME          = '".$obj->CHAT_TIME."'
                where 
                    IDX = ".$obj->IDX."
            ";


        if($this->conn->prepare($query)->execute()){
            return true;
        }
        return false;
    }

    function deleteBookMark($user_idx,$cs_idx){


        $query =
            "
                delete from TBL_USER_BOOKMARK where USER_IDX = '".$user_idx."' AND CS_IDX = '".$cs_idx."'
            ";


        if($this->conn->prepare($query)->execute()){
            return true;
        }
        return false;
    }

    function doBookMark($user_idx,$cs_idx){


        $query =
            "
                INSERT INTO TBL_USER_BOOKMARK SET
                USER_IDX      = ".$user_idx."
                , CS_IDX   = ".$cs_idx."
                , REGIST_DATE = NOW()
            ";

        if($this->conn->prepare($query)->execute()){
            return true;
        }
        return false;
    }
}
