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


    let key_cnt=0;
    const add_keyword = () => {
        const keywords = document.querySelectorAll('.keyword');
        const keywordLimit = 10;
        if (keywords.length < keywordLimit) {
            key_cnt++;
            const keyword = document.querySelector('#target_keyword').value;

            if (!keyword){
                //alert('키워드를 입력해주세요');
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


    const img_upload = () => {
        const fileInput = document.getElementById("IMG");
        const imgElement = document.getElementById("MAIN_IMG");
        let file = fileInput.files[0];
        let reader = new FileReader();
        reader.onload = function(event) {
            imgElement.src = event.target.result;
        };
        reader.readAsDataURL(file);
        let fileName = file.name; // 파일 이름 가져오기
        document.querySelector('#img_value').value = fileName;
    }

    const save_pw = () => {

        if(isNull(document.querySelector("#PASSWORD").value)){
            alert('비밀번호를 입력해주세요.');
            document.querySelector("#pw").focus();
            return;
        }
/*
        if(!isValidPassword(document.querySelector("#PASSWORD").value)){
            alert('비밀번호가 8자 이상, 영문 대/소문자, 숫자, 특수 문자 중 적어도 하나씩을 포함하고 있어야 합니다.');
            document.querySelector("#pw").focus();
            return;
        }*/

        let csObj =
            {
                IDX		  : "<?php echo $cs_idx ?>"
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


    const getCSInfo = () => {
        let csObj =
            {
                IDX		  : "<?php echo $cs_idx ?>"
            };

        try {
            let param = JSON.stringify(csObj);
            let data = new FormData();
            data.append("csObj", param);
            axios.post('/api/cs/readOne', data)
                .then((result) => {
                    console.log(result);
                    if (result.data.isSuc) {

                        csObj = result.data.csObj;

                        document.querySelector('#NAME').value = csObj.NAME;
                        document.querySelector('#NICK_NAME').value = csObj.NICK_NAME;
                        document.querySelector('#EMAIL').value = csObj.EMAIL;

                        document.querySelector('#PHONE').innerHTML = csObj.PHONE;

                        document.querySelector('#img_value').value = csObj.IMG
                        document.querySelector('#MAIN_IMG').src = '/app/assets/upload/cs/'+csObj.IMG

                        const cs_keyword = csObj.CS_KEYWORD.split(',');
                        for (const keyword of cs_keyword) {
                            document.querySelector('#target_keyword').value = keyword;
                            add_keyword();
                        }

                        document.querySelector('input[name="STATUS"][value="' + csObj.STATUS + '"]').checked = true;

                        document.querySelector('#CODE').value = csObj.CODE;
                        document.querySelector('#GRADE').value = csObj.GRADE;

                        document.querySelector('input[name="TYPE"][value="' + csObj.TYPE + '"]').checked = true;
                        /*
                        if(csObj.TARO_YN=='Y'){document.querySelector('#TARO_YN').checked = true;}
                        if(csObj.LUCK_YN=='Y'){document.querySelector('#LUCK_YN').checked = true;}
                        if(csObj.FORTUNE_YN=='Y'){document.querySelector('#FORTUNE_YN').checked = true;}
                        if(csObj.EASY_YN=='Y'){document.querySelector('#EASY_YN').checked = true;}
                        */
                        document.querySelector('#SHORT_INFO').value = csObj.SHORT_INFO;
                        document.querySelector('#NOTICE').value = csObj.NOTICE.replace(/<br\s*[/]?>/gi, "\n");
                        document.querySelector('#GREETING').value = csObj.GREETING.replace(/<br\s*[/]?>/gi, "\n");
                        document.querySelector('#CAREER').value = csObj.CAREER.replace(/<br\s*[/]?>/gi, "\n");

                        document.querySelector('#WORK_TIME').value = csObj.WORK_TIME;
                        document.querySelector('#AFTER_AMOUNT').value = csObj.AFTER_AMOUNT;
                        //document.querySelector('#BEFORE_AMOUNT').value = csObj.BEFORE_AMOUNT;

                        if(csObj.SHOW_YN=='Y'){document.querySelector('#SHOW_YN').checked = true;}
                        if(csObj.NEW_YN=='Y'){document.querySelector('#NEW_YN').checked = true;}
                        document.querySelector('#CS_DATE').value = csObj.CS_DATE;
                    } else {

                    }
                })
        } catch (err) {
            console.log("Error >>", err);
        }

    }


    const update_cs = () => {

        if (isNull(document.querySelector('#NAME').value)){
            alert("이름을 입력해주세요.");
            return;
        }

        if (isNull(document.querySelector('#NICK_NAME').value)){
            alert("닉네임을 입력해주세요.");
            return;
        }

        if (isNull(document.querySelector('#EMAIL').value)){
            alert("이메일을 입력해주세요.");
            return;
        }

        if(!validateEmail(document.querySelector("#EMAIL").value)){
            alert('이메일을 양식을 맞춰주세요.');
            return;
        }



        //키워드 text 뽑아서 list로 세팅
        const keywords = document.querySelectorAll('.keyword');
        let keyword_arr = new Array();
        if (keywords.length > 0 && keywords.length < 11){
            for (const element of keywords) {
                keyword_arr.push(element.textContent)
            }
        } else if (keywords.length > 10) {
            alert('최대 10개만 입력이 가능합니다.');
            return;
        } else if(keywords.length == 0){
            alert('키워드를 입력해주세요.');
            return;
        }


        if(isNull(document.querySelector("#SHORT_INFO").value)){
            alert('짧은 소개글을 작성해주세요.');
            return;
        }


        if(isNull(document.querySelector("#GREETING").value)){
            alert('인사말을 작성해주세요.');
            return;
        }

        if(isNull(document.querySelector("#CAREER").value)){
            alert('경력사항을 기재해주세요.');
            return;
        }


        let csObj =
            {
                IDX		        :  "<?php echo $cs_idx ?>",
                NAME            : document.querySelector('#NAME').value,
                NICK_NAME       : document.querySelector('#NICK_NAME').value,
                //EMAIL           : document.querySelector('#EMAIL').value,
                //PHONE           : document.querySelector('#PHONE').value,
                KEYWORD      : keyword_arr,
                STATUS          : document.querySelector('input[name="STATUS"]:checked').value,
                CODE            : document.querySelector('#CODE').value,
                GRADE           : document.querySelector('#GRADE').value,

                TYPE          : document.querySelector('input[name="TYPE"]:checked').value,
                /*
                TARO_YN         : document.getElementById("TARO_YN").checked ? "Y" : "N",
                LUCK_YN         : document.getElementById("LUCK_YN").checked ? "Y" : "N",
                FORTUNE_YN      : document.getElementById("FORTUNE_YN").checked ? "Y" : "N",
                EASY_YN         : document.getElementById("EASY_YN").checked ? "Y" : "N",
                */
                SHORT_INFO       : document.querySelector('#SHORT_INFO').value,
                NOTICE        : document.querySelector('#NOTICE').value,
                GREETING        : document.querySelector('#GREETING').value,
                CAREER          : document.querySelector('#CAREER').value,
                WORK_TIME       : document.querySelector('#WORK_TIME').value,
                AFTER_AMOUNT    : document.querySelector('#AFTER_AMOUNT').value,
                /*BEFORE_AMOUNT   : document.querySelector('#BEFORE_AMOUNT').value,*/
                SHOW_YN         : document.getElementById("SHOW_YN").checked ? "Y" : "N",
                NEW_YN         : document.getElementById("NEW_YN").checked ? "Y" : "N",
                IMG_VALUE       : document.querySelector('#img_value').value

            };

        const files = [];
        const fileInputs = document.querySelectorAll('.img_file');
        if (fileInputs.length > 0) {
            for (const fileInput of fileInputs) {
                files.push(fileInput.files[0]);
            }
        }

        try {
            let param = JSON.stringify(csObj);
            let data = new FormData();
            data.append("csObj", param);

            //list 파일 세팅
            for (let i = 0; i < files.length; i++) {
                data.append("file[]", files[i]);
            }

            axios.post('/api/cs/update', data, {
                headers: {
                    'Content-Type': 'multipart/form-data'
                }
            })
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
                                <p>이름 : <input type="text" id="NAME" value=""> </p>
                                <p>닉네임 : <input type="text" id="NICK_NAME" value=""> </p>
                                <p><input type="button" value="비밀번호 수정" onclick="Javascript:document.querySelector('#modal').style.display = 'block'; document.querySelectorAll('.pop_keyword').forEach(el => el.style.display = 'none');"> </p>
                                <p>이메일 : <input type="text" id="EMAIL" value="" readonly> </p>
                                <p>핸드폰 : <span id="PHONE"></span> </p>
                                <p>메인 이미지 :
                                    <input type="hidden" id="img_value">
                                    <img src="" id="MAIN_IMG" style="width: 200px; height: 200px">
                                    <input type='file' id="IMG" class="img_file" name='img_file' onchange="img_upload();">
                                </p>

                                <p>키워드 :
                                <div id="keyword_area" class="form-group">
                                    <input type="text" onclick="Javascript:document.querySelector('#modal').style.display = 'block'; document.querySelector('#target_keyword').focus(); document.querySelectorAll('.pop_password').forEach(el => el.style.display = 'none');" readonly><br>
                                </div>
                                </p>

                                <p>상담사 상태 :

                                    <div class="form-check form-check-inline">
                                        <input class="form-check-input" type="radio" name="STATUS" id="STATUS_1" value="1">
                                        <label class="form-check-label" for="STATUS_1">대기중</label>
                                    </div>
                                    <div class="form-check form-check-inline">
                                        <input class="form-check-input" type="radio" name="STATUS" id="STATUS_2" value="2">
                                        <label class="form-check-label" for="STATUS_2">상담중</label>
                                    </div>
                                    <div class="form-check form-check-inline">
                                        <input class="form-check-input" type="radio" name="STATUS" id="STATUS_3" value="3">
                                        <label class="form-check-label" for="STATUS_3">부재중</label>
                                    </div>

                                </p>
                                <p>상담사 코드 : <input type="text" id="CODE" value=""> </p>
                                <p>상담사 등급 :
                                    <select id="GRADE">

                                        <option value="BRONZE">BRONZE</option>
                                        <option value="SILVER">SILVER</option>
                                        <option value="GOLD">GOLD</option>

                                    </select>
                                </p>

                                타입 :
                                <div class="form-check form-check-inline">
                                    <input class="form-check-input" type="radio" name="TYPE" id="tarot" value="1" checked>
                                    <label class="form-check-label" for="tarot">타로</label>
                                </div>
                                <div class="form-check form-check-inline">
                                    <input class="form-check-input" type="radio" name="TYPE" id="psychic" value="2">
                                    <label class="form-check-label" for="psychic">신점</label>
                                </div>
                                <div class="form-check form-check-inline">
                                    <input class="form-check-input" type="radio" name="TYPE" id="palmistry" value="3">
                                    <label class="form-check-label" for="palmistry">역학</label>
                                </div>
                                <div class="form-check form-check-inline">
                                    <input class="form-check-input" type="radio" name="TYPE" id="divination" value="4">
                                    <label class="form-check-label" for="divination">사주</label>
                                </div>



                                <p>짧은 한줄 : <input type="text" id="SHORT_INFO" value=""> </p>
                                <p>공지 : <textarea id="NOTICE" style="width: 500px; height: 200px"></textarea> </p>
                                <p>인사말 : <textarea id="GREETING" style="width: 500px; height: 200px"></textarea> </p>
                                <p>커리어 : <textarea id="CAREER" style="width: 500px; height: 200px"></textarea></p>

                                <p>상담사 업무 시간 : <input type="text" id="WORK_TIME" value=""> </p>
                                <p>상담사 선불금액 : <input type="text" id="AFTER_AMOUNT" value=""> </p>
                                <!--<p>삼담사 후불금액 : <input type="text" id="BEFORE_AMOUNT" value=""> </p>-->
                                <p>노출여부 : <input type="checkbox" id="SHOW_YN" value=""> </p>
                                <p>신규여부 : <input type="checkbox" id="NEW_YN" value=""> </p>
                                <p>상담사 등록일 : <input type="text" id="CS_DATE" value="" readonly> </p>

                                <input type="button" value="저장" onclick="update_cs();">
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

