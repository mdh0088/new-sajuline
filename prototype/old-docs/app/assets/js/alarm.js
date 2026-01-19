function showAlarm(idx,cate,nick_name,code,status,img){

    let status_nm = '';
    if (status == 2){
        status_nm = '상담중';
    } else if (status==3){
        status_nm = '부재중';
    }

    let inner = `
    <div class="inBox">
        <div class="popCont">
            <div class="csAppTop">
                <div class="csBox">
                    <div class="flBox">
                        <div class="ibox">
                            <img id="IMG" src="/app/assets/upload/cs/`+img+`">
                        </div>
                        <div class="tbox">
                            <div class="tagBox">
                                <span class="cate">`+cate+`</span>
                            </div>
                            <div class="owner">
                                <span>`+nick_name+`</span>
                                <span>`+code+`번</span>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            <div class="csAppMid">
                <div class="alarmCont">
                    <p>
                        `+nick_name+` 선생님은 현재 <b class="cRed2">`+status_nm+`</b>입니다.<br><br>

                        상담사 접속 알림을 설정하시면,<br>
                        상담 가능시 카카오 알림톡을 통하여 안내드립니다.
                    </p>
                </div>
            </div>
            <div class="csAppBottom">
                <div class="callBox" onClick="doAlert(`+idx+`,'`+nick_name+`');">
                    <img id="IMG" src="/app/assets/img/contents/ico-alarm.png">
                        <strong>알림 설정</strong>
                </div>
            </div>
        </div>
        <a href="javascript:void(0)" onClick="fn_layer_close('alarmPop');">닫기</a>
    </div>
    `;

    document.querySelector('#alarmPop').innerHTML=inner;
    fn_layer('alarmPop');
}

const doAlert= async(idx,nick_name)=>{

    showLoading();
    let csObj =
        {
            CS_IDX : idx
        };
    try {
        let param = JSON.stringify(csObj);
        let data = new FormData();
        data.append("csObj", param);
        let result = await axios.post('/api/sms/add_alert_list', data);

        console.log(result);
        if (result.data.isSuc) {
            let inner = `
            <div class="inBox">
                <div class="popCont">
                    <h3>알림</h3>
                    <p>`+nick_name+` 선생님 상담가능시 1회성 알림 설정하였습니다.</p>
                    <a href="javascript:void(0)" onClick="fn_layer_close('alarmCheckPop');">확인</a>
                </div>
            </div>
            `;

            document.querySelector('#alarmCheckPop').innerHTML=inner;
            fn_layer_close('alarmPop');
            fn_layer('alarmCheckPop');

        } else {
            alert(result.data.message);
            fn_layer_close('alarmPop');
        }
        hideLoading();
    } catch (err) {
        console.log("Error >>", err);
    }

}
