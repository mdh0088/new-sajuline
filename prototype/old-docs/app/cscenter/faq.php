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
				<li>
					<button type="button" onclick="window.location.href='/app/cscenter/notice'">공지사항</button>
				</li>
				<li class="on">
					<button type="button">FAQ</button>
				</li>
				<li>
					<button type="button" onclick="window.location.href='/app/cscenter/inquiry'">1:1문의</button>
				</li>
			</ul>
		</div>

		<div class="faqWrap">

			<div class="faqBox">
				<div class="q" onclick="toggleBtn(this)">
					<strong>Q. 사주로는 어떤곳인가요?</strong>
				</div>
				<div class="a">
					A. 사주로는 피플라인에서 운영하고 있는 타로, 운세, 사주상담을 선불제, 후불제를 선택해서<br>
                    편하게 전화상담을 받을 수 있는 1:1전화상담 서비스입니다.<br>
                    항상 고객님의 편의를 위해 노력하는 사주로가 되겠습니다.
				</div>
			</div>

			<div class="faqBox">
				<div class="q" onclick="toggleBtn(this)">
					<strong>Q. 060 후불제 1:1전화 상담안내</strong>
				</div>
				<div class="a">
                    A. 060 후불 전화 상담은 후불제로 전화 상담을 하는 것이며,<br>
                    이용 요금은 당월 전화요금에 정보 이용료로 부과되어 함께 청구됩니다.<br>

                    1. 원하시는 상담사 프로필에서 [상담하기]-[후불로 상담 이용하기]-[☎060상담하기]를 눌러주세요<br>
                    2. 원하시는 상담사의 고유번호 3자리를 입력하여 전화 연결을 하실 수 있습니다. <br>
                    *상담사별 060번호/요금이 다릅니다.*
				</div>
			</div>

			<div class="faqBox">
				<div class="q" onclick="toggleBtn(this)">
					<strong>Q. 포인트 선불제 1;1전화 상담안내</strong>
				</div>
				<div class="a">
                    A. 포인트 전화상담은 상담을 위해 포인트를 선불로 구매 후 해당 포인트를 이용하여 전화상담을 하는 서비스입니다.<br>
                    포인트 전화상담은 최소 10,000포인트 이상 보유 시 상담이 가능합니다.<br><br>

                    (포인트 구매방법)
                    1.홈페이지 하단 [충전]메뉴에서 포인트를 충전해주세요.<br>

                    (포인트 상담방법)
                    1. 포인트 구매 후 원하시는 상담사 프로필에서 [☎포인트상담하기]를 눌러주세요
                    2. 원하시는 상담사의 고유번호 3자리를 입력하여 전화 연결을 하실 수 있습니다.
                    ※ 이용 요금은 상담사가 설정한 상담 가격으로 진행됩니다. (30초당 800포인트부터 ~)<br><br>

                    (상담 중 포인트 연장안내)
                    상담중에 포인트 연장이 필요하신 분은 종료 3분전에 포인트 구매하여 연장이 가능합니다.
                    잔여포인트는 상담 전 마이페이지 및 상담연결 시 안내되오니 참고 부탁드립니다.
				</div>
			</div>
			<div class="faqBox">
				<div class="q" onclick="toggleBtn(this)">
					<strong>Q. 사주로 회원혜택 안내</strong>
				</div>
				<div class="a">
                    A. 사주로 회원으로 신규가입하시면 포인트상담을 이용하실 수 있는 [10,000포인트]를 지급해드립니다.<br>
                    ※최초 1회에 한해 지급 되는 점 참고 부탁드립니다.<br>
                    -각종 이벤트에 참여가 가능합니다.<br>
                    -상담후기 작성이 가능합니다.
				</div>
			</div>
            <div class="faqBox">
				<div class="q" onclick="toggleBtn(this)">
					<strong>Q. 사주로 회원가입 안내</strong>
				</div>
				<div class="a">
                    A. 060 후불 전화 상담은 별도의 회원가입 없이 이용할 수 있습니다.<br>
                    단, 060 후불 전화 상담은 후기 작성이 불가하오니 이 점 참고 부탁드립니다.<br>
                    포인트 선불상담은 회원 가입 후 이용 가능합니다.
				</div>
			</div>
            <div class="faqBox">
				<div class="q" onclick="toggleBtn(this)">
					<strong>Q. 사주로 후기작성 안내</strong>
				</div>
				<div class="a">
                    A. 상담 후기는 [포인트상담]을 통해 상담을 이용 하신 분들만 작성이 가능하며,<br>
                    상담사 프로필의 [상담후기]-[후기작성하기]에서 작성이 가능합니다.<br>
                    작성된 후기에 대한 답글은 해당 상담사만 작성이 가능합니다.
				</div>
			</div>
            <div class="faqBox">
				<div class="q" onclick="toggleBtn(this)">
					<strong>Q. 사주로 상담문의 안내</strong>
				</div>
				<div class="a">
                    A. 상담 문의는 로그인 하신 분들만 작성이 가능하며,<br>
                    해당 상담사 프로필의 [상담 문의]에서 작성이 가능합니다.<br>
                    상담 가능 시간 등의 문의사항을 남기는 1:1게시판입니다.<br>
                    모든글은 비밀글로 작성되어 고객님/상담사만 확인 가능합니다.
				</div>
			</div>
            <div class="faqBox">
				<div class="q" onclick="toggleBtn(this)">
					<strong>Q. 사주로 빠른상담 안내</strong>
				</div>
				<div class="a">
                    A. 사주로 빠른상담은 원하시는 상담사를 한눈에 보며<br>
                    빠르게 상담을 요청하실 수 있는 페이지 입니다.<br>
                    빠른상담에는 현재 상담이 가능하신 상담사 분들만 랜덤노출됩니다.
				</div>
			</div>
            <div class="faqBox">
				<div class="q" onclick="toggleBtn(this)">
					<strong>Q. 사주로 검색시스템 안내</strong>
				</div>
				<div class="a">
                    A. 사주로 검색 시스템은 원하시는 상담사정보/후기 등을 검색하실 수 있습니다.<br>
                    금주의 인기 검색어는 전주(월요일~일요일)의 데이터에 따라 선정됩니다.
				</div>
			</div>
            <div class="faqBox">
				<div class="q" onclick="toggleBtn(this)">
					<strong>Q. 사주로 사용내역 확인 안내</strong>
				</div>
				<div class="a">
                    A. 상담 내역은 [마이페이지] - [상담내역]에서 확인 가능합니다.
				</div>
			</div>
            <div class="faqBox">
				<div class="q" onclick="toggleBtn(this)">
					<strong>Q. 사주로 잔여포인트 부족하다고 나옵니다.어떻게 해야 하나요?</strong>
				</div>
				<div class="a">
                    A. 잔여포인트는 상담 전 마이페이지에서 확인 가능하며<br>
                    포인트상담 연결 시 안내됩니다.<br>
                    ※포인트 전화상담은 최소 10,000포인트 이상 보유 시 상담이 가능합니다.<br><br>
                    또한 [마이페이지]/[포인트 결제내역]에 충분하게 포인트가 있음에도
                    사용가능한 포인트가 없다면 [마이페이지]에 등록된 휴대폰 번호와
                    상담을 시도하는 휴대폰 번호가 일치한지 확인 부탁드립니다.<br><br>

                    사주로의 아이디 및 포인트는 휴대폰 번호와 연동되어 있음으로,<br>
                    번호 변경 시 꼭 [고객센터] - [1:1문의] 게시판을 통하여 문의주시길 바랍니다.
				</div>
			</div>
            <div class="faqBox">
				<div class="q" onclick="toggleBtn(this)">
					<strong>Q. 사주로 정보변경 안내</strong>
				</div>
				<div class="a">
                    A. [고객센터] - [1:1문의] 게시판을 통하여 문의해주세요.<br>
                    사주로의 아이디 및 포인트는 휴대폰 번호와 연동되어 있음으로,<br>
                    번호 변경 시 꼭 문의주시길 바랍니다.<br><br>

                    또한, [1:1문의] 신청 시 변경전 연락처와 변경후 연락처를 함께 남겨주시면<br>
                    좀 더 신속하게 처리가 가능합니다.
				</div>
			</div>
            <div class="faqBox">
				<div class="q" onclick="toggleBtn(this)">
					<strong>Q. 사주로 회원가입 연령 안내</strong>
				</div>
				<div class="a">
                    A. 사주로 회원가입 및 이용가능한 연령은 만19세 이상입니다.
				</div>
			</div>

            <div class="faqBox">
				<div class="q" onclick="toggleBtn(this)">
					<strong>Q. 사주로 회원탈퇴 안내</strong>
				</div>
				<div class="a">
                    A. 회원탈퇴는 [마이페이지]에서 가능합니다.<br>
                    단,탈퇴 후 동일 번호는 재가입이 불가능합니다.
				</div>
			</div>
            <div class="faqBox">
				<div class="q" onclick="toggleBtn(this)">
					<strong>Q. 사주로 포인트 환불 안내</strong>
				</div>
				<div class="a">
                    A. 구매한 포인트를 사용하지 않았을 경우,<br>
                    구매일로부터 7일 이내에는 결제 금액 100% 환불이 가능합니다.<br>
                    단, 구매일로부터 7일이 지난 이후에는 결제금액의 10%를<br>
                    환불수수료로 공제한 후 환불됩니다.<br>
                    ※ 구매한 포인트를 사용한 경우에는 환불이 불가합니다.<br>
                    ※ 이벤트로 지급받은 포인트는 환불이 불가능합니다.<br>
                    포인트 환불 신청은 [고객센터] - [1:1문의] 게시판 혹은 고객센터로 신청해주시면 가능합니다.
				</div>
			</div>
            <div class="faqBox">
				<div class="q" onclick="toggleBtn(this)">
					<strong>Q. 사주로 해외이용 안내</strong>
				</div>
				<div class="a">
					A. 해외 직통(외국 현지 번호) 전화번호는 지원하지 않아 불가능한 상태입니다.<br>
                    다만, 이용 중인 통신사 "로밍 서비스" 신청 시 사주로 상담 이용이 가능하며<br>
                    모든 요금은 로밍 서비스 신청자 부담인 점 참고 부탁드립니다.<br>
                    문의사항은 고객센터 또는 1:1문의를 통해 말씀해 주시면 감사하겠습니다.
				</div>
			</div>
            <div class="faqBox">
				<div class="q" onclick="toggleBtn(this)">
					<strong>Q. 사주로 불편신고</strong>
				</div>
				<div class="a">
					A. <개인정보><br>
                    저희 사주로는 정책상 상담사와의 개인정보 교환을 일체 금하고 있습니다.<br>
                    혹여나, 개인정보를 요구하거나 전달하는 상담사가 있다면 <br>
                    녹음파일과 함께 [고객센터] - [1:1문의]를 남겨주시면 보상하도록 하겠습니다.<br><br>
                    <상담><br>
                    상담중에 불편사항 및 기타 제안이 있으시다면<br>
                    [고객센터] - [1:1문의]를 남겨주시기 바랍니다.<br>
                    단,근거없는 내용,사생활 침해 사항은 처리되지 않습니다.
				</div>
			</div>
		</div>

	</div>
</section>


<script src="/app/assets/js/setMeta.js"></script>
<script>
    setMeta({
        title: '자주묻는질문',
        description:
            '자주묻는질문 : 회원혜택, 상담방법, 포인트사용, 상담사정보까지 궁금한 점을 확인해보세요.',
        url: 'https://sajutarot.com/app/cscenter/faq',
        keyword: ''
    });
</script>

<?php
require_once($_SERVER['DOCUMENT_ROOT']."/app/common/footer.php");
?>
