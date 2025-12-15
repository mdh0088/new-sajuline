<?php
require_once($_SERVER['DOCUMENT_ROOT']."/app/admin/common/top.php");
include_once $_SERVER['DOCUMENT_ROOT'].'/api/config/database.php';
$database       = new Database();
$db = $database->getConnection();

$cs_query =
"
    SELECT
        *
    FROM TBL_CS WHERE 
        APPROVAL_YN='Y'
    ORDER BY RECRUIT_DATE DESC
";

$cs_stmt = $db->prepare( $cs_query );
$cs_stmt->execute();

$use_query =
    "
    SELECT
        *
    FROM TBL_USER WHERE 
        LEFT(USER_ID,'4') ='dumy'
";

$user_stmt = $db->prepare( $use_query );
$user_stmt->execute();



?>

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

    const upload_dumpy_review = () => {

        if(isNull(document.querySelector("#PASSWORD").value)){
            alert('비밀번호를 입력해주세요.');
            document.querySelector("#pw").focus();
            return;
        }

        let csObj =
            {
                IDX		  : "<?php// echo $cs_idx ?>"
                ,PASSWORD  : document.querySelector('#PASSWORD').value
            };

        try {
            let param = JSON.stringify(csObj);
            let data = new FormData();
            data.append("csObj", param);
            axios.post('/api/cs/update_pw', data)
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
                <h1 class="h3 mb-2 text-gray-800">상담사</h1>
                <p class="mb-4">설명
                    <a target="_blank" href="https://www.chartjs.org/docs/latest/">
                        official Chart.js documentation
                    </a>.</p>

                <!-- Content Row -->
                <div class="row">
                    <div class="col-xl-8 col-lg-7">
                        <!-- Area Chart -->
                        <div class="card shadow mb-4">

                            <div class="card-header py-3">
                                <h6 class="m-0 font-weight-bold text-primary">상담사 정보</h6>
                            </div>

                            <div class="card-body">
                                <p>유저 : <input type="text" id="USER_ID"></p>
                                <p>유저 리뷰 : <textarea id="USER_CONT" style="width: 500px; height: 200px"></textarea> </p>
                                <p>상담사 :
                                    <?php
                                    $str = '<select id="CS_IDX">';
                                    while ($row = $cs_stmt->fetch(PDO::FETCH_ASSOC)) {
                                        $str .= '<option value="'.$row['IDX'].'">'.$row['NICK_NAME'].'</option>';
                                    }
                                    $str .= '</select>';
                                    echo $str;
                                    ?>
                                </p>
                                <p>상담사 리뷰 : <textarea id="CS_CONT" style="width: 500px; height: 200px"></textarea> </p>
                                <hr>
                            </div>
                            <input type="button" value="등록">
                        </div>
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

