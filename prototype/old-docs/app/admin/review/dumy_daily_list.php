<?php
require_once($_SERVER['DOCUMENT_ROOT']."/app/admin/common/top.php");
include_once $_SERVER['DOCUMENT_ROOT'].'/api/config/database.php';

$database       = new Database();
$db = $database->getConnection();

$query =
    "
    SELECT
        t1.daily_list
        , (SELECT COUNT(*) FROM TBL_CS_REVIEW_DUMY WHERE DATE_FORMAT(REGIST_DATE,'%Y-%m-%d')  = t1.daily_list )  AS CNT
    FROM (
        SELECT
            DISTINCT(DATE_FORMAT(REGIST_DATE,'%Y-%m-%d')) as daily_list
        FROM TBL_CS_REVIEW_DUMY
    ) t1
            
";

$stmt = $db->prepare( $query );
$stmt->execute();
?>

<script>


    document.addEventListener('DOMContentLoaded', () => {
        //getReviewList();
    })



    const getReviewList = () => {
        let csObj =
            {

            };

        try {
            let param = JSON.stringify(csObj);
            let data = new FormData();
            data.append("csObj", param);
            axios.post('/api/cs/read_admin_dumy_user_list', data)
                .then((result) => {
                    console.log(result);
                    if (result.data.isSuc) {
                        let inner = "";
                        let cnt= 0;
                        result.data.list.forEach(item => {
                            cnt++;
                            inner += '<tr>';
                            inner += ' <td> '+item.USER_ID+'   <input type="text" id="USER_ID_'+cnt+'" value="'+item.USER_ID+'"> <button class="btn btn-primary" type="button" onclick="update_dumy_user_id(\''+item.USER_ID+'\','+cnt+');">수정</button></td>';
                            inner += ' <td onclick=Javascript:location.href="/app/admin/review/dumy_detail?userid='+item.USER_ID+'">' + item.CNT + '</td>';
                            inner += "</tr>";
                        });

                        document.querySelector('#listArea').insertAdjacentHTML("beforeend", inner);
                        $('#dataTable').DataTable();
                    } else {
                    }
                })
        } catch (err) {
            console.log("Error >>", err);
        }
    }


    const update_dumy_user_id = (userid,cnt) => {


        let csObj =
            {
                USER_ID		  : userid
                ,UPDATE_USER_ID  : document.querySelector('#USER_ID_'+cnt).value
            };


        try {
            let param = JSON.stringify(csObj);
            let data = new FormData();
            data.append("csObj", param);
            axios.post('/api/admin/update_dumy_user_id', data)
                .then((result) => {
                    console.log(result);
                    alert(result.data.message);
                    if (result.data.isSuc) {
                        getReviewList();
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

            <!-- Topbar -->
            <?php
            require_once($_SERVER['DOCUMENT_ROOT']."/app/admin/common/header.php");
            ?>
            <!-- End of Topbar -->

            <!-- Begin Page Content -->
            <div class="container-fluid">

                <!-- Page Heading -->
                <h1 class="h3 mb-2 text-gray-800">Tables</h1>
                <p class="mb-4">DataTables is a third party plugin that is used to generate the demo table below.
                    For more information about DataTables, please visit the
                    <a target="_blank" href="https://datatables.net">official DataTables documentation</a>.</p>

                <!-- DataTales Example -->
                <div class="card shadow mb-4">

                    <div class="card-header py-3">
                        <h6 class="m-0 font-weight-bold text-primary">DataTables Example</h6>
                    </div>

                    <div class="card-body">
                        <div class="table-responsive">
                            <table class="table table-bordered" id="dataTable" width="100%" cellspacing="0">
                                <thead>
                                <tr>
                                    <th>노출 시작일</th>
                                    <th>등록된 리뷰수</th>
                                </tr>
                                </thead>

                                <tfoot>
                                <tr>
                                    <th>노출 시작일</th>
                                    <th>등록된 리뷰수</th>
                                </tr>
                                </tfoot>

                                <tbody id="listArea">
                                <?php
                                while ($row = $stmt->fetch(PDO::FETCH_ASSOC)) {
                                ?>
                                    <tr onclick="location.href='/app/admin/review/dumy_daily_detail?format=<?php echo $row['daily_list']?>'">
                                        <td><?php echo $row['daily_list'] ?></td>
                                        <td><?php echo $row['CNT'] ?></td>
                                    </tr>
                                <?php
                                }
                                ?>
                                </tbody>
                            </table>
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
