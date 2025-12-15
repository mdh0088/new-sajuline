<?php
require_once($_SERVER['DOCUMENT_ROOT']."/app/admin/common/top.php");
?>

<style>
    #popup {
        display: none;
        position: fixed;
        top: 50%;
        left: 50%;
        max-height: 80%; /* Add max height */
        overflow-y: auto; /* Add scroll for overflow */
        transform: translate(-50%, -50%);
        background-color: white;
        padding: 20px;
        border: 1px solid black;
        z-index: 1000;
    }
    #overlay {
        display: none;
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background-color: rgba(0, 0, 0, 0.5);
        z-index: 999;
    }
    /* Add this style for the pre tag inside the popup */
    #popup-content {
        white-space: pre-wrap;
        word-wrap: break-word;
    }

    #edit-button {
        display: none;
        background-color: #b9b9e7;
        color: white;
        padding: 5px;
        cursor: pointer;
        margin-top: 10px;
    }
</style>

<script>


    document.addEventListener('DOMContentLoaded', () => {
        getRecruitList();
    })


    const getRecruitList = () => {
        let userObj =
            {
                // SEARCH_NAME		  : document.querySelector('#seaarch_name').value
                SEARCH_NAME		  : "test"
            };

        try {
            let param = JSON.stringify(userObj);
            let data = new FormData();
            data.append("userObj", param);
            axios.post('/api/admin/user/read_user_faq', data)
                .then((result) => {
                    console.log(result);
                    if (result.data.isSuc) {
                        let inner = "";
                        result.data.list.forEach(item => {
                            inner += '<tr>';
                            inner += " <td>" + item.NICK_NAME + "</td>";
                            inner += " <td>" + item.USER_ID + "</td>";
                            inner += " <td>" + item.USER_TITLE + "</td>";

                            let user_cont = (item.USER_CONT || '').replace(/\n/g, ' ').replace(/'/g, "\\'").replace(/"/g, '&quot;');
                            let shortened_user_cont = user_cont.length > 20 ? user_cont.substring(0, 20) + "..." : user_cont;

                            let admin_cont = (item.ADMIN_CONT || '').replace(/\n/g, ' ').replace(/'/g, "\\'").replace(/"/g, '&quot;');
                            let shortened_ADMIN_cont = admin_cont.length > 20 ? admin_cont.substring(0, 20) + "..." : admin_cont;

                            inner += ` <td onclick="showPopup('${user_cont.replace(/'/g, "\\'").replace(/"/g, '\\"')}')">` + shortened_user_cont + "</td>";

                            inner += " <td>" + ( isNull(item.USER_REGIST_DATE)?'':item.USER_REGIST_DATE )+"</td>";
                            inner += ` <td onclick="showPopup('${admin_cont.replace(/'/g, "\\'").replace(/"/g, '\\"')}', '${item.IDX}', true)">` + shortened_ADMIN_cont + "</td>";
                            inner += " <td>" + ( isNull(item.ADMIN_REGIST_DATE)?'':item.ADMIN_REGIST_DATE )+ "</td>";
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
    function showPopup(content, itemId, showEditButton = false) {
        const popupContent = document.getElementById('popup-content');
        if (showEditButton) {
            popupContent.innerHTML = `<textarea id="admin-content-textarea">${content}</textarea>`;
        } else {
            popupContent.innerText = content;
        }
        document.getElementById('edit-button').style.display = showEditButton ? 'block' : 'none';
        if (showEditButton) {
            document.getElementById('edit-button').setAttribute('data-item-id', itemId);
        }
        document.getElementById('popup').style.display = 'block';
        document.getElementById('overlay').style.display = 'block';
    }

    function closePopup() {
        document.getElementById('popup').style.display = 'none';
        document.getElementById('overlay').style.display = 'none';
    }

    // Add a function for the '수정' button click
    function editButtonClick() {
        const itemId = document.getElementById('edit-button').getAttribute('data-item-id');
        const cont = document.querySelector('#admin-content-textarea').value;
        if (cont == ''){
            alert('수정할 내용을 입력해주세요.');
            return;
        }

        let userObj =
            {
                CONT : cont,
                IDX  : itemId
            };

        try {
            let param = JSON.stringify(userObj);
            let data = new FormData();
            data.append("userObj", param);
            axios.post('/api/admin/user/update_user_faq', data)
                .then((result) => {
                    console.log(result);
                    alert(result.data.message);
                    if (result.data.isSuc) {
                        location.reload();
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
                                    <th>닉네임</th>
                                    <th>유저 아이디</th>
                                    <th>문의 제목</th>
                                    <th>문의 내용</th>
                                    <th>문의 날짜</th>
                                    <th>답변 내용</th>
                                    <th>답변 날짜</th>
                                </tr>
                                </thead>

                                <tfoot>
                                <tr>
                                    <th>닉네임</th>
                                    <th>유저 아이디</th>
                                    <th>문의 제목</th>
                                    <th>문의 내용</th>
                                    <th>문의 날짜</th>
                                    <th>답변 내용</th>
                                    <th>답변 날짜</th>
                                </tr>
                                </tfoot>

                                <tbody id="listArea">

                                </tbody>
                            </table>

                            <div id="overlay" onclick="closePopup()"></div>
                            <div id="popup">
                                <pre id="popup-content"></pre>
                                <div id="edit-button" onclick="editButtonClick()">수정</div>
                            </div>
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
