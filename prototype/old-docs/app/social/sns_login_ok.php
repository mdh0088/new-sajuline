<script>
    //const isMobile =/iPhone|iPad|iPod|Android/i.test(navigator.userAgent);
    alert('환영합니다.');
    if (navigator.maxTouchPoints){
        location.href='/';
    } else {
        window.opener.location.href='/';
        window.close();
    }


    //window.opener.alert('pc');
</script>


<html>
<head>
    <meta http-equiv="Content-Type" content="text/html; charset=UTF-8">
</head>
</html>
