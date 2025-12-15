<?php
require_once($_SERVER['DOCUMENT_ROOT']."/app/admin/common/top.php");
?>

<script>


    document.addEventListener('DOMContentLoaded', () => {
        getRecruitList();
    })


    const getRecruitList = () => {
        let csObj =
            {
                // SEARCH_NAME		  : document.querySelector('#seaarch_name').value
                SEARCH_NAME		  : "test"
            };

        try {
            let param = JSON.stringify(csObj);
            let data = new FormData();
            data.append("csObj", param);
            axios.post('/api/user/admin_user_list', data)
                .then((result) => {
                    console.log(result);
                    if (result.data.isSuc) {
                        let inner = "";
                        result.data.list.forEach(item => {
                            inner += '<tr>';
                            inner += '<td onclick="javascript:location.href=\'/app/admin/user/detail?idx='+item.IDX+'\' ">' + item.NICK_NAME + '</td>';
                            inner += " <td>" + item.USER_ID + " </td>";
                            inner += " <td>" + item.EMAIL + "</td>";
                            inner += " <td>" + item.PHONE + "</td>";
                            inner += " <td>" + item.JOIN_TYPE + "</td>";
                            inner += " <td>" + item.REGIST_DATE + "</td>";
                            inner += " <td>" + item.LAST_LOGIN + " <button onclick='delete_user("+item.IDX+");'>탈퇴</button> </td>";
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


    const delete_user = async (idx) => {

        if (!confirm('정말로 이 작업을 수행하시겠습니까?')) {
            return;
        }



        let userObj =
            {
                IDX : idx
            };

        try {
            let param = JSON.stringify(userObj);
            let data = new FormData();
            data.append("userObj", param);
            let result = await axios.post('/api/admin/user/delete', data);

            console.log(result);
            alert(result.data.message);
            if (result.data.isSuc) {
                location.reload();
            } else {
            }
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
                                    <th>닉네임</th>
                                    <th>아이디</th>
                                    <th>이메일</th>
                                    <th>핸드폰</th>
                                    <th>가입루트</th>
                                    <th>가입일</th>
                                    <th>마지막 로그인</th>
                                </tr>
                                </thead>

                                <tfoot>
                                <tr>
                                    <th>닉네임</th>
                                    <th>아이디</th>
                                    <th>이메일</th>
                                    <th>핸드폰</th>
                                    <th>가입루트</th>
                                    <th>가입일</th>
                                    <th>마지막 로그인</th>
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
