<?php

// 'user' object
class Order{



    // constructor
    public function __construct($db){
        $this->conn = $db;
    }

    // create new user record
    function create($obj){

        // insert query
        $query =
            "
                INSERT INTO TBL_USER_TRADE SET
                USER_ID             = '".htmlspecialchars(strip_tags($obj->user_id))."'
                , USER_NAME         = '".htmlspecialchars(strip_tags($obj->user_name))."'
                , ORDER_NO          = '".htmlspecialchars(strip_tags($obj->order_no))."'
                , SERVICE_NAME      = '".htmlspecialchars(strip_tags($obj->service_name))."'
                , PRODUCT_NAME      = '".htmlspecialchars(strip_tags($obj->product_name))."'
                , CUSTOM_PARAMETER  = '".htmlspecialchars(strip_tags($obj->custom_parameter))."'
                , TID               = '".htmlspecialchars(strip_tags($obj->tid))."'
                , CID               = '".htmlspecialchars(strip_tags($obj->cid))."'
                , AMOUNT            = '".htmlspecialchars(strip_tags($obj->amount))."'
                , PAY_INFO          = '".htmlspecialchars(strip_tags($obj->pay_info))."'
                , PGCODE            = '".htmlspecialchars(strip_tags($obj->pgcode))."'
                , DOMESTIC_FLAG     = '".htmlspecialchars(strip_tags($obj->domestic_flag))."'
                , BILLKEY           = '".htmlspecialchars(strip_tags($obj->billkey))."'
                , TRANSACTION_DATE  = '".htmlspecialchars(strip_tags($obj->transaction_date))."'
                , CARD_INFO         = '".htmlspecialchars(strip_tags($obj->card_info))."'
                , PAYHASH           = '".htmlspecialchars(strip_tags($obj->payhash))."'
                , INSTALL_MONTH     = '".htmlspecialchars(strip_tags($obj->install_month))."'
                , REGIST_DATE       = NOW()
            ";

        $query .=
            "
                ,ACCOUNT_NO             =
                ,ACCOUNT_NAME           =
                ,ACCOUNT_HOLDER         =
                ,BANK_CODE              =
                ,BANK_NAME              =
                ,EXPIRE_DATE            =
                ,EXPIRE_TIME            =
                ,ISSUE_TID              =
                ,CASH_RECEIPT_TYPE      =
                ,PAY_TYPE               =
            ";

        $query .=
            "
            ";




        if($this->conn->prepare($query)->execute()){
            return true;
        }
        return false;
    }

    function generateOrderNumber(){
        $timestamp = time();
        $orderNumber = 'ORD-' . date('YmdHis', $timestamp);

        $query =

            "
                SELECT 
                    count(*) as count 
                FROM TBL_USER_TRADE WHERE 
                    ORDER_NO = '".$orderNumber."'
            ";

        $stmt = $this->conn->prepare( $query );
        $stmt->execute();

        $row = $stmt->fetch(PDO::FETCH_ASSOC);

        if ($row['count'] > 0) {
            // 이미 사용 중인 주문번호이므로, 다시 생성
            return generateOrderNumber();
        }

        return $orderNumber;
    }


    function create_trade_log($obj){

        // insert query
        $query =
            "
                INSERT INTO TBL_USER_TRADE_LOG SET
                AMOUNT                    = '".htmlspecialchars(strip_tags($obj->amount))."'
                , BILLKEY                 = '".htmlspecialchars(strip_tags($obj->billkey))."'
                , CARD_CODE               = '".htmlspecialchars(strip_tags($obj->card_code))."'
                , CARD_INFO               = '".htmlspecialchars(strip_tags($obj->card_info))."'
                , CID                     = '".htmlspecialchars(strip_tags($obj->cid))."'
                , USER_IDX                = '".htmlspecialchars(strip_tags($obj->custom_parameter))."'
                , DISCOUNT_AMOUNT         = '".htmlspecialchars(strip_tags($obj->discount_amount))."'
                , DISPOSABLE_CUP_DEPOSIT  = '".htmlspecialchars(strip_tags($obj->disposable_cup_deposit))."'
                , DOMESTIC_FLAG           = '".htmlspecialchars(strip_tags($obj->domestic_flag))."'
                , INSTALL_MONTH           = '".htmlspecialchars(strip_tags($obj->install_month))."'
                , NONSETTLE_AMOUNT        = '".htmlspecialchars(strip_tags($obj->nonsettle_amount))."'
                , ORDER_NO                = '".htmlspecialchars(strip_tags($obj->order_no))."'
                , PAY_INFO                = '".htmlspecialchars(strip_tags($obj->pay_info))."'
                , PAYHASH                 = '".htmlspecialchars(strip_tags($obj->payhash))."'
                , PGCODE                  = '".htmlspecialchars(strip_tags($obj->pgcode))."'
                , POINTUSE_FLAG           = '".htmlspecialchars(strip_tags($obj->pointuse_flag))."'
                , PRODUCT_NAME            = '".htmlspecialchars(strip_tags($obj->product_name))."'
                , SERVICE_NAME            = '".htmlspecialchars(strip_tags($obj->service_name))."'
                , TAX_AMOUNT              = '".htmlspecialchars(strip_tags($obj->tax_amount))."'
                , TAXFREE_AMOUNT          = '".htmlspecialchars(strip_tags($obj->taxfree_amount))."'
                , TID                     = '".htmlspecialchars(strip_tags($obj->tid))."'
                , TRANSACTION_DATE        = '".htmlspecialchars(strip_tags($obj->transaction_date))."'
                , USER_ID                 = '".htmlspecialchars(strip_tags($obj->user_id))."'
                , USER_NAME               = '".htmlspecialchars(strip_tags($obj->user_name))."'
                , REGIST_DATE             = NOW()
            ";

        if($this->conn->prepare($query)->execute()){
            return true;
        }
        return false;
    }


    function create_trade_card($obj){

        // insert query
        $query =
            "
                INSERT INTO TBL_USER_TRADE SET
                CODE                        = '".htmlspecialchars(strip_tags($obj->code))."'
                , MESSAGE                   = '".htmlspecialchars(strip_tags($obj->message))."'
                , USER_ID                   = '".htmlspecialchars(strip_tags($obj->user_id))."'
                , USER_NAME                 = '".htmlspecialchars(strip_tags($obj->user_name))."'
                , ORDER_NO                  = '".htmlspecialchars(strip_tags($obj->order_no))."'
                , SERVICE_NAME              = '".htmlspecialchars(strip_tags($obj->service_name))."'
                , PRODUCT_NAME              = '".htmlspecialchars(strip_tags($obj->product_name))."'
                , USER_IDX                  = '".htmlspecialchars(strip_tags($obj->custom_parameter))."'
                , PGCODE                    = '".htmlspecialchars(strip_tags($obj->pgcode))."'
                
                , TID                       = '".htmlspecialchars(strip_tags($obj->tid))."'
                , CID                       = '".htmlspecialchars(strip_tags($obj->cid))."'
                , AMOUNT                    = '".htmlspecialchars(strip_tags($obj->amount))."'
                , PAY_INFO                  = '".htmlspecialchars(strip_tags($obj->pay_info))."'
                , DOMESTIC_FLAG             = '".htmlspecialchars(strip_tags($obj->domestic_flag))."'
                , INSTALL_MONTH             = '".htmlspecialchars(strip_tags($obj->install_month))."'
                , PAYHASH                   = '".htmlspecialchars(strip_tags($obj->payhash))."'
                , TAXFREE_AMOUNT            = '".htmlspecialchars(strip_tags($obj->taxfree_amount))."'
                , TAX_AMOUNT                = '".htmlspecialchars(strip_tags($obj->tax_amount))."'
                , NONSETTLE_AMOUNT          = '".htmlspecialchars(strip_tags($obj->nonsettle_amount))."'
                , DISCOUNT_AMOUNT           = '".htmlspecialchars(strip_tags($obj->discount_amount))."'
                , POINTUSE_FLAG             = '".htmlspecialchars(strip_tags($obj->pointuse_flag))."'
                , DISPOSABLE_CUP_DEPOSIT    = '".htmlspecialchars(strip_tags($obj->disposable_cup_deposit))."'
                , TRANSACTION_DATE          = '".htmlspecialchars(strip_tags($obj->transaction_date))."'
                , REGIST_DATE               = NOW()
                , PAY_TYPE                  = '".htmlspecialchars(strip_tags($obj->pay_type))."'
                
            ";

        if($this->conn->prepare($query)->execute()){
            return true;
        }
        return false;
    }

    function create_trade_virtual($obj){

        // insert query
        $query =
            "
                INSERT INTO TBL_USER_TRADE SET
                CODE                        = '".htmlspecialchars(strip_tags($obj->code))."'
                , MESSAGE                   = '".htmlspecialchars(strip_tags($obj->message))."'
                , USER_ID                   = '".htmlspecialchars(strip_tags($obj->user_id))."'
                , USER_NAME                 = '".htmlspecialchars(strip_tags($obj->user_name))."'
                , ORDER_NO                  = '".htmlspecialchars(strip_tags($obj->order_no))."'
                , SERVICE_NAME              = '".htmlspecialchars(strip_tags($obj->service_name))."'
                , PRODUCT_NAME              = '".htmlspecialchars(strip_tags($obj->product_name))."'
                , USER_IDX                  = '".htmlspecialchars(strip_tags($obj->custom_parameter))."'
                , PGCODE                    = '".htmlspecialchars(strip_tags($obj->pgcode))."'
                
                , ACCOUNT_NO                = '".htmlspecialchars(strip_tags($obj->account_no))."'
                , ACCOUNT_NAME              = '".htmlspecialchars(strip_tags($obj->account_name))."'
                , ACCOUNT_HOLDER            = '".htmlspecialchars(strip_tags($obj->account_holder))."'
                , BANK_CODE                 = '".htmlspecialchars(strip_tags($obj->bank_code))."'
                , BANK_NAME                 = '".htmlspecialchars(strip_tags($obj->bank_name))."'
                , EXPIRE_DATE               = '".htmlspecialchars(strip_tags($obj->expire_date))."'
                , EXPIRE_TIME               = '".htmlspecialchars(strip_tags($obj->expire_time))."'
                , ISSUE_TID                 = '".htmlspecialchars(strip_tags($obj->issue_tid))."'
                , CASH_RECEIPT_TYPE         = '".htmlspecialchars(strip_tags($obj->cash_receipt_type))."'
                , REGIST_DATE               = NOW()
                , PAY_TYPE                  = 'HOLD'
                
            ";

        if($this->conn->prepare($query)->execute()){
            return true;
        }
        return false;
    }


    function read_order_hold($user_idx){
        $query =

            "
            SELECT
                ORDER_NO
                , DATE_FORMAT(REGIST_DATE,'%Y%m%d') as REGIST_DATE
            FROM TBL_USER_TRADE WHERE 
                PAY_TYPE = 'HOLD'
                AND USER_IDX = '".$user_idx."'
            ";

        $stmt = $this->conn->prepare( $query );
        $stmt->execute();

        $list = [];
        while ($row = $stmt->fetch(PDO::FETCH_ASSOC)) {
            $list[] = $row;
        }
        return $list;
    }

    function read_order_hold_by_orderno($order_no){
        $query =

            "
            SELECT
                ORDER_NO
                , DATE_FORMAT(REGIST_DATE,'%Y%m%d') as REGIST_DATE
            FROM TBL_USER_TRADE WHERE 
                PAY_TYPE = 'HOLD'
                AND ORDER_NO = '".$order_no."'
            ";

        $stmt = $this->conn->prepare( $query );
        $stmt->execute();

        $list = [];
        while ($row = $stmt->fetch(PDO::FETCH_ASSOC)) {
            $list[] = $row;
        }

        return $list;
    }

    function update_order_paytype($order_no,$pattype,$amount){


        $query =
            "
                UPDATE TBL_USER_TRADE SET
                 PAY_TYPE  = '".$pattype."'
                , AMOUNT = $amount
                , UPDATE_DATE = NOW()
                , TRANSACTION_DATE= NOW()
                WHERE 
                    ORDER_NO = '".$order_no."'
            ";

        if($this->conn->prepare($query)->execute()){
            return true;
        }
        return false;
    }

    function read(){
        $query =

            "
            SELECT
                AA.IDX,
                BB.NICK_NAME,
                BB.USER_ID,
                BB.EMAIL,
                AA.ORDER_NO,
                CASE
                    WHEN AA.PAY_TYPE = 'SUCCESS' THEN '성공'
                    WHEN AA.PAY_TYPE = 'FAIL' THEN '실패'
                    WHEN AA.PAY_TYPE = 'HOLD' THEN '대기'
                    WHEN AA.PAY_TYPE = 'CANCEL' THEN '취소'
                END AS PAY_TYPE,
                AA.MESSAGE,
                CASE
                    WHEN AA.PGCODE = 'kakaopay' THEN '카카오'
                    WHEN AA.PGCODE = 'creditcard' THEN '신용카드'
                    WHEN AA.PGCODE = 'virtualaccount' THEN '무통장'
                END AS PGCODE,
                AA.REGIST_DATE,
                AA.UPDATE_DATE,
                AA.PRODUCT_NAME,
                AA.AMOUNT
            FROM TBL_USER_TRADE AA, TBL_USER BB WHERE
                AA.USER_IDX = BB.IDX
                ORDER BY AA.REGIST_DATE DESC
            ";

        $stmt = $this->conn->prepare( $query );
        $stmt->execute();

        $list = [];
        while ($row = $stmt->fetch(PDO::FETCH_ASSOC)) {
            $list[] = $row;
        }
        return $list;
    }

    function read_trade_idx($idx){
        $query =

            "
            SELECT
                *
            FROM TBL_USER_TRADE WHERE
                IDX = '".$idx."'
            ";

        $stmt = $this->conn->prepare( $query );
        $stmt->execute();


        $row = $stmt->fetch(PDO::FETCH_ASSOC);
        return $row;
    }

    function update_cancel_info($cancel_tid,$cancel_amount,$cancel_date){


        $query =
            "
                UPDATE TBL_USER_TRADE SET
                 PAY_TYPE  = 'CANCEL'
                , CANCEL_DATE = '".$cancel_date."'
                , CANCEL_AMOUNT = '".$cancel_amount."'
                WHERE 
                    TID = '".$cancel_tid."'
            ";

        if($this->conn->prepare($query)->execute()){
            return true;
        }
        return false;
    }

    function read_charge_event(){
        $query =

            "
            SELECT
                *
            FROM TBL_EVENT WHERE
                IDX = 2
            ";

        $stmt = $this->conn->prepare( $query );
        $stmt->execute();


        $row = $stmt->fetch(PDO::FETCH_ASSOC);
        return $row;
    }
}
