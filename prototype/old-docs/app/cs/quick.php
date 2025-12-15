<?php
require_once($_SERVER['DOCUMENT_ROOT']."/app/common/header.php");
?>

<script>

    document.addEventListener('DOMContentLoaded', () => {
        getQuickCS();
    })

    const getQuickCS = async () => {
        showLoading();
        let searchObj =
            {

            };
        try {
            let param = JSON.stringify(searchObj);
            let data = new FormData();
            data.append("searchObj", param);
            let result = await axios.post('/api/cs/read_quick', data);
            console.log(result);
            let inner = '';
            if (result.data.isSuc) {
                let review_list = result.data.list;
                if (review_list.length > 0 ){
                    review_list.forEach((item) => {
                        inner +='<div class="fcBox">';
                        inner +='    <div class="csBox type1">';

						if (item.TYPE == '타로') {
							inner +='        <div class="ibox" onclick="Javascript:location.href=\'/app/cs/cs_detail?idx='+item.IDX+'\' ">';
						}else if (item.TYPE == '사주')
						{
							inner +='        <div class="ibox bg2" onclick="Javascript:location.href=\'/app/cs/cs_detail?idx='+item.IDX+'\' ">';
						}else if (item.TYPE == '신점')
						{
							inner +='        <div class="ibox bg5" onclick="Javascript:location.href=\'/app/cs/cs_detail?idx='+item.IDX+'\' ">';
						}


                        inner +='             <img src="/app/assets/upload/cs/'+item.IMG+'">';
                        inner +='                <div class="tagBox">';

						if (item.TYPE == '타로') {
							inner +='                   <span class="cate">'+item.TYPE+'</span>';
						}else if (item.TYPE == '사주')
						{
							inner +='                   <span class="cate bg2">'+item.TYPE+'</span>';
						}else if (item.TYPE == '신점')
						{
							inner +='                   <span class="cate bg5">'+item.TYPE+'</span>';
						}


                        if (item.CHK_NEW == '신규') {
                            inner +='                   <span class="cate bg4">'+item.CHK_NEW+'</span>';
                        }
                        inner +='               </div>';
                        inner +='       </div>';
                        inner +='       <div class="owner" onclick="Javascript:location.href=\'/app/cs/cs_detail?idx='+item.IDX+'\' ">';
						inner +='			<img class="rank" src="/app/assets/img/contents/ico-rank-'+item.GRADE.toLowerCase()+'.png">';
                        inner +='           <span>'+item.NICK_NAME+'</span>';
                        inner +='           <span>'+item.CODE+'번</span>';
                        inner +='       </div>';
                        inner +='       <p class="point flBox jcC alC">';
                        inner +='           <span>p</span>';
                        inner +='           <em>'+item.AFTER_AMOUNT+'</em>';
                        inner +='       </p>';

                        if (item.STATUS == 1){
                            inner += '                <button type="button" class="csBtn play" onclick="showCallPop('+item.IDX+')">';
                            inner += '                    상담하기';
                            inner += '                </button>';
                        } else if(item.STATUS == 2){
                            inner += '                <button type="button" class="csBtn ing" onclick="showAlarm(\''+item.IDX+'\',\''+item.TYPE+'\',\''+item.NICK_NAME+'\',\''+item.CODE+'\',\''+item.STATUS+'\',\''+item.IMG+'\')">';
                            inner += '                    상담중';
                            inner += '                </button>';
                        } else {
                            inner += '                <button type="button" class="csBtn miss" onclick="showAlarm(\''+item.IDX+'\',\''+item.TYPE+'\',\''+item.NICK_NAME+'\',\''+item.CODE+'\',\''+item.STATUS+'\',\''+item.IMG+'\')">';
                            inner += '                    부재중';
                            inner += '                </button>';
                        }


                        inner +='   </div>';
                        inner +='</div>';
                    });
                }
            } else {

            }
            document.querySelector('#quick_area').innerHTML=inner;
            hideLoading();
        } catch (err) {
            console.log("Error >>", err);
        }
    }

</script>

<section id="csWrap" class="section fast">
	<!-- subTitBox -->
	<div class="subTitBox">
		<h3>빠른상담</h3>
		<button type="button" class="icoBtn icoRefresh" onclick="getQuickCS();">새로고침</button>
	</div>
	<!--// subTitBox -->

	<div id="quick_area" class="fcWrap">



	</div>
</section>

<script src="/app/assets/js/setMeta.js"></script>
<script>
    setMeta({
        title: '빠른상담',
        description:
            '빠른상담 : 사주로의 인기상담사를 한눈에! 남들보다 빠르게 인기상담사와 상담하세요',
        url: 'https://sajutarot.com/app/cs/quick',
        keyword: ''
    });
</script>

<?php
require_once($_SERVER['DOCUMENT_ROOT']."/app/common/footer.php");
?>
