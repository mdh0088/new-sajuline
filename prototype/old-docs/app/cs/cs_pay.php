<?php
require_once($_SERVER['DOCUMENT_ROOT']."/app/common/header.php");

if (!isset($_SESSION['IDX'])){
    echo "
        <script>
            alert('잘못된 접근입니다.');
            location.href='/app/main';
        </script>
        ";
}

if ($_SESSION['IS_CS']!='Y'){
    echo "
        <script>
            location.href='/app/main';
        </script>
        ";
}


$grade = $_SESSION['GRADE'];
?>

<section id="csWrap" class="section">
	<!-- subTitBox -->
	<div class="subTitBox">
		<h3>상담료 안내</h3>
	</div>
	<!--// subTitBox -->
    <?
        if($grade=='BRONZE'){
    ?>
	<div class="payTable csPayTable bronze">
		<table>
			<thead>
				<tr>
					<th>등급</th>
					<th>자격요건</th>
					<th>상담료</th>
				</tr>
			</thead>
			<tbody>
				<tr>
					<td rowspan="8">
						<img src="/app/assets/img/contents/ico-rank-bronze.png" />브론즈
					</td>
				</tr>
				<tr>
					<td>0~10시간</td>
					<td>40,000원</td>
				</tr>
                <tr>
					<td>10~30시간</td>
					<td>42,000원</td>
				</tr>
				<tr>
					<td>30~40시간</td>
					<td>44,000원</td>
				</tr>
				<tr>
					<td>40~50시간</td>
					<td>45,000원</td>
				</tr>
				<tr>
					<td>50~70시간</td>
					<td>47,000원</td>
				</tr>
				<tr>
					<td>70~90시간</td>
					<td>49,000원</td>
				</tr>
                <tr>
					<td>100시간 이상</td>
					<td>50,000원</td>
				</tr>
			</tbody>

		</table>
	</div>
    <?
        }
    ?>

    <?
    if($grade=='SILVER'){
    ?>
	<div class="payTable csPayTable silver">
		<table>
			<thead>
				<tr>
					<th>등급</th>
					<th>자격요건</th>
					<th>상담료</th>
				</tr>
			</thead>
			<tbody>
				<tr>
					<td rowspan="13">
						<img src="/app/assets/img/contents/ico-rank-silver.png" />실버
					</td>
				</tr>
				<tr>
					<td>0~10시간</td>
					<td>45,000원</td>
				</tr>
                <tr>
					<td>10~30시간</td>
					<td>47,000원</td>
				</tr>
				<tr>
					<td>30~40시간</td>
					<td>49,000원</td>
				</tr>
				<tr>
					<td>40~50시간</td>
					<td>50,000원</td>
				</tr>
				<tr>
					<td>50~60시간</td>
					<td>52,000원</td>
				</tr>
				<tr>
					<td>60~70시간</td>
					<td>54,000원</td>
				</tr>
				<tr>
					<td>70~80시간</td>
					<td>56,000원</td>
				</tr>
                <tr>
					<td>80~90시간</td>
					<td>58,000원</td>
				</tr>
                <tr>
					<td>90~100시간</td>
					<td>60,000원</td>
				</tr>
                <tr>
					<td>100~120시간</td>
					<td>64,000원</td>
				</tr>
                <tr>
					<td>120~140시간</td>
					<td>68,000원</td>
				</tr>
                <tr>
					<td>140시간 이상</td>
					<td>70,000원</td>
				</tr>
			</tbody>

		</table>
	</div
    <?
    }
    ?>

    <?
    if($grade=='GOLD'){
    ?>
	<div class="payTable csPayTable gold">
		<table>
			<thead>
				<tr>
					<th>등급</th>
					<th>자격요건</th>
					<th>상담료</th>
				</tr>
			</thead>
			<tbody>
				<tr>
					<td rowspan="18">
						<img src="/app/assets/img/contents/ico-rank-gold.png" />골드
					</td>
				</tr>
				<tr>
					<td>0~10시간</td>
					<td>50,000원</td>
				</tr>
                <tr>
					<td>10~30시간</td>
					<td>54,000원</td>
				</tr>
				<tr>
					<td>30~40시간</td>
					<td>56,000원</td>
				</tr>
				<tr>
					<td>40~50시간</td>
					<td>58,000원</td>
				</tr>
				<tr>
					<td>50~60시간</td>
					<td>60,000원</td>
				</tr>
				<tr>
					<td>60~70시간</td>
					<td>62,000원</td>
				</tr>
				<tr>
					<td>70~80시간</td>
					<td>64,000원</td>
				</tr>
                <tr>
					<td>80~90시간</td>
					<td>66,000원</td>
				</tr>
                <tr>
					<td>90~100시간</td>
					<td>68,000원</td>
				</tr>
                <tr>
					<td>100~120시간</td>
					<td>72,000원</td>
				</tr>
                <tr>
					<td>120~140시간</td>
					<td>74,000원</td>
				</tr>
                <tr>
					<td>140~160시간</td>
					<td>76,000원</td>
				</tr>
                <tr>
					<td>160~180시간</td>
					<td>78,000원</td>
				</tr>
                <tr>
					<td>180~200시간</td>
					<td>80,000원</td>
				</tr>
                <tr>
					<td>200~250시간</td>
					<td>85,000원</td>
				</tr>
                <tr>
					<td>250~300시간</td>
					<td>90,000원</td>
				</tr>
                <tr>
					<td>300시간 이상</td>
					<td>100,000원</td>
				</tr>

			</tbody>

		</table>
	</div>
    <?
    }
    ?>
	<br>
	<div class="payTable csPayTable">
		<table>
			<thead>
				<tr>
					<th>등급</th>
					<th>자격요건</th>
					<th>상담료</th>
				</tr>
			</thead>
			<tbody>
				<tr>
					<td colspan="3">
						별도 협의 책정
					</td>
				</tr>
			</tbody>

		</table>
	</div>

</section>

<?php
require_once($_SERVER['DOCUMENT_ROOT']."/app/common/footer.php");
?>
