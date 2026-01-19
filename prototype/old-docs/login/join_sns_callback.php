<?php
    $join_type = isset($_GET['join_type'])?$_GET['join_type']:'common';
?>
<script>
    //const isMobile =/iPhone|iPad|iPod|Android/i.test(navigator.userAgent);
    if (navigator.maxTouchPoints){
        location.href='../join/join.php?join_type=<?php echo $join_type?>';
    } else {
        window.opener.location.href='../common/join.php?join_type=<?php echo $join_type?>';
        window.close();
    }


    //window.opener.alert('pc');
</script>
