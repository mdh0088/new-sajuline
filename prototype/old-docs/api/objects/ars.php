<?php
include_once $_SERVER['DOCUMENT_ROOT'].'/api/config/ars_database.php';
// 'user' object
class ARS{

    // constructor
    public function __construct($db){
        $this->conn = $db;
    }

    function read(){
        $query =

            "
            SELECT
                *
            FROM tm60_member
            ";

        $result = mssql_query($query, $this->conn);

        $list = [];
        while ($row = mssql_fetch_assoc($result)) {
            $list[] = $row;
        }
        return $list;
    }

    // 1개 리턴용
    function create_cs($obj){
        $query =

            "
                insert into tm60_member
                (
                    m_code, m_name, m_nickname, m_tel, m_tel1, m_tel2,
                    m_mobile, m_id, m_bunho, m_prate, m_fdate
                )
                values
                (
                    '".$obj['m_code']."', '".$obj['m_name']."', '".$obj['m_nickname']."', '".$obj['m_tel']."', '".$obj['m_tel1']."', '".$obj['m_tel2']."',
                    '".$obj['m_mobile']."', '".$obj['m_id']."', '1', ".$obj['m_prate'].", getdate()
                )
            ";

        $result = mssql_query($query, $this->conn);

        return $result;
    }

    function update_cs($obj){
        $query =

            "
                update tm60_member set
                    m_code          =   '".$obj['m_code']."'
                    ,m_name          =   '".$obj['m_name']."'
                    ,m_nickname     =   '".$obj['m_nickname']."'
                    ,m_prate         =   '".$obj['m_prate']."'
                    ,m_state         =   '".$obj['m_state']."'
                    ,m_bunho        =    '".$obj['m_bunho']."' 
                 where 
                     m_tel           =   '".$obj['m_tel']."'
                     
            ";

        $result = mssql_query($query, $this->conn);

        return $result;
    }


    function create_cs_log($obj){
        $query =

            "
                DECLARE @predate datetime;
                
                SELECT @predate = ISNULL(MAX(predate), GETDATE())
                FROM tm60_memberlog
                WHERE m_code = '".$obj['m_code']."';
                
                insert into tm60_memberlog
                (
                    m_code, m_name, m_nickname, m_absent, 
                    predate, regdate
                )
                values
                (
                    '".$obj['m_code']."','".$obj['m_name']."','".$obj['m_nickname']."','".$obj['m_state']."',
                    @predate, getdate()
                )
            ";

        $result = mssql_query($query, $this->conn);

        return $result;
    }

    function create_user($obj){
        $query =

            "
                insert into tm60_users
                (
                    u_id, u_tel, u_kname, u_fdate
                )
                values
                (
                    '".$obj['u_id']."', '".$obj['u_tel']."', '".$obj['u_kname']."',  getdate()
                )
            ";

        $result = mssql_query($query, $this->conn);

        return $result;
    }

    function charge_point($obj){
        $query =

            "
            UPDATE tm60_users	SET
                u_point = u_point + ".$obj['u_point']."
            WHERE 
                u_id = '".$obj['u_id']."'                
            ";


        $result = mssql_query($query, $this->conn);

        return $result;
    }

    function getUserInfo($obj){
        $query =

            "
            SELECT
                *
            FROM tm60_users where
                u_id = '".$obj['USER_ID']."'
                AND u_tel = '".$obj['PHONE']."'
            ";


        $result = mssql_query($query, $this->conn);

        $row = mssql_fetch_assoc($result);
        return $row;
    }

    function getUserInfoById($user_id){
        $query =

            "
            SELECT
                *
            FROM tm60_users where
                u_id = '".$user_id."'
            ";

        $result = mssql_query($query, $this->conn);

        $row = mssql_fetch_assoc($result);
        return $row;
    }

    function update_user($obj){
        $query =

            "
                update tm60_users set
                    u_kname          =   '".$obj['u_kname']."'
                 where 
                     u_id           =   '".$obj['u_id']."'
                     
            ";

        $result = mssql_query($query, $this->conn);

        return $result;
    }

    function update_point_by_cancel($user_id,$chk_point){
        $query =

            "
                update tm60_users set
                    u_point          =   '".$chk_point."'
                 where 
                     u_id           =   '".$user_id."'
                     
            ";

        $result = mssql_query($query, $this->conn);

        return $result;
    }

    function getChatlogById($user_id,$code){
        $query =

            "
                SELECT
                    idx
                    , m_code
                    , yyyy
                    , mm
                    , dd
                FROM tm60_chatlog WHERE
                   u_id = '".$user_id."'
                   and m_code ='".$code."'
                   AND fname =''
                   AND call_name !='waiting' 
                   order by chatstart desc
            ";


        $result = mssql_query($query, $this->conn);

        $list = [];
        while ($row = mssql_fetch_assoc($result)) {
            $list[] = $row;
        }
        return $list;
    }

    function update_chatlog_for_review($idx){
        $query =

            "
                update tm60_chatlog set
                    fname          =   'TRUE'
                 where 
                     idx           =   '".$idx."'
                     
            ";


        $result = mssql_query($query, $this->conn);

        return $result;
    }

    function getChatlogByIdForUser($user_id,$month){
        $query =

            "
                SELECT
                    idx
                    , m_code
                    , yyyy + '.' + mm + '.' + dd AS chat_day
                    , ISNULL(CONVERT(VARCHAR, DATEADD(SECOND, DATEDIFF(SECOND, chatstart, chatend), '00:00:00'), 108), '00:00:00') AS chat_time
                    , usepoint
                    , fname
                    , CASE WHEN fdnis = '62090808' THEN '1'
                      ELSE '2' END AS chat_type
                FROM tm60_chatlog WHERE
                   u_id = '".$user_id."'
                   AND chatstart BETWEEN DATEADD(MONTH, -".$month.", GETDATE()) AND GETDATE()
                   order by chatstart desc
            ";
        $result = mssql_query($query, $this->conn);

        $list = [];
        while ($row = mssql_fetch_assoc($result)) {
            $list[] = $row;
        }
        return $list;
    }

    function getChatLogForReview($chat_idx){
        $query =

            "
            SELECT
               yyyy + '.' + mm + '.' + dd AS chat_day
               , ISNULL(CONVERT(VARCHAR, DATEADD(SECOND, DATEDIFF(SECOND, chatstart, chatend), '00:00:00'), 108), '00:00:00') AS chat_time
               , usepoint
               , CASE WHEN fdnis = '62090808' THEN '1'
                  ELSE '2' END AS chat_type
            FROM tm60_chatlog WHERE
               idx = ".$chat_idx."
            ";


        $result = mssql_query($query, $this->conn);

        $row = mssql_fetch_assoc($result);
        return $row;
    }


    function getChatTimeByCode($code){
/*        $query =

            "
                SELECT
                    *
                FROM 
                (
                
                SELECT
                    ISNULL(CONVERT(VARCHAR, DATEADD(SECOND, SUM(CASE WHEN fdnis = '62090808' THEN DATEDIFF(SECOND, chatstart, chatend) ELSE 0 END), '00:00:00'), 108), '00:00:00') AS total_point_time_last_month
                    ,ISNULL(CONVERT(VARCHAR, DATEADD(SECOND, SUM(CASE WHEN fdnis <> '62090808' THEN DATEDIFF(SECOND, chatstart, chatend) ELSE 0 END), '00:00:00'), 108), '00:00:00') AS total_postpay_time_last_month    
                FROM
                    tm60_chatlog
                WHERE
                    m_code = ".$code."
                    AND chatstart >= DATEADD(MONTH, DATEDIFF(MONTH, 0, GETDATE()) - 1, 0)
                    AND chatend <= DATEADD(MONTH, DATEDIFF(MONTH, 0, GETDATE()), 0) - 1
                
                    
                ) T1,
                (
                SELECT
                    ISNULL(CONVERT(VARCHAR, DATEADD(SECOND, SUM(CASE WHEN fdnis = '62090808' THEN DATEDIFF(SECOND, chatstart, chatend) ELSE 0 END), '00:00:00'), 108), '00:00:00') AS total_point_time_this_month
                    ,ISNULL(CONVERT(VARCHAR, DATEADD(SECOND, SUM(CASE WHEN fdnis <> '62090808' THEN DATEDIFF(SECOND, chatstart, chatend) ELSE 0 END), '00:00:00'), 108), '00:00:00') AS total_postpay_time_this_month
                
                FROM
                    tm60_chatlog
                WHERE
                    m_code = ".$code."
                    AND chatstart >= DATEADD(MONTH, DATEDIFF(MONTH, 0, GETDATE()), 0)
                    AND chatend <= DATEADD(MONTH, DATEDIFF(MONTH, 0, GETDATE()) + 1, 0) - 1
                )T2
            ";*/

        $query=
            "
            SELECT
                /*ISNULL(CONVERT(VARCHAR, DATEADD(SECOND, SUM(DATEDIFF(SECOND, chatstart, chatend)), '00:00:00'), 108), '00:00:00') AS total_time_this_month*/
                /*ISNULL(CONVERT(VARCHAR, DATEADD(SECOND, SUM(chattm), '00:00:00'), 108), '00:00:00') AS total_time_this_month*/
              CAST(FLOOR(SUM(chattm) / 3600) AS VARCHAR(10)) + ':' +
                RIGHT('0' + CAST((SUM(chattm) % 3600) / 60 AS VARCHAR(2)), 2) + ':' +
                RIGHT('0' + CAST(SUM(chattm) % 60 AS VARCHAR(2)), 2) AS total_time_this_month
            FROM
                tm60_chatlog
            WHERE
                m_code = ".$code."
                AND chatstart >= DATEADD(MONTH, DATEDIFF(MONTH, 0, GETDATE()), 0)
                AND chatend <= DATEADD(SECOND, -1, DATEADD(DAY, 1, DATEADD(MONTH, DATEDIFF(MONTH, 0, GETDATE()) +1 , 0) -1 ));
            ";

        $result = mssql_query($query, $this->conn);

        $row = mssql_fetch_assoc($result);
        return $row;
    }

    function update_status_by_code($obj){
        $query =

            "
                update tm60_member set
                    m_state          =   '".$obj->STATUS."'
                 where 
                     m_code           =   '".$obj->CODE."'
                     
            ";

        $result = mssql_query($query, $this->conn);

        return $result;
    }

    function getCsStatus($code){
        $query =

            "
            SELECT
               m_state
            FROM tm60_member WHERE
               m_code = ".$code."
            ";

        $result = mssql_query($query, $this->conn);

        $row = mssql_fetch_assoc($result);
        return $row['m_state'];
    }

    function update_mobile($obj){
        $query =

            "
                insert into tm60_mobile
                (
                    mb_id, mb_code, mb_platform, regdate
                )
                values
                (
                    '".$obj->ID."', '".$obj->CODE."', '".$obj->TYPE."', getdate()
                )
            ";

        $result = mssql_query($query, $this->conn);

        return $result;
    }

    function admin_update_user_point($obj){
        $query =

            "
            UPDATE tm60_users	SET
                u_point = ".$obj['u_point']."
            WHERE 
                u_id = '".$obj['u_id']."'                
            ";


        $result = mssql_query($query, $this->conn);

        return $result;
    }

    function getChatlogByChatIdx($idx){
        $query =

            "
                SELECT
                    idx
                    , m_code
                    , yyyy + '.' + mm + '.' + dd AS chat_day
                    , ISNULL(CONVERT(VARCHAR, DATEADD(SECOND, DATEDIFF(SECOND, chatstart, chatend), '00:00:00'), 108), '00:00:00') AS chat_time
                    , usepoint
                    , fname
                    , CASE WHEN fdnis = '62090808' THEN '1'
                      ELSE '2' END AS chat_type
                FROM tm60_chatlog WHERE
                   idx = '".trim($idx)."'
                   order by chatstart desc
            ";


        $result = mssql_query($query, $this->conn);

        $row = mssql_fetch_assoc($result);
        return $row;
    }

    function delete_user($phone){
        $query =

            "
            DELETE FROM tm60_users WHERE 
                u_tel = '".$phone."'                
            ";


        $result = mssql_query($query, $this->conn);

        return $result;
    }

    function new_user_point($phone,$point){
        $query =

            "
            UPDATE tm60_users	SET
                u_point = u_point + ".$point."
            WHERE 
                u_tel = '".$phone."'                
            ";


        $result = mssql_query($query, $this->conn);

        return $result;
    }

}
