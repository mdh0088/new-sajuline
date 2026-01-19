<?php
require_once($_SERVER['DOCUMENT_ROOT']."/app/common/header.php");
?>

<script src="/app/assets/js/swiper.min.js"></script>
<script src="/app/assets/js/swiper-bundle.min.js"></script>
<link rel="stylesheet" href="/app/assets/js/swiper.min.css"></script>

<div id="detailTop" class="searchTop">
    <div class="inner">
        <div class="leftArea fN">
            <button type="button" class="btnBack" onclick="pageBack();">
                <img src="/app/assets/img/contents/ico-back-btn.png">
            </button>
            <div class="searchBox">
                <input type="text" id="search_name" title="검색어 입력" placeholder="검색어를 입력해주세요">
                <button type="button" class="btnSearch"></button>
            </div>
        </div>

    </div>
</div>


<section id="searchWrap" class="section">
    <div class="inner">

        <!-- srchBox -->
        <div class="srchBox">
            <div class="sbox searchHis">
                <div class="titBox fl alC jcSb">
                    <h3>최근검색어</h3>
                    <button type="button" onclick="delAll();">전체삭제</button>
                </div>
                <div class="hisBox" id="search_iist_target">
					<span class="search_list">
						<button type="button">무무문동</button>
						<button type="button" class="btnDel">삭제</button>
					</span>
                    <span class="search_list">
						<button type="button">무무문동</button>
						<button type="button" class="btnDel">삭제</button>
					</span>
                    <span class="search_list">
						<button type="button">무무문동</button>
						<button type="button" class="btnDel">삭제</button>
					</span>
                </div>
            </div>
        </div>
        <!--// srchBox -->

        <!-- srchBox -->
        <div class="srchBox">
            <div class="titBox">
                <div class="leftArea">
                    <h3>최근 상담사</h3>
                    <p>최근 상담사 목록입니다.</p>
                </div>
            </div>
            <div class="slideWrap full">
                <div class="swiper-container col-01">
                    <div class="swiper-wrapper">

                        <!-- swiper-slide -->
                        <div class="swiper-slide">
                            <a href="#">
                                <div class="csBox type1">
                                    <div class="ibox">
                                        <img src="/app/assets/img/dumy/dumy-people.png">
                                        <div class="tagBox">
                                            <span class="cate bg1">타로</span>
                                            <span class="cate bg2">신규</span>
                                        </div>
                                    </div>
                                    <div class="owner">
                                        <span>샤롯데</span>
                                        <span>114번</span>
                                    </div>
                                </div>
                            </a>
                        </div>
                        <!--// swiper-slide -->

                        <!-- swiper-slide -->
                        <div class="swiper-slide">
                            <a href="#">
                                <div class="csBox type1">
                                    <div class="ibox">
                                        <img src="/app/assets/img/dumy/dumy-people.png">
                                        <div class="tagBox">
                                            <span class="cate bg1">타로</span>
                                            <span class="cate bg2">신규</span>
                                        </div>
                                    </div>
                                    <div class="owner">
                                        <span>샤롯데</span>
                                        <span>114번</span>
                                    </div>
                                </div>
                            </a>
                        </div>
                        <!--// swiper-slide -->

                        <!-- swiper-slide -->
                        <div class="swiper-slide">
                            <a href="#">
                                <div class="csBox type1">
                                    <div class="ibox">
                                        <img src="/app/assets/img/dumy/dumy-people.png">
                                        <div class="tagBox">
                                            <span class="cate bg1">타로</span>
                                            <span class="cate bg2">신규</span>
                                        </div>
                                    </div>
                                    <div class="owner">
                                        <span>샤롯데</span>
                                        <span>114번</span>
                                    </div>
                                </div>
                            </a>
                        </div>
                        <!--// swiper-slide -->

                    </div>
                </div>
            </div>
        </div>
        <!--// srchBox -->


        <!--// srchBox -->

        <!-- srchBox -->
        <div class="srchBox">
            <div class="titBox">
                <div class="leftArea">
                    <h3>실시간 후기</h3>
                </div>
            </div>

            <div class="slideWrap">
                <div class="swiper-container dot row-01">
                    <div class="swiper-wrapper">

                        <!-- swiper-slide -->
                        <div class="swiper-slide">
                            <!-- csRevBox -->
                            <div class="csRevBox">
                                <div class="leftArea">
                                    <div class="iBox">
                                        <img src="/app/assets/img/dumy/dumy-people.png">
                                    </div>
                                    <div class="info">
                                        <span>샤롯데</span>
                                        <span>114번</span>
                                    </div>
                                </div>
                                <div class="rightArea">
                                    <div class="owner">
                                        <p>진오</p>
                                        <p>
                                            <span>2022.3.29</span>
                                            <button type="button" onclick="fn_layer('layer03', 320)">신고</button>
                                        </p>
                                    </div>
                                    <div class="tbox">
                                        요즘 많이 불안한 상태인데 제인샘이랑<br>
                                        상담 하구 나면 마음이 참 차분해 지네요~<br>
                                        상담 자주 못 드렸지만 선생님한테 늘<br>
                                        감사드려요♡
                                    </div>
                                </div>
                            </div>
                            <!--// csRevBox -->
                        </div>
                        <!--// swiper-slide -->

                        <!-- swiper-slide -->
                        <div class="swiper-slide">
                            <!-- csRevBox -->
                            <div class="csRevBox">
                                <div class="leftArea">
                                    <div class="iBox">
                                        <img src="/app/assets/img/dumy/dumy-people.png">
                                    </div>
                                    <div class="info">
                                        <span>샤롯데</span>
                                        <span>114번</span>
                                    </div>
                                </div>
                                <div class="rightArea">
                                    <div class="owner">
                                        <p>진오</p>
                                        <p>
                                            <span>2022.3.29</span>
                                            <button type="button" onclick="fn_layer('layer03', 320)">신고</button>
                                        </p>
                                    </div>
                                    <div class="tbox">
                                        요즘 많이 불안한 상태인데 제인샘이랑<br>
                                        상담 하구 나면 마음이 참 차분해 지네요~<br>
                                        상담 자주 못 드렸지만 선생님한테 늘<br>
                                        감사드려요♡
                                    </div>
                                </div>
                            </div>
                            <!--// csRevBox -->
                        </div>
                        <!--// swiper-slide -->

                        <!-- swiper-slide -->
                        <div class="swiper-slide">
                            <!-- csRevBox -->
                            <div class="csRevBox">
                                <div class="leftArea">
                                    <div class="iBox">
                                        <img src="/app/assets/img/dumy/dumy-people.png">
                                    </div>
                                    <div class="info">
                                        <span>샤롯데</span>
                                        <span>114번</span>
                                    </div>
                                </div>
                                <div class="rightArea">
                                    <div class="owner">
                                        <p>진오</p>
                                        <p>
                                            <span>2022.3.29</span>
                                            <button type="button" onclick="fn_layer('layer03', 320)">신고</button>
                                        </p>
                                    </div>
                                    <div class="tbox">
                                        요즘 많이 불안한 상태인데 제인샘이랑<br>
                                        상담 하구 나면 마음이 참 차분해 지네요~<br>
                                        상담 자주 못 드렸지만 선생님한테 늘<br>
                                        감사드려요♡
                                    </div>
                                </div>
                            </div>
                            <!--// csRevBox -->
                        </div>
                        <!--// swiper-slide -->

                    </div>
                    <div class="swiper-pagination"></div>
                </div>
            </div>

        </div>
        <!--// srchBox -->

        <!-- srchBox -->
        <div class="srchBox">
            <div class="titBox">
                <div class="leftArea">
                    <h3>인기 검색어</h3>
                </div>
            </div>
            <div class="srchList">
                <ul>
                    <li>
                        <button type="button">
                            <span>1</span>
                            <p>타로</p>
                        </button>
                    </li>
                    <li>
                        <button type="button">
                            <span>2</span>
                            <p>사주/운세</p>
                        </button>
                    </li>
                    <li>
                        <button type="button">
                            <span>3</span>
                            <p>샤롯데</p>
                        </button>
                    </li>
                    <li>
                        <button type="button">
                            <span>4</span>
                            <p>샤롯데</p>
                        </button>
                    </li>
                    <li>
                        <button type="button">
                            <span>5</span>
                            <p>샤롯데</p>
                        </button>
                    </li>
                    <li>
                        <button type="button">
                            <span>6</span>
                            <p>사주/운세</p>
                        </button>
                    </li>
                    <li>
                        <button type="button">
                            <span>7</span>
                            <p>샤롯데</p>
                        </button>
                    </li>
                    <li>
                        <button type="button">
                            <span>8</span>
                            <p>샤롯데</p>
                        </button>
                    </li>
                    <li>
                        <button type="button">
                            <span>9</span>
                            <p>샤롯데</p>
                        </button>
                    </li>
                    <li>
                        <button type="button">
                            <span>10</span>
                            <p>샤롯데</p>
                        </button>
                    </li>
                </uL>
            </div>
        </div>
        <!--// srchBox -->

        <!-- srchBox -->
        <div class="srchBox">
            <div class="titBox">
                <div class="leftArea">
                    <h3>검색결과</h3>
                </div>
            </div>

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

        </div>
        <!--// srchBox -->

        <!-- nodata -->
        <div class="nodata">
            <p>"타로" 검색 결과가 없습니다.</p>
        </div>
        <!--// nodata -->


    </div>
</section>

<style>
    .swiper-wrapper {height:auto !important;}
</style>
<script>
    // swiper
    function slideSwiper(){

        var $slideItem01 = $(".swiper-container.col-01"),
            $slideItem04 = $(".swiper-container.row-01");

        if(!$(".swiper-container").length > 0) return false;

        // col-01
        $slideItem01.each(function(i, el){
            var $this = $(this);
            $this.addClass('swiperCol01-' + i + 1);

            var swiper = new Swiper('.swiperCol01-' + i + 1, {
                observer: true,
                observeParents: true,
                slidesPerView : 2.3,
                spaceBetween: 15,
                autoHeight : true,
                breakpoints: {
                    470: {
                        slidesPerView : 1.4,
                    },
                },
                watchOverflow: true
            });
        });
        // row-01
        $slideItem04.each(function(i, el){
            var $this = $(this);
            $this.addClass('swiperRow01-' + i + 1);

            var swiper = new Swiper('.swiperRow01-' + i + 1, {
                observer: true,
                observeParents: true,
                slidesPerView : 1,
                spaceBetween: 15,
                autoHeight : true,
                breakpoints: {
                    470: {
                        slidesPerView :1,
                    },
                },
                watchOverflow: true,
                pagination : {
                    el : '.swiper-pagination',
                    clickable : true,
                },
            });
        });


    }
    $(window).on("load", function(){
        slideSwiper();
    })
</script>
<?php
require_once($_SERVER['DOCUMENT_ROOT']."/app/common/footer.php");
?>
