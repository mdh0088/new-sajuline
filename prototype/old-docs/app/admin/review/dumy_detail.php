<?php
require_once($_SERVER['DOCUMENT_ROOT']."/app/admin/common/top.php");
include_once $_SERVER['DOCUMENT_ROOT'].'/api/config/database.php';
$database       = new Database();
$db = $database->getConnection();

if ($_GET['userid']==''){
    echo
    "
    <script>
        alert('잘못된 접근입니다.');
        location.href='/app/admin/dumy_user_list.php';
    </script>
    ";
}

$userid = $_GET['userid'];

$chk_query = "SELECT  count(*) as cnt FROM TBL_CS_REVIEW_DUMY WHERE  USER_ID = '".$userid."'";
$chk_stmt = $db->prepare( $chk_query );
$chk_stmt->execute();
$row = $chk_stmt->fetch(PDO::FETCH_ASSOC);
if($row['cnt'] < 1){
    echo
    "
    <script>
        alert('존재하지 않은 더미 유저입니다.');
        location.href='/app/admin/review/dumy_user_list';
    </script>
    ";
}


$query =
    "
        SELECT
            AA.IDX
            , AA.USER_ID
            , BB.CODE
            , BB.NICK_NAME
            , AA.USER_CONT
            , AA.USER_REGIST_DATE
            , AA.CS_IDX
            , AA.CS_CONT
            , AA.CS_REGIST_DATE
            , AA.REGIST_DATE
            , AA.CHAT_TIME
        FROM TBL_CS_REVIEW_DUMY AA, TBL_CS BB WHERE
            AA.CS_IDX = BB.IDX
            AND AA.USER_ID = '".$userid."'
            ORDER BY AA.REGIST_DATE 
        
";

$stmt = $db->prepare( $query );
$stmt->execute();





?>
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/flatpickr/dist/flatpickr.min.css">
<script src="https://cdn.jsdelivr.net/npm/flatpickr"></script>
<style>
    #modal {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: rgba(0, 0, 0, 0.5);
        z-index: 9999;
    }

    #modal-content {
        position: absolute;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        background: #fff;
        padding: 20px;
        border-radius: 5px;
        width: 80%;
        height: 80%;
        overflow: auto;
    }

</style>



<script>
    document.addEventListener('DOMContentLoaded', () => {
        flatpickr(".datePicker", {
            enableTime: true,
            dateFormat: "Y:m:d H:i:S"
        });

        flatpickr(".timePicker", {
            enableTime: true,
            dateFormat: "H:i:S"
        });
    })
    const update_dumy_review = (IDX) => {


        let csObj =
            {
                IDX             : IDX
                ,USER_CONT		: document.querySelector('#USER_CONT_'+IDX).value
                ,CS_IDX         : document.querySelector('#CS_IDX_'+IDX).value
                ,CS_CONT        : document.querySelector('#CS_CONT_'+IDX).value
                ,REGIST_DATE    : document.querySelector('#REGIST_DATE_'+IDX).value
                ,CHAT_TIME      : document.querySelector('#CHAT_TIME_'+IDX).value
            };

        try {
            let param = JSON.stringify(csObj);
            let data = new FormData();
            data.append("csObj", param);
            axios.post('/api/cs/update_dumy_review', data)
                .then((result) => {
                    console.log(result);
                    alert(result.data.message);
                    if (result.data.isSuc) {

                    } else {

                    }
                })
        } catch (err) {
            console.log("Error >>", err);
        }
    }


</script>

<!-- Page Wrapper -->
<div id="wrapper">
    <!-- Sidebar -->
    <?php
    require_once($_SERVER['DOCUMENT_ROOT']."/app/admin/common/navi.php");
    ?>
    <!-- End of Sidebar -->

    <!-- Content Wrapper -->
    <div id="content-wrapper" class="d-flex flex-column">

        <!-- Main Content -->
        <div id="content">
            <?php
            require_once($_SERVER['DOCUMENT_ROOT']."/app/admin/common/header.php");
            ?>

            <!-- Begin Page Content -->
            <div class="container-fluid">

                <!-- Page Heading -->
                <h1 class="h3 mb-2 text-gray-800">더미 상담사 리뷰</h1>

                <!-- Content Row -->
                <div class="row">
                    <div class="col-xl-8 col-lg-7">
                        <p>더미 유저 : <input type="text" id="USER_ID" value="<?php echo $userid ?>"></p>
                        <?php
                        while ($row = $stmt->fetch(PDO::FETCH_ASSOC)) {
                        ?>
                        <!-- Area Chart -->
                        <div class="card shadow mb-4">

                            <div class="card-header py-3">
                                <h6 class="m-0 font-weight-bold text-primary">상담사 정보</h6>
                            </div>

                            <div class="card-body">
                                <div class="row">
                                    <div class="col-md-12">
                                        <p>더미 유저 리뷰 :</p>
                                        <textarea id="USER_CONT_<?php echo $row['IDX']?>" style="width: 500px; height: 200px;"><?php echo str_replace('<br>', "\n", $row['USER_CONT']) ?></textarea>
                                    </div>
                                    <div class="col-md-6">
                                        <p>매칭 상담사 :
                                        <?php
                                        $str = '<select id="CS_IDX_'.$row['IDX'].'">';

                                        $cs_query = "SELECT   * FROM TBL_CS WHERE  APPROVAL_YN='Y' ORDER BY RECRUIT_DATE DESC ";
                                        $cs_stmt = $db->prepare($cs_query);
                                        $cs_stmt->execute();
                                        while ($cs_row = $cs_stmt->fetch(PDO::FETCH_ASSOC)) {
                                            $selected = "";
                                            if ($row['CS_IDX'] == $cs_row['IDX']) {
                                                $selected = "selected";
                                            }
                                            $str .= '<option value="' . $cs_row['IDX'] . '" ' . $selected . '>' . $cs_row['NICK_NAME'] . '</option>';
                                        }
                                        $str .= '</select>';
                                        echo $str;
                                        ?>
                                        </p>
                                    </div>
                                    <div class="col-md-12">
                                        <p>매칭 상담사 리뷰:</p>
                                        <textarea id="CS_CONT_<?php echo $row['IDX']?>" style="width: 500px; height: 100px;"><?php echo $row['CS_CONT'] ?></textarea>
                                    </div>
                                    <div class="col-md-12">
                                        <p>노출 시작 일시 : <input type="text" id="REGIST_DATE_<?php echo $row['IDX']?>" class="datePicker" value="<?php echo $row['REGIST_DATE'] ?>"></p>
                                    </div>
                                    <div class="col-md-12">
                                        <p>상담시간 : <input type="text" id="CHAT_TIME_<?php echo $row['IDX']?>" class="timePicker" value="<?php echo $row['CHAT_TIME'] ?>"> </p>
                                    </div>
                                </div>
                            </div>
                            <button type="button" class="btn btn-success" onclick="update_dumy_review(<?php echo $row['IDX'] ?>);">수정</button>
                        </div>

                            <?php
                        }
                        ?>

                    </div>
                </div>
            </div>
            <!-- /.container-fluid -->
        </div>
        <!-- End of Main Content -->

        <!-- Footer -->
        <?php
        require_once($_SERVER['DOCUMENT_ROOT']."/app/admin/common/footer.php");
        ?>
        <!-- End of Footer -->

    </div>
    <!-- End of Content Wrapper -->

</div>

</div>

<div id="modal" style="display: none;">
    <div id="modal-content">
        <input type="button" value="닫기" onclick="Javascript:document.getElementById('modal').style.display = 'none';">

        <input type="text" id="target_keyword" class="pop_keyword" onkeypress="if (event.keyCode == 13) add_keyword()" placeholder="키워드를 입력해주세요.">
        <input type="button" value="등록" class="pop_keyword" onclick="add_keyword()">

        <input type="text" id="PASSWORD" class="pop_password" placeholder="비밀번호를 입력해주세요.">
        <input type="button" value="수정" class="pop_password" onclick="save_pw()">
    </div>


</div>
<!-- End of Page Wrapper -->
<?php
require_once($_SERVER['DOCUMENT_ROOT']."/app/admin/common/bottom.php");
?>

