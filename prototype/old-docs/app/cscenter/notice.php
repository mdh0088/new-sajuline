<?php
require_once($_SERVER['DOCUMENT_ROOT']."/app/common/header.php");
?>

<section id="csCenterWrap" class="section">

	<div class="topBox">

		<strong>사주로 고객센터</strong>
		<p class="call">02.6212.0465</p>
		<p class="info1">
			카카오톡 : tarob  I 이메일 : tarotb@naver.com
		</p>
		<p class="info2">
			업무시간 : 09:00~17:00<br>
			점심시간 : 12:00~13:00<br>
			주말 및 공휴일 휴무
		</p>

	</div>



	<div class="tabWrap">

		<div class="tabList">
			<ul>
				<li class="on">
					<button type="button">공지사항</button>
				</li>
				<li>
					<button type="button" onclick="window.location.href='/app/cscenter/faq'">FAQ</button>
				</li>
				<li>
					<button type="button" onclick="window.location.href='/app/cscenter/inquiry'">1:1문의</button>
				</li>
			</ul>
		</div>

		<div class="noticeTable">
			<table>
				<tbody>
					<tr>
						<td>
							<a href="/app/cscenter/notice_view">
								<strong>[안내] 오픈이벤트 1</strong>
								<p>2023. 3. 22</p>
							</a>
						</td>
					</tr>
					<tr>
						<td>
							<a href="/app/cscenter/notice_view2">
								<strong>[안내] 오픈이벤트 2</strong>
								<p>2023. 3. 22</p>
							</a>
						</td>
					</tr>
					<tr>
						<td>
							<a href="/app/cscenter/notice_view3">
								<strong>[안내] 오픈이벤트 3</strong>
								<p>2023. 3. 22</p>
							</a>
						</td>
					</tr>
				</tbody>
			</table>
		</div>

	</div>
</section>
<script src="/app/assets/js/setMeta.js"></script>
<script>
    setMeta({
        title: '사주로 고객센터',
        description:
            '사주로 고객센터 : 이용에 궁금한 점, 불폄함을 겪고 계시다면? 1:1문의 또는 02-6212-4650 전화주세요.(평일 09-18시)',
        url: 'https://sajutarot.com/app/cscenter/notice',
        keyword: ''
    });
</script>
<?php
require_once($_SERVER['DOCUMENT_ROOT']."/app/common/footer.php");
?>
