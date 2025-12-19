<?php
    $amount = $_GET['amount'];
    $charge_type = $_GET['charge_type'];
    echo
    "
        <script>
    
        if (navigator.maxTouchPoints){
            location.href='/app/charge/point_success?amt=$amount&charge_type=$charge_type';
        }else{
            window.parent.location.href='/app/charge/point_success?amt=$amount&charge_type=$charge_type';
        }
    
        </script>
    ";
?>

