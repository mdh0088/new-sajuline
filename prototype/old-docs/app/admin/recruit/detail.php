<?php
require_once($_SERVER['DOCUMENT_ROOT']."/app/admin/common/top.php");
$cs_idx = $_GET['idx'];
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

    document.addEventListener('DOMContentLoaded', () => {
        getCSInfo();
    })

    const getCSInfo = () => {
        let csObj =
            {
                IDX		  : "<?php echo $cs_idx ?>"
            };

        try {
            let param = JSON.stringify(csObj);
            let data = new FormData();
            data.append("csObj", param);
            axios.post('/api/recruit/readOne', data)
                .then((result) => {
                    console.log(result);
                    if (result.data.isSuc) {
                        document.querySelector('#NAME').textContent = result.data.csObj.NAME;
                        document.querySelector('#NICK_NAME').textContent = result.data.csObj.NICK_NAME;
                        document.querySelector('#EMAIL').textContent = result.data.csObj.EMAIL;
                        document.querySelector('#PHONE').textContent = result.data.csObj.PHONE;
                        //document.querySelector('#ADDRESS').textContent = result.data.csObj.ADDRESS;

                        let type = ['타로','신점','역학','사주'];
                        document.querySelector('#TYPE').textContent = type[(result.data.csObj.TYPE)-1];
                        document.querySelector('#CS_KEYWORD').textContent = result.data.csObj.CS_KEYWORD;


                        !isNull(result.data.csObj.IMG1)?document.querySelector('#IMG1').src = '/app/assets/upload/recruit/'+result.data.csObj.IMG1:
                            document.querySelector('#IMG1').remove();
                        !isNull(result.data.csObj.IMG2)?document.querySelector('#IMG2').src = '/app/assets/upload/recruit/'+result.data.csObj.IMG2:
                            document.querySelector('#IMG2').remove();
                        !isNull(result.data.csObj.IMG3)?document.querySelector('#IMG3').src = '/app/assets/upload/recruit/'+result.data.csObj.IMG3:
                            document.querySelector('#IMG3').remove();
                        !isNull(result.data.csObj.IMG4)?document.querySelector('#IMG4').src = '/app/assets/upload/recruit/'+result.data.csObj.IMG4:
                            document.querySelector('#IMG4').remove();
                        !isNull(result.data.csObj.IMG5)?document.querySelector('#IMG5').src = '/app/assets/upload/recruit/'+result.data.csObj.IMG5:
                            document.querySelector('#IMG5').remove();

                        document.querySelector('#SHORT_INFO').textContent = result.data.csObj.SHORT_INFO;
                        document.querySelector('#GREETING').textContent = result.data.csObj.GREETING.replace(/<br\s*[/]?>/gi, "\n");
                        document.querySelector('#CAREER').textContent = result.data.csObj.CAREER.replace(/<br\s*[/]?>/gi, "\n");

                        document.querySelector('#RECRUIT_DATE').textContent = result.data.csObj.RECRUIT_DATE;

                    } else {

                    }
                })
        } catch (err) {
            console.log("Error >>", err);
        }

    }

    const update_approval = () => {

        let csObj =
            {
                IDX		  : "<?php echo $cs_idx ?>"
            };

        if (isNull(document.querySelector('#CS_CODE').value)){
            alert('상담사 코드를 입력해주세요.');
            return;
        }

        if (!formatThreeDigitNumber(csObj.CODE)){
            alert('0이 아닌 3자리수만 입력 가능합니다.');
            return;
        }

        csObj.CODE = formatThreeDigitNumber(document.querySelector('#CS_CODE').value);

        if (!isValidNumber(csObj.CODE)){
            alert('숫자 3자리수 이하의 값을 입력해주세요.');
            return;
        }


        try {
            let param = JSON.stringify(csObj);
            let data = new FormData();
            data.append("csObj", param);
            axios.post('/api/recruit/create_cs', data)
                .then((result) => {
                    console.log(result);
                    alert(result.data.message);
                    if (result.data.isSuc) {
                        location.href='/app/admin/recruit/list';
                    } else {

                    }
                })
        } catch (err) {
            console.log("Error >>", err);
        }


    }

    let key_cnt=0;
    const add_keyword = () => {
        const keywords = document.querySelectorAll('.keyword');
        const keywordLimit = 10;
        if (keywords.length < keywordLimit) {
            key_cnt++;
            const keyword = document.querySelector('#target_keyword').value;

            if (!keyword){
                alert('키워드를 입력해주세요');
                return;
            }

            for (const element of keywords) {
                if (keyword === element.textContent) {
                    alert("중복된 키워드가 있습니다.");
                    return;
                }
            }

            let inner = "";
            inner += "<span id='keyword_"+key_cnt+"'>";
            inner += "<b class='keyword'>"+keyword+"</b>";
            inner += "<input type='button' value='삭제' onclick='Javascript:document.querySelector(\"#keyword_" + key_cnt + "\").remove()'>";
            inner += "</span>";

            document.querySelector("#keyword_area").insertAdjacentHTML("beforeend", inner);

        } else {
            alert('10개만 등록 가능합니다.');
        }
        document.getElementById('modal').style.display = 'none';
        document.querySelector('#target_keyword').value='';

    }


    function isValidNumber(input) {
        if (!input) return false;
        return /^\d{1,3}$/.test(input);
    }

    function formatThreeDigitNumber(number) {
        if (number > 999 || number == 0 ) {
            return false;
        }

        let formattedNumber = String(number);
        while (formattedNumber.length < 3) {
            formattedNumber = '0' + formattedNumber;
        }

        return formattedNumber;
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
                                <p>이름 : <span id="NAME"></span> </p>
                                <p>닉네임 : <span id="NICK_NAME"></span> </p>
                                <p>이메일 : <span id="EMAIL"></span> </p>
                                <p>핸드폰 : <span id="PHONE"></span> </p>
                                <!--<p>지역 :  <span id="ADDRESS"></span></p>
-->
                                <p>신청 타입 : <span id="TYPE"></span> </p>

                                <p>신청 키워드 :<span id="CS_KEYWORD"></span> </p>
                                <p>신청 이미지1 : <img src="" id="IMG1" style="width: 200px; height: 200px"></p>
                                <p>신청 이미지2 : <img src="" id="IMG2" style="width: 200px; height: 200px"></p>
                                <p>신청 이미지3 : <img src="" id="IMG3" style="width: 200px; height: 200px"></p>
                                <p>신청 이미지4 : <img src="" id="IMG4" style="width: 200px; height: 200px"></p>
                                <p>신청 이미지5 : <img src="" id="IMG5" style="width: 200px; height: 200px"></p>
                                <p>짧은 한줄 : <span id="SHORT_INFO"></span></p>
                                <p>인사말 : <textarea id="GREETING" style="width: 500px; height: 200px" readonly></textarea></p>
                                <p>커리어 : <textarea id="CAREER" style="width: 500px; height: 200px"  readonly></textarea></p>
                                <p>상담사 등록 신청일 : <span id="RECRUIT_DATE"></span> </p>

                                <p>상담사 부여코드 : <input type="text" id="CS_CODE"> </p>
                                <input type="button" value="상담사로 전환" onclick="update_approval();">
                                <hr>
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

<div id="modal" style="display: none;">
    <div id="modal-content">
        <input type="button" value="닫기" onclick="Javascript:document.getElementById('modal').style.display = 'none';">
        <input type="text" id="target_keyword" onkeypress="if (event.keyCode == 13) add_keyword()">
        <input type="button" value="등록" onclick="add_keyword()">
    </div>
</div>
<!-- End of Page Wrapper -->
<?php
require_once($_SERVER['DOCUMENT_ROOT']."/app/admin/common/bottom.php");
?>

