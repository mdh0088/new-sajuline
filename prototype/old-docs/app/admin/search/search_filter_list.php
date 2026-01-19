<?php
require_once($_SERVER['DOCUMENT_ROOT']."/app/admin/common/top.php");


?>

<script>


    document.addEventListener('DOMContentLoaded', () => {
        getSeachList();
    })



    const getSeachList = () => {
        let csObj =
            {

            };

        try {
            let param = JSON.stringify(csObj);
            let data = new FormData();
            data.append("csObj", param);
            axios.post('/api/admin/search/read_admin_search_filter_list', data)
                .then((result) => {
                    console.log(result);
                    if (result.data.isSuc) {
                        let inner = "";
                        let cnt= 0;
                        result.data.list.forEach(item => {
                            cnt++;
                            inner += '<tr>';
                            inner += ' <td> '+item.KEYWORD;
                            inner += '  <button class="btn btn-danger" type="button" onclick="delete_filter_keyword('+item.IDX+');">삭제</button>';
                            inner += ' </td>';
                            inner += "</tr>";
                        });

                        document.querySelector('#listArea').innerHTML=inner;
                        $('#dataTable').DataTable();
                    } else {
                    }
                })
        } catch (err) {
            console.log("Error >>", err);
        }
    }


    const delete_filter_keyword = (IDX) => {


        let searchObj =
            {
                IDX : IDX
            };


        try {
            let param = JSON.stringify(searchObj);
            let data = new FormData();
            data.append("searchObj", param);
            axios.post('/api/admin/search/delete_filter_keyword', data)
                .then((result) => {
                    console.log(result);
                    alert(result.data.message);
                    if (result.data.isSuc) {
                        getSeachList();
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
                                    <th>필터 키워드</th>
                                </tr>
                                </thead>

                                <tfoot>
                                <tr>
                                    <th>필터 키워드</th>
                                </tr>
                                </tfoot>

                                <tbody id="listArea">

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
