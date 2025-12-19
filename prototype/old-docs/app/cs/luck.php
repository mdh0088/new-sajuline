<?php
require_once($_SERVER['DOCUMENT_ROOT']."/app/common/header.php");
?>

<section id="csWrap" class="section">
	<!-- subTitBox -->
	<div class="subTitBox">
		<h3>사주/운세</h3>
	</div>
	<!--// subTitBox -->

<!-- tabWrap -->
		<div class="tabWrap">
			<div class="tabList">
				<ul>
					<li class="on">
						<button type="button" onclick="tabOpen(event, this, 'luck01');">상담가능</button>
					</li>
					<li>
						<button type="button" onclick="tabOpen(event, this, 'luck02')">상담중</button>
					</li>
					<li>
						<button type="button" onclick="tabOpen(event, this, 'luck03')">신규</button>
					</li>
				</ul>
			</div>
			<div id="cs_area" class="tabContWrap">

				<!-- luck01 -->
				<div id="luck01" class="tabContItem">
					<div class="csBox">
						<div class="flBox">
							<div class="ibox">
								<span class="cate">타로</span>
								<img src="/app/assets/img/dumy/dumy-people.png">
							</div>
							<div class="tbox">
								<p class="owner">
									<span>
										<img src="/app/assets/img/contents/ico-rank-gold.png">
										샤롯데
									</span>
									<span>114번</span>
								</p>
								<p class="desc">맑은 기운을 가진 애동제자</p>
								<p class="point flBox alC">
									<span>p</span>
									<em>1000</em>
								</p>

								<button type="button" class="csBtn ing">
									상담중
								</button>

								<button type="button" class="csBtn miss">
									부재중
								</button>

								<button type="button" class="csBtn play">
									상담하기
								</button>
							</div>
						</div>
					</div>
					<!-- notiBox -->
					<div class="notiBox">
						<ul>
							<li>
								<a href="#">
									<!-- <span>후기</span> -->
									<span class="noti">공지</span>
									<p>운명은 정해져 있다지만, 정작 매 순간순간 순간순간</p>
								</a>
							</li>
						</ul>
					</div>
					<!--// notiBox -->

					<!-- revToggle -->
					<div class="revToggle">
						<div class="toggleTop flBox alC jcFe">
							<button type="button" class="revToggleBtn flBox alC" onclick="revToggle();">
								<img src="/app/assets/img/contents/ico-rev-num.png">
								<p>후기<span>999+</span></p>
							</button>
						</div>
						<div class="toggleRow">
							<ul>
								<li>
									<a href="#">
										<p>
											<span>1</span>
											현실적이고 친절하세요. 카드로 이렇게 맞...
										</p>
										<span>abcde</span>
									</a>
								</li>
								<li>
									<a href="#">
										<p>
											<span>2</span>
											현실적이고 친절하세요. 카드로 이렇게 맞...
										</p>
										<span>abcde</span>
									</a>
								</li>
								<li>
									<a href="#">
										<p>
											<span>3</span>
											현실적이고 친절하세요. 카드로 이렇게 맞...
										</p>
										<span>abcde</span>
									</a>
								</li>
							</ul>
						</div>
					</div>
					<!--// revToggle -->
				</div>
				<!--// luck01 -->

				<!-- luck02 -->
				<div id="luck02" class="tabContItem">
					<div class="csBox">
						<div class="flBox">
							<div class="ibox">
								<span class="cate">타로</span>
								<img src="/app/assets/img/dumy/dumy-people.png">
							</div>
							<div class="tbox">
								<p class="owner">
									<span>
										<img src="/app/assets/img/contents/ico-rank-gold.png">
										샤롯데
									</span>
									<span>114번</span>
								</p>
								<p class="desc">맑은 기운을 가진 애동제자</p>
								<p class="point flBox alC">
									<span>p</span>
									<em>1000</em>
								</p>
								<button type="button" class="csBtn ing">
									상담중
								</button>

								<button type="button" class="csBtn miss">
									부재중
								</button>

								<button type="button" class="csBtn play">
									상담하기
								</button>
							</div>
						</div>
					</div>
					<!-- notiBox -->
					<div class="notiBox">
						<ul>
							<li>
								<a href="#">
									<!-- <span>후기</span> -->
									<span class="noti">공지</span>
									<p>운명은 정해져 있다지만, 정작 매 순간순간 순간순간</p>
								</a>
							</li>
						</ul>
					</div>
					<!--// notiBox -->

					<!-- revToggle -->
					<div class="revToggle">
						<div class="toggleTop flBox alC jcFe">
							<button type="button" class="revToggleBtn flBox alC" onclick="revToggle();">
								<img src="/app/assets/img/contents/ico-rev-num.png">
								<p>후기<span>999+</span></p>
							</button>
						</div>
						<div class="toggleRow">
							<ul>
								<li>
									<a href="#">
										<p>
											<span>1</span>
											현실적이고 친절하세요. 카드로 이렇게 맞...
										</p>
										<span>abcde</span>
									</a>
								</li>
								<li>
									<a href="#">
										<p>
											<span>2</span>
											현실적이고 친절하세요. 카드로 이렇게 맞...
										</p>
										<span>abcde</span>
									</a>
								</li>
								<li>
									<a href="#">
										<p>
											<span>3</span>
											현실적이고 친절하세요. 카드로 이렇게 맞...
										</p>
										<span>abcde</span>
									</a>
								</li>
							</ul>
						</div>
					</div>
					<!--// revToggle -->
				</div>
				<!--// luck02 -->
				<!-- luck03 -->
				<div id="luck03" class="tabContItem">
					<div class="csBox">
						<div class="flBox">
							<div class="ibox">
								<span class="cate">타로</span>
								<img src="/app/assets/img/dumy/dumy-people.png">
							</div>
							<div class="tbox">
								<p class="owner">
									<span>
										<img src="/app/assets/img/contents/ico-rank-gold.png">
										샤롯데
									</span>
									<span>114번</span>
								</p>
								<p class="desc">맑은 기운을 가진 애동제자</p>
								<p class="point flBox alC">
									<span>p</span>
									<em>1000</em>
								</p>

								<button type="button" class="csBtn ing">
									상담중
								</button>

								<button type="button" class="csBtn miss">
									부재중
								</button>

								<button type="button" class="csBtn play">
									상담하기
								</button>

							</div>
						</div>
					</div>
					<!-- notiBox -->
					<div class="notiBox">
						<ul>
							<li>
								<a href="#">
									<!-- <span>후기</span> -->
									<span class="noti">공지</span>
									<p>운명은 정해져 있다지만, 정작 매 순간순간 순간순간</p>
								</a>
							</li>
						</ul>
					</div>
					<!--// notiBox -->

					<!-- revToggle -->
					<div class="revToggle">
						<div class="toggleTop flBox alC jcFe">
							<button type="button" class="revToggleBtn flBox alC" onclick="revToggle();">
								<img src="/app/assets/img/contents/ico-rev-num.png">
								<p>후기<span>999+</span></p>
							</button>
						</div>
						<div class="toggleRow">
							<ul>
								<li>
									<a href="#">
										<p>
											<span>1</span>
											현실적이고 친절하세요. 카드로 이렇게 맞...
										</p>
										<span>abcde</span>
									</a>
								</li>
								<li>
									<a href="#">
										<p>
											<span>2</span>
											현실적이고 친절하세요. 카드로 이렇게 맞...
										</p>
										<span>abcde</span>
									</a>
								</li>
								<li>
									<a href="#">
										<p>
											<span>3</span>
											현실적이고 친절하세요. 카드로 이렇게 맞...
										</p>
										<span>abcde</span>
									</a>
								</li>
							</ul>
						</div>
					</div>
					<!--// revToggle -->
				</div>
				<!--// luck03 -->

			</div>
		</div>
		<!--// tabWrap -->
</section>

<?php
require_once($_SERVER['DOCUMENT_ROOT']."/app/common/footer.php");
?>
