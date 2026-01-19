<script>
    alert('결제를 취소하셨습니다.');
    if (navigator.maxTouchPoints){
        location.href='/app/charge/point';
    }else{
        window.parent.location.href='/app/charge/point';
    }

</script>

<html>
<head>
    <meta http-equiv="Content-Type" content="text/html; charset=UTF-8">
</head>
</html>
