<!DOCTYPE html>
<html lang="en">

<head>

    <meta charset="utf-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">
    <meta name="description" content="">
    <meta name="author" content="">

    <title>SB Admin 2 - Dashboard</title>

    <!-- Custom fonts for this template-->
    <link href="/app/admin/vendor/fontawesome-free/css/all.min.css" rel="stylesheet" type="text/css">
    <link
        href="https://fonts.googleapis.com/css?family=Nunito:200,200i,300,300i,400,400i,600,600i,700,700i,800,800i,900,900i"
        rel="stylesheet">

    <!-- Custom styles for this template-->
    <link href="/app/admin/css/sb-admin-2.min.css" rel="stylesheet">

    <!-- Custom styles for this page -->
    <link href="/app/admin/vendor/datatables/dataTables.bootstrap4.min.css" rel="stylesheet">

    <script src="/app/assets/js/jquery-3.4.1.min.js"></script>
    <script src="/app/assets/js/jquery-ui.js"></script>
    <script src="/app/assets/js/swiper.min.js"></script>
    <script src="/app/assets/js/common.js"></script>
    <script src="/app/assets/js/function.js"></script>
    <script src="/app/assets/js/config.js"></script>

    <script src="https://unpkg.com/axios/dist/axios.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/sweetalert2@11.4.10/dist/sweetalert2.min.js"></script>
    <script src="https://malsup.github.io/min/jquery.form.min.js"></script>


    <script src="/app/admin/vendor/jquery/jquery.min.js"></script>
    <script src="/app/admin/vendor/bootstrap/js/bootstrap.bundle.min.js"></script>

    <!-- Core plugin JavaScript-->
    <script src="/app/admin/vendor/jquery-easing/jquery.easing.min.js"></script>

    <!-- Custom scripts for all pages-->
    <script src="/app/admin/js/sb-admin-2.min.js"></script>

    <!-- Page level plugins -->
    <script src="/app/admin/vendor/chart.js/Chart.min.js"></script>
    <script src="/app/admin/vendor/datatables/jquery.dataTables.min.js"></script>
    <script src="/app/admin/vendor/datatables/dataTables.bootstrap4.min.js"></script>

    <!-- Page level custom scripts -->
    
</head>


<?php
session_start();
if (!isset($_SESSION['IDX'])  || $_SESSION['USER_STATUS']!=0){
    echo
    "
    <script>
        alert('접근이 불가능합니다.');
        location.href='/app/admin/login';
    </script>
    ";
}
?>







<body id="page-top">
