<?php
require_once($_SERVER['DOCUMENT_ROOT']."/app/common/header.php");

include_once $_SERVER['DOCUMENT_ROOT'].'/api/config/database.php';
include_once $_SERVER['DOCUMENT_ROOT'].'/api/objects/order.php';
include_once $_SERVER['DOCUMENT_ROOT'].'/api/shared/errorlog.php';
$database  = new Database(); $db = $database->getConnection();

$order = new Order($db);
$order_info = $order->read_charge_event();
$current_date = date("Y-m-d H:i:s");
$start_date = $order_info['START_DATE'];
$end_date = $order_info['END_DATE'];

$is_event = 'N';
if ($current_date >= $start_date  &&  $current_date < $end_date && $order_info['USE_YN']=='Y') {
    $is_event = 'Y';
}

?>
<script>
/*// 메타태그
document.addEventListener("DOMContentLoaded", () => {
	document.title = "포인트 충전 | 사주로";
	document.getElementsByTagName('meta')["description"].content = "포인트 충전 : 저렴한 상담비용 결제하기 ! ";
});*/
</script>

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

    #pc-iframe {
        width: 100%;
        height: 100%;
    }
</style>

<script>
    document.addEventListener('DOMContentLoaded', () => {
        choose_point(30000);
    })
    const choose_point =  (amount) => {

        let point = document.querySelector('input[name="point"]:checked').value*1;
        const vat = point / 10;
        const total = (point+vat).toLocaleString()+"원"
        const is_evnt = '<?php echo $is_event ?>';
        if (is_evnt=='Y'){
            if (point == '30000'){
                point = point + (point * (5 / 100));
            } else if (point == '50000'){
                point = point + (point * (5 / 100));
            } else if (point == '100000'){
                point = point + (point * (10 / 100));
            } else if (point == '200000'){
                point = point + (point * (10 / 100));
            } else if (point == '300000'){
                point = point + (point * (15 / 100));
            } else if (point == '500000'){
                point = point + (point * (20 / 100));
            }
        }

        document.querySelector("#total_time").innerHTML = point.toLocaleString()+"P";
        document.querySelector("#total_price").innerHTML = amount.toLocaleString()+"원";
        document.querySelector("#total_vat").innerHTML = vat.toLocaleString()+"원";
        document.querySelector("#total_amt").innerHTML = total;

    }


    const doCharge =  () => {


        //let charge_type = document.querySelector("#charge_type").value;
		let charge_type = document.querySelector('input[name="trade_method"]:checked').value;
        let point = document.querySelector('input[name="point"]:checked').value;

        let pointObj =
            {
                charge_type     : charge_type,
                point           : point,
                tax_amount      : (point*1)/10
            };

        try {
            //let param = encodeURI(JSON.stringify(usrObj));
            let param = JSON.stringify(pointObj);
            let data = new FormData();
            data.append("pointObj",param);
            axios.post('/api/point/Payment',data,null)
                .then((result) => {
                    console.log(result);
                    if (result.data.isSuc===false){
                        alert(result.data.message);
                    } else {
                        if (navigator.maxTouchPoints) {
                            location.href = result.data.mobile_url;
                        } else {
                            //location.href = result.data.online_url;
                            let iframe = document.getElementById("pc-iframe");
                            iframe.src = result.data.mobile_url;
                            document.getElementById("modal").style.display = "block";
                            //window.frames['ifrm_sns'].document.getElementById('birth_year').setAttribute('onChange',"Javascript:window.parent.chkBirthForJoin('sns')");

                            // document.getElementById("pc-iframe-container").style.display = "block";
                        }
                        // alert(result.data.IDX); 하나뽑기
                        // alert(result.data.list[1].IDX); 리스트뽑기
                    }
                })
        } catch(err) {
            console.log("Error >>", err);
        }

    }
</script>

<section id="mypageWrap" class="section">
	<!-- subTitBox -->
	<div class="subTitBox">
		<h3>포인트 충전</h3>
	</div>
	<!--// subTitBox -->

	<!-- payTable -->
	<div class="payTable">
		<div class="payTableTop flBox alC jcSB">
			<p>결제금액(VAT 별도) 선택</p>
			<a href="/app/charge/guide">상담 이용안내</a>
		</div>
		<table class="table table-bordered">
			<thead>
				<tr>

					<th>선택</th>
					<th>결제금액</th>
					<th>충전 포인트</th>
				</tr>
			</thead>
			<tbody>
				<tr>
					<td>
						<div class="radioBox">
							<input type="radio" id="charge01" name="point" value="30000" checked onclick="choose_point(30000);">
							<label for="charge01"></label>
						</div>
					</td>
					<td>30,000원</td>
					<td>30,000P
                    <?php
                    if ($current_date >= $start_date  &&  $current_date < $end_date && $order_info['USE_YN']=='Y') {
                        echo '<span class="evPoint">+5%</span>';
                    }
                    ?>
                    </td>
				</tr>
				<tr>
					<td>
						<div class="radioBox">
							<input type="radio" id="charge02" name="point" value="50000" onclick="choose_point(50000);">
							<label for="charge02"></label>
						</div>
					</td>
					<td>50,000원</td>
					<td>50,000P
                    <?php
                    if ($current_date >= $start_date  &&  $current_date < $end_date && $order_info['USE_YN']=='Y') {
                        echo '<span class="evPoint">+5%</span>';
                    }
                    ?>
                    </td>
				</tr>
				<tr>
					<td>
						<div class="radioBox">
							<input type="radio" id="charge03" name="point" value="100000" onclick="choose_point(100000);">
							<label for="charge03"></label>
						</div>
					</td>
					<td>100,000원</td>
					<td>100,000P
                    <?php
                    if ($current_date >= $start_date  &&  $current_date < $end_date && $order_info['USE_YN']=='Y') {
                        echo '<span class="evPoint">+10%</span>';
                    }
                    ?>
                    </td>
				</tr>
				<tr>
					<td>
						<div class="radioBox">
							<input type="radio" id="charge04" name="point" value="200000" onclick="choose_point(200000);">
							<label for="charge04"></label>
						</div>
					</td>
					<td>200,000원</td>
					<td>200,000P
                    <?php
                    if ($current_date >= $start_date  &&  $current_date < $end_date && $order_info['USE_YN']=='Y') {
                        echo '<span class="evPoint">+10%</span>';
                    }
                    ?>
                    </td>
				</tr>
				<tr>
					<td>
						<div class="radioBox">
							<input type="radio" id="charge05" name="point" value="300000" onclick="choose_point(300000);">
							<label for="charge05"></label>
						</div>
					</td>
					<td>300,000원</td>
					<td>300,000P
                    <?php
                    if ($current_date >= $start_date  &&  $current_date < $end_date && $order_info['USE_YN']=='Y') {
                        echo '<span class="evPoint">+15%</span>';
                    }
                    ?>
                    </td>
				</tr>
				<tr>
					<td>
						<div class="radioBox">
							<input type="radio" id="charge06" name="point" value="500000" onclick="choose_point(500000);">
							<label for="charge06"></label>
						</div>
					</td>
					<td>500,000원</td>
					<td>500,000P
                    <?php
                    if ($current_date >= $start_date  &&  $current_date < $end_date && $order_info['USE_YN']=='Y') {
                        echo '<span class="evPoint">+20%</span>';
                    }
                    ?>
                    </td>
				</tr>
			</tbody>
		</table>
	</div>
	<!--// payTable -->

	<!-- payBox -->
	<div class="payBox mt30">

		<div class="titBox">
			<div class="leftArea">
				<h3>결제수단 선택</h3>
			</div>
		</div>

		<div class="paymentChoiceBox">
			<ul>
				<li>
					<div class="radioBox">
						<input type="radio" id="paymentChoice01" name="trade_method" value="allthegate" checked>
						<label for="paymentChoice01">신용카드</label>
					</div>
				</li>
				<li>
					<div class="radioBox">
						<input type="radio" id="paymentChoice02" name="trade_method" value="virtualaccount">
						<label for="paymentChoice02">무통장입금</label>
					</div>
				</li>
				<li>
					<div class="radioBox">
						<input type="radio" id="paymentChoice03" name="trade_method" value="kakaopay">
						<label for="paymentChoice03">카카오페이</label>
					</div>
				</li>

<!--                <li>
                    <div class="radioBox">
                        <input type="radio" id="paymentChoice04" name="trade_method" value="naverpay">
                        <label for="paymentChoice04">네이버페이</label>
                    </div>
                </li>

                <li>
                    <div class="radioBox">
                        <input type="radio" id="paymentChoice05" name="trade_method" value="allthegate">
                        <label for="paymentChoice05">올더게이트</label>
                    </div>
                </li>-->



			</ul>
		</div>

	</div>
	<!--// payBox -->

	<!-- payBox -->
	<div class="payBox mt40">
		<div class="titBox">
			<div class="leftArea">
				<h3>결제내역 확인</h3>
			</div>
		</div>
		<div class="totalBox">
			<dl>
				<dt>충전 포인트</dt>
				<dd id="total_time" class="total_part_1"></dd>
			</dl>
			<dl>
				<dt>총 결제금액</dt>
				<dd id="total_price" class="total_part_2"></dd>
			</dl>
			<dl>
				<dt>VAT</dt>
				<dd id="total_vat" class="total_part_3"></dd>
			</dl>
			<dl class="totalPrice">
				<dt>결제금액 합계</dt>
				<dd id="total_amt" class="total_part_4"></dd>
			</dl>
		</div>
	</div>
	<!--// payBox -->

	<!-- bottomBtn -->
	<div class="bottomBtn mt25">
		<button type="button" class="btn" onclick="doCharge();">결제하기</button>
	</div>
	<!--// bottomBtn -->

</section>


<div id="modal" style="display: none;">
    <div id="modal-content">
        <iframe src="" id="pc-iframe"></iframe>
    </div>
</div>

<script src="/app/assets/js/setMeta.js"></script>
<script>
    setMeta({
        title: '포인트 충전',
        description:
            '포인트 충전 : 저렴한 상담비용 결제하기 !',
        url: 'https://sajutarot.com/app/charge/point',
        keyword: ''
    });
</script>
<?php
require_once($_SERVER['DOCUMENT_ROOT']."/app/common/footer.php");
?>
