document.addEventListener("DOMContentLoaded", () => {
    const body = document.querySelector('body');
    const header = document.getElementById('header');
    const gnb = document.getElementById("gnb");
    const lnb = document.getElementById("lnb");
    
	// SlideUp
    let slideUp = (target, duration=300) => {
        target.style.transitionProperty = 'height, margin, padding';
        target.style.transitionDuration = duration + 'ms';
        target.style.boxSizing = 'border-box';
        target.style.height = target.offsetHeight + 'px';
        // target.offsetHeight;
        target.style.overflow = 'hidden';
        target.style.height = 0;
        target.style.paddingTop = 0;
        target.style.paddingBottom = 0;
        target.style.marginTop = 0;
        target.style.marginBottom = 0;
        window.setTimeout( () => {
            target.style.display = 'none';
            target.style.removeProperty('height');
            target.style.removeProperty('padding-top');
            target.style.removeProperty('padding-bottom');
            target.style.removeProperty('margin-top');
            target.style.removeProperty('margin-bottom');
            target.style.removeProperty('overflow');
            target.style.removeProperty('transition-duration');
            target.style.removeProperty('transition-property');
            //alert("!");
        }, duration);
    }
    // SlideDown
    let slideDown = (target, duration=300) => {
        target.style.removeProperty('display');
        let display = window.getComputedStyle(target).display;
        if (display === 'none') display = 'block';
        target.style.display = display;
        let height = target.offsetHeight;
        target.style.overflow = 'hidden';
        target.style.height = 0;
        target.style.paddingTop = 0;
        target.style.paddingBottom = 0;
        target.style.marginTop = 0;
        target.style.marginBottom = 0;
        target.offsetHeight;
        target.style.boxSizing = 'border-box';
        target.style.transitionProperty = "height, margin, padding";
        target.style.transitionDuration = duration + 'ms';
        target.style.height = height + 'px';
        target.style.removeProperty('padding-top');
        target.style.removeProperty('padding-bottom');
        target.style.removeProperty('margin-top');
        target.style.removeProperty('margin-bottom');
        window.setTimeout( () => {
            target.style.removeProperty('height');
            target.style.removeProperty('overflow');
            target.style.removeProperty('transition-duration');
            target.style.removeProperty('transition-property');
        }, duration);
    }  


	// 태그 체크
	/*
	setTimeout(function(){
		let cate = document.querySelectorAll(".cate");
				console.log(cate);
		cate.forEach(el => {
		  let chk = el.textContent;
		  if (chk === "타로") {
			el.classList.add("bg3");
			el.parentElement.classList.add("bg3");
		  } else if (chk === "사주") {
			el.classList.add("bg2");
			el.parentElement.classList.add("bg2");
		  } else if (chk === "신규") {
			el.classList.add("bg4");
			el.parentElement.classList.add("bg4");
		  } else if (chk === "신점") {
			el.classList.add("bg5");
			el.parentElement.classList.add("bg5");
		  }else {
			el.classList.add("bg1");
		  }
		});		
	}, 700);*/

})

// 메타태그
window.addEventListener('load', function() {
	metaTitle();
	// metaDesc();
});

function metaTitle(){
  const _metaTitle = document.querySelectorAll('.subTitBox h3').length; 
  
  if (_metaTitle > 0) {
	const _title = document.querySelector('.subTitBox h3').textContent;	
    document.title = `${_title} | 사주로`; 
  } else {
    return false;
  }	
}
/*
function metaDesc(){
	const _metaKeyDesc = document.querySelectorAll('.subTitBox .desc').length;
	if(_metaKeyDesc > 0){
		const _val = document.querySelectorAll('.subTitBox .desc').innerText;
		document.getElementsByTagName('meta').namedItem('description').setAttribute('content', = _val); 
			console.log(_val);
	}else{
		return false;
	}
	console.log(_metaKeyDesc);
}
*/


// 메인 후기 토글
function revToggle(el){
	let $target = el.parentElement;
	$target.classList.toggle("on");
}

// 즐찾  토글
function favToggle(el){	
	el.classList.toggle("on");
}

// toggle button
function toggleBtn(el){
	let $target = el.nextElementSibling;
	el.classList.toggle("on");
	$target.classList.toggle("on");
}

// TAB 공통
function tabOpen(e, target, tabName){  
    e.preventDefault();

    let i, tabList, tabCont, tabWrap;
    tabWrap = target.closest(".tabWrap");
    
    
    tabList = tabWrap.querySelectorAll(".tabList > ul > li");
    tabCont = tabWrap.querySelectorAll(".tabContWrap > div");
    
    for(i = 0; i < tabList.length; i++){ 
        tabList[i].classList.remove("on");
    }
    for(i = 0; i < tabCont.length; i++){ 
        tabCont[i].style.display = "none";
    }

    target.parentNode.classList.add("on");
    document.getElementById(tabName).style.display = "block";
    
    
}

// PopupOpen
function fn_layer(el, s, h){
    const thisPop = document.querySelector("#" + el);
    thisPop.style.display = "block";            
    //thisPop.querySelector(".inner").style.width = s + "px";
    //thisPop.querySelector(".inner").style.height = h + "px";
}

// popupClose
function fn_layer_close(el){
    document.querySelector("#" + el).style.display = "none";
}

// page back
function pageBack(){
	window.history.back();
}

function footerInfoToggle(_this){
	_this.classList.toggle("on");
	let footerInfo = document.querySelectorAll(".footerInfo");
	footerInfo.forEach(_target => {
		_target.classList.toggle("on");
	})
}


const showCallPop = async (cs_idx) => {

    let csObj = {
            IDX : cs_idx
    };
    try {
        let param = JSON.stringify(csObj);
        let data = new FormData();
        data.append("csObj", param);
        let result = await axios.post('/api/cs/read_call_info', data);

        console.log(result);
        if (result.data.isSuc) {
            fn_layer('csApplicationPop');
            document.querySelector('#csApplicationPop').innerHTML=result.data.csObj.cont;
        } else {
            alert('일반 이용자만 이용가능합니다.');
        }

    } catch (err) {
        console.log("Error >>", err);
    }
}


const callByPoint = async (code,id) => {

    let callObj = {
        CODE : code,
        ID : id
    };
    try {
        let param = JSON.stringify(callObj);
        let data = new FormData();
        data.append("callObj", param);
        let result = await axios.post('/api/cs/call_by_point', data);

        console.log(result);
        if (result.data.isSuc) {
            location.href='tel:02-6209-0808';
        } else {

        }

    } catch (err) {
        console.log("Error >>", err);
    }
}
