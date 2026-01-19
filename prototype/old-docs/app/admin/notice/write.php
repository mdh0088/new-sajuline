<?php
require_once($_SERVER['DOCUMENT_ROOT']."/app/admin/common/top.php");
include_once $_SERVER['DOCUMENT_ROOT'].'/api/config/database.php';
$notice_idx = '';

$database       = new Database();
$db = $database->getConnection();

$title = "";
$cont = "";

if(isset($_GET['idx'])){
    $notice_idx = $_GET['idx'];


    $query = "SELECT  * FROM TBL_CS_NOTICE WHERE  IDX = '".$notice_idx."'";
    $stmt = $db->prepare( $query );
    $stmt->execute();
    $row = $stmt->fetch(PDO::FETCH_ASSOC);

    $title = $row['TITLE'];
    $cont = $row['CONT'];
}
?>

<script>
    const save_notice = () => {

        let noticeObj =
            {
                IDX : '<?php echo $notice_idx ?>',
                TITLE : document.querySelector('#title').value,
                CONT  : document.querySelector('#cont').value
            };

        try {
            let param = JSON.stringify(noticeObj);
            let data = new FormData();
            data.append("noticeObj", param);
            axios.post('/api/admin/notice/save_notice', data)
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
                <h1 class="h3 mb-2 text-gray-800">관리자 공지 등록</h1>


                <!-- Content Row -->
                <div class="row">
                    <div class="col-xl-8 col-lg-7">
                        <!-- Area Chart -->
                        <div class="card shadow mb-4">

                            <div class="card-header py-3">
                                <h6 class="m-0 font-weight-bold text-primary">관리자 공지 등록</h6>
                            </div>

                            <div class="card-body">
                                <p>제목 : <input type="text" id="title" name="title" style="width: 500px" value = "<?php echo $title ?>"></p>
                                <p>내용 : <textarea id="cont" name="cont" style="width: 500px; height: 500px"><?php echo $cont ?></textarea></p>
                            </div>
                            <input type="button" value="저장" onclick="save_notice();">
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

<!-- End of Page Wrapper -->
<?php
require_once($_SERVER['DOCUMENT_ROOT']."/app/admin/common/bottom.php");
?>

