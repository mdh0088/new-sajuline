<?php
require_once($_SERVER['DOCUMENT_ROOT']."/app/common/header.php");

if (!isset($_SESSION['IDX'])){
    echo "
        <script>
            alert('잘못된 접근입니다.');
            location.href='/';
        </script>
        ";
}

if ($_SESSION['IS_CS']=='Y'){
    echo "
        <script>
            location.href='/app/cs/mypage';
        </script>
        ";
}
$user_idx = $_SESSION['IDX'];
?>

<script>
    document.addEventListener('DOMContentLoaded', () => {
        getChargeInfo();
    })

    const getChargeInfo = async () => {
        showLoading();
        let userObj =
            {
                IDX : <?php echo $user_idx?>
            };
        try {
            let param = JSON.stringify(userObj);
            let data = new FormData();
            data.append("userObj", param);
            let result = await axios.post('/api/user/read_chargeInfo', data);

            console.log(result);
            if (result.data.isSuc) {
                let charge_info = result.data.list;
                let inner = '';

                charge_info.forEach(item => {
                    inner +='<tr>';
                    inner +='    <td>'+( isNull(item.TRANSACTION_DATE)?'':item.TRANSACTION_DATE )+'</td>';
                    inner +='    <td><strong>+'+item.PRODUCT_NAME+'P</strong></td>';
                    inner +='    <td class="mainColor">'+( isNull(item.AMOUNT)?'':item.AMOUNT+'원')+'</td>';
                    inner +='    <td>'+item.PAY_TYPE+'</td>';
                    inner +='</tr>';
                });
                document.querySelector("#charge_area").innerHTML = inner;
            } else {

            }
            hideLoading();
        } catch (err) {
            console.log("Error >>", err);
        }
    }
</script>

<div id="detailTop">
	<div class="inner">
		<div class="leftArea">
			<button type="button" class="btnBack" onclick="pageBack();">
				<img src="/app/assets/img/contents/ico-back-btn.png">
				뒤로가기
			</button>
		</div>
	</div>
</div>

<section id="mypageWrap" class="section myCharge">

	<!-- subTitBox -->
	<div class="subTitBox">
	  <h3>충전내역 보기</h3>
	</div>
	<!--// subTitBox -->

	<div class="colTable">
		<table>
			<caption>충전날짜, 결제정보, 충전금액, 상태 항목으로 구성된 충전내역 표 입니다.</caption>
			<colgroup>
				<col style="width:25%"></col>
				<col style="width:30%"></col>
				<col style="width:30%"></col>
				<col style="width:15%"></col>
			</colgroup>
			<thead>
				<tr>
					<th>충전날짜</th>
					<th>충전포인트</th>
					<th>충전금액</th>
					<th>상태</th>
				</tr>
			</thead>
			<tbody id="charge_area">

			</tbody>
		</table>
	</div>

</section>



<script src="/app/assets/js/setMeta.js"></script>
<script>
    setMeta({
        title: '나의 충전내역',
        description:
            '나의 충전내역 : 나의 포인트 결제내역을 한눈에 ! No.1 전화 사주/타로상담 서비스 플랫폼 사주로',
        url: 'https://sajutarot.com/app/user/history_charge',
        keyword: ''
    });
</script>

<?php
require_once($_SERVER['DOCUMENT_ROOT']."/app/common/footer.php");
?>

<style>
	footer {display:none !important;}
</style>
