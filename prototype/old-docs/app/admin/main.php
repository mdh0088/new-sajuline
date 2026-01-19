
<?php
require_once($_SERVER['DOCUMENT_ROOT']."/app/admin/common/top.php");
?>

<style>

    .modal {
        display: none;
        position: fixed;
        z-index: 1;
        padding-top: 100px;
        left: 0;
        top: 0;
        width: 100%;
        height: 100%;
        overflow: auto;
        background-color: rgb(0,0,0);
        background-color: rgba(0,0,0,0.4);
        overflow-y: auto;
        z-index: 9999;
    }

    .modal-content {
        background-color: #fefefe;
        margin: auto;
        padding: 20px;
        border: 1px solid #888;
        width: 80%;
    }

    /* PC 환경 */
    .img-responsive {
        width: 200px;
        height: 200px;
    }

    /* 모바일 환경 (480px 이하) */
    @media screen and (max-width: 480px) {
        .img-responsive {
            width: 50%;
            height: auto;
        }
    }

    .close {
        color: #aaaaaa;
        float: right;
        font-size: 28px;
        font-weight: bold;
    }

    .close:hover, .close:focus {
        color: #000;
        text-decoration: none;
        cursor: pointer;
    }
</style>

<script>

    var modal, span, modalText;
    document.addEventListener('DOMContentLoaded', () => {

        var currentDate = new Date();


        document.querySelector('#month_value').value = currentDate.getMonth() + 1;
        document.querySelector('#year_value').value = currentDate.getFullYear();

        getDailyTradeInfo();
        getTradeInfo('day');
        getCsAccessInfo();



        modal = document.getElementById("myModal");
        span = document.getElementsByClassName("close")[0];
        modalText = document.getElementById("modalText");

        span.onclick = function() {
            modal.style.display = "none";
        }

        window.onclick = function(event) {
            if (event.target == modal) {
                modal.style.display = "none";
            }
        }

    })


    const getCsAccessInfo = () => {

        let csObj =
            {
                // SEARCH_NAME		  : document.querySelector('#seaarch_name').value
                SEARCH_NAME		  : "test"
            };


        try {
            let param = JSON.stringify(csObj);
            let data = new FormData();
            data.append("csObj", param);
            axios.post('/api/admin/cs/read_cs_access_info', data)
                .then((result) => {
                    console.log(result);
                    if (result.data.isSuc) {

                        let cs_access_running = []; //2
                        let cs_access_wait = []; //1
                        let cs_access_out = []; //3

                        result.data.list.forEach(item => {
                            if (item.STATUS == 1){
                                cs_access_wait.push(item);
                            } else if (item.STATUS == 2){
                                cs_access_running.push(item);
                            } else {
                                cs_access_out.push(item);
                            }
                        });

                        let ctx = document.getElementById("myPieChart");
                        let myPieChart = new Chart(ctx, {
                            type: 'doughnut',
                            data: {
                                labels: ["상담중", "대기중", "부재중"],
                                datasets: [{
                                    data: [cs_access_running.length, cs_access_wait.length, cs_access_out.length],
                                    cs_data: [cs_access_running, cs_access_wait, cs_access_out],
                                    backgroundColor: ['#4e73df', '#1cc88a', '#36b9cc'],
                                    hoverBackgroundColor: ['#2e59d9', '#17a673', '#2c9faf'],
                                    hoverBorderColor: "rgba(234, 236, 244, 1)",
                                }],
                            },
                            options: {
                                maintainAspectRatio: false,
                                tooltips: {
                                    backgroundColor: "rgb(255,255,255)",
                                    bodyFontColor: "#858796",
                                    borderColor: '#dddfeb',
                                    borderWidth: 1,
                                    xPadding: 15,
                                    yPadding: 15,
                                    displayColors: false,
                                    caretPadding: 10,
                                },
                                legend: {
                                    display: false
                                },
                                cutoutPercentage: 80,
                                onClick: function(event, array) {


                                    if (array[0]) {
                                        var chartData = array[0]['_chart'].data;
                                        var idx = array[0]['_index'];
                                        var csData = chartData.datasets[0].cs_data[idx];

                                        var table = document.createElement('table');
                                        table.classList.add('table', 'table-striped'); // Bootstrap table classes
                                        table.innerHTML = '<thead><tr><th scope="col">NO</th><th scope="col">NICK_NAME</th><th scope="col">IMG</th></tr></thead><tbody></tbody>';


                                        csData.forEach(function(item, index) {
                                            var tr = document.createElement('tr');

                                            var noTd = document.createElement('td');
                                            noTd.textContent = index + 1;
                                            tr.appendChild(noTd);

                                            var nameTd = document.createElement('td');
                                            nameTd.textContent = item.NICK_NAME;
                                            tr.appendChild(nameTd);

                                            var imgTd = document.createElement('td');
                                            var img = document.createElement('img');
                                            img.src = "/app/assets/upload/cs/" + item.IMG;
                                            img.className = "img-responsive";
                                            imgTd.appendChild(img);
                                            tr.appendChild(imgTd);

                                            table.appendChild(tr);
                                        });

                                        modalText.innerHTML = '';
                                        modalText.appendChild(table);
                                        modal.style.display = "block";
                                    }
                                }
                            },
                        });
                    } else {
                    }
                })
        } catch (err) {
            console.log("Error >>", err);
        }
    }




    const getDailyTradeInfo = () => {

        let csObj =
            {
                // SEARCH_NAME		  : document.querySelector('#seaarch_name').value
                SEARCH_NAME		  : "test"
            };


        try {
            let param = JSON.stringify(csObj);
            let data = new FormData();
            data.append("csObj", param);
            axios.post('/api/admin/trade/read_daily_trade_info', data)
                .then((result) => {
                    console.log(result);
                    if (result.data.isSuc) {

                        let trade_info = '';
                        result.data.list.forEach(item => {
                            trade_info = item.Sales+'원';
                            if (item.SalesType == 'DAILY'){
                                document.querySelector('#day_trade_info').innerHTML = trade_info;
                            } else if (item.SalesType == 'MONTHLY'){
                                document.querySelector('#month_trade_info').innerHTML = trade_info;
                            } else {
                                document.querySelector('#year_trade_info').innerHTML = trade_info;
                            }
                        });


                    } else {
                    }
                })
        } catch (err) {
            console.log("Error >>", err);
        }
    }


    var myLineChart;
    const getTradeInfo = (type) => {

        document.querySelector('#myAreaChart').empty;


        let month_value = document.querySelector('#month_value').value;
        let year_value = document.querySelector('#year_value').value;

        if (type == 'day' && (month_value == 0 || month_value == '')){
            alert('검색할 월(MONTH)를 입력해주세요.');
            return;
        }
        if (type == 'month' && (year_value == 0 || year_value == '')){
            alert('검색할 연도(YEAR)를 입력해주세요.');
            return;
        }

        let tradeObj =
            {
                TYPE : type,
                MONTH_VALUE : month_value,
                YEAR_VALUE : year_value
            };

        try {
            let param = JSON.stringify(tradeObj);
            let data = new FormData();
            data.append("tradeObj", param);
            axios.post('/api/admin/trade/read_trade_info', data)
                .then((result) => {
                    console.log('testttttttt>>>',result);
                    if (result.data.isSuc) {


                        var ctx = document.getElementById("myAreaChart");
                        // 기존 차트가 존재한다면 제거
                        if (myLineChart) {
                            myLineChart.destroy();
                        }
                        let target_labels = [];
                        let target_data = [];
                        result.data.list.forEach(item => {
                            target_labels.push(item.SEARCH_TYPE+'일');
                            target_data.push(item.Sales);
                        });


                        let test_labels = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12","13"];
                        let test_data = [0, 10000, 5000, 15000, 10000, 20000, 15000, 25000, 20000, 30000, 25000, 40000,40000];

                        myLineChart = new Chart(ctx, {
                            type: 'line',
                            data: {
                                labels: target_labels,
                                datasets: [{
                                    label: "Earnings",
                                    lineTension: 0.3,
                                    backgroundColor: "rgba(78, 115, 223, 0.05)",
                                    borderColor: "rgba(78, 115, 223, 1)",
                                    pointRadius: 3,
                                    pointBackgroundColor: "rgba(78, 115, 223, 1)",
                                    pointBorderColor: "rgba(78, 115, 223, 1)",
                                    pointHoverRadius: 3,
                                    pointHoverBackgroundColor: "rgba(78, 115, 223, 1)",
                                    pointHoverBorderColor: "rgba(78, 115, 223, 1)",
                                    pointHitRadius: 10,
                                    pointBorderWidth: 2,
                                    data: target_data,
                                }],
                            },
                            options: {
                                maintainAspectRatio: false,
                                layout: {
                                    padding: {
                                        left: 10,
                                        right: 25,
                                        top: 25,
                                        bottom: 0
                                    }
                                },
                                scales: {
                                    xAxes: [{
                                        time: {
                                            unit: 'date'
                                        },
                                        gridLines: {
                                            display: false,
                                            drawBorder: false
                                        },
                                        ticks: {
                                            maxTicksLimit: 7
                                        }
                                    }],
                                    yAxes: [{
                                        ticks: {
                                            maxTicksLimit: 5,
                                            padding: 10,
                                            // Include a dollar sign in the ticks
                                            callback: function(value, index, values) {
                                                return number_format(value)+'원';
                                            }
                                        },
                                        gridLines: {
                                            color: "rgb(234, 236, 244)",
                                            zeroLineColor: "rgb(234, 236, 244)",
                                            drawBorder: false,
                                            borderDash: [2],
                                            zeroLineBorderDash: [2]
                                        }
                                    }],
                                },
                                legend: {
                                    display: false
                                },
                                tooltips: {
                                    backgroundColor: "rgb(255,255,255)",
                                    bodyFontColor: "#858796",
                                    titleMarginBottom: 10,
                                    titleFontColor: '#6e707e',
                                    titleFontSize: 14,
                                    borderColor: '#dddfeb',
                                    borderWidth: 1,
                                    xPadding: 15,
                                    yPadding: 15,
                                    displayColors: false,
                                    intersect: false,
                                    mode: 'index',
                                    caretPadding: 10,
                                    callbacks: {
                                        label: function(tooltipItem, chart) {
                                            var datasetLabel = chart.datasets[tooltipItem.datasetIndex].label || '';
                                            return number_format(tooltipItem.yLabel)+'원';
                                        }
                                    }
                                }
                            }
                        });

                    } else {
                    }
                })
        } catch (err) {
            console.log("Error >>", err);
        }
    }



    function number_format(number, decimals, dec_point, thousands_sep) {
        // *     example: number_format(1234.56, 2, ',', ' ');
        // *     return: '1 234,56'
        number = (number + '').replace(',', '').replace(' ', '');
        var n = !isFinite(+number) ? 0 : +number,
            prec = !isFinite(+decimals) ? 0 : Math.abs(decimals),
            sep = (typeof thousands_sep === 'undefined') ? ',' : thousands_sep,
            dec = (typeof dec_point === 'undefined') ? '.' : dec_point,
            s = '',
            toFixedFix = function(n, prec) {
                var k = Math.pow(10, prec);
                return '' + Math.round(n * k) / k;
            };
        // Fix for IE parseFloat(0.55).toFixed(0) = 0;
        s = (prec ? toFixedFix(n, prec) : '' + Math.round(n)).split('.');
        if (s[0].length > 3) {
            s[0] = s[0].replace(/\B(?=(?:\d{3})+(?!\d))/g, sep);
        }
        if ((s[1] || '').length < prec) {
            s[1] = s[1] || '';
            s[1] += new Array(prec - s[1].length + 1).join('0');
        }
        return s.join(dec);
    }
</script>

<!-- Page Wrapper -->
<div id="wrapper">

    <!-- Sidebar -->
    <?php
    require_once($_SERVER['DOCUMENT_ROOT']."/app/admin/common/navi.php");
    ?>
    <!-- End of Sidebar -->

    <!-- Content Wrapper -->
    <div id="content-wrapper" class="d-flex flex-column">

        <!-- Main Content -->
        <div id="content">

            <!-- Topbar -->
            <?php
            require_once($_SERVER['DOCUMENT_ROOT']."/app/admin/common/header.php");
            ?>
            <!-- End of Topbar -->

            <!-- Begin Page Content -->
            <div class="container-fluid">

                <!-- Page Heading -->
                <div class="d-sm-flex align-items-center justify-content-between mb-4">
                    <h1 class="h3 mb-0 text-gray-800">Dashboard</h1>
                    <a href="#" class="d-none d-sm-inline-block btn btn-sm btn-primary shadow-sm"><i
                            class="fas fa-download fa-sm text-white-50"></i> Generate Report</a>
                </div>

                <!-- Content Row -->
                <div class="row">

                    <div class="col-xl-3 col-md-6 mb-4">
                        <div class="card border-left-primary shadow h-100 py-2">
                            <div class="card-body">
                                <div class="row no-gutters align-items-center">
                                    <div class="col mr-2">
                                        <div class="text-xs font-weight-bold text-primary text-uppercase mb-1">
                                            일 매출</div>
                                        <div id="day_trade_info" class="h5 mb-0 font-weight-bold text-gray-800"></div>
                                    </div>
                                    <div class="col-auto">
                                        <i class="fas fa-calendar fa-2x text-gray-300"></i>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                    
                    <!-- Earnings (Monthly) Card Example -->
                    <div class="col-xl-3 col-md-6 mb-4">
                        <div class="card border-left-primary shadow h-100 py-2">
                            <div class="card-body">
                                <div class="row no-gutters align-items-center">
                                    <div class="col mr-2">
                                        <div class="text-xs font-weight-bold text-primary text-uppercase mb-1">
                                            월 매출</div>
                                        <div id="month_trade_info" class="h5 mb-0 font-weight-bold text-gray-800"></div>
                                    </div>
                                    <div class="col-auto">
                                        <i class="fas fa-calendar fa-2x text-gray-300"></i>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>

                    <!-- Earnings (Monthly) Card Example -->
                    <div class="col-xl-3 col-md-6 mb-4">
                        <div class="card border-left-success shadow h-100 py-2">
                            <div class="card-body">
                                <div class="row no-gutters align-items-center">
                                    <div class="col mr-2">
                                        <div class="text-xs font-weight-bold text-success text-uppercase mb-1">
                                            연 매출</div>
                                        <div id="year_trade_info" class="h5 mb-0 font-weight-bold text-gray-800"></div>
                                    </div>
                                    <div class="col-auto">
                                        <i class="fas fa-dollar-sign fa-2x text-gray-300"></i>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>

                    <!-- Earnings (Monthly) Card Example -->
                    <div class="col-xl-3 col-md-6 mb-4">
                        <div class="card border-left-info shadow h-100 py-2">
                            <div class="card-body">
                                <div class="row no-gutters align-items-center">
                                    <div class="col mr-2">
                                        <div class="text-xs font-weight-bold text-info text-uppercase mb-1">Tasks
                                        </div>
                                        <div class="row no-gutters align-items-center">
                                            <div class="col-auto">
                                                <div class="h5 mb-0 mr-3 font-weight-bold text-gray-800">50%</div>
                                            </div>
                                            <div class="col">
                                                <div class="progress progress-sm mr-2">
                                                    <div class="progress-bar bg-info" role="progressbar"
                                                        style="width: 50%" aria-valuenow="50" aria-valuemin="0"
                                                        aria-valuemax="100"></div>
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                    <div class="col-auto">
                                        <i class="fas fa-clipboard-list fa-2x text-gray-300"></i>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>


                    
                </div>

                <!-- Content Row -->

                <div class="row">

                    <!-- Area Chart -->
                    <div class="col-xl-8 col-lg-7">

                        <div class="card shadow mb-4">
                            <!-- Card Header - Dropdown -->
                            <div class="card-header py-3 d-flex flex-row align-items-center justify-content-between">
                                <h6 class="m-0 font-weight-bold text-primary">매출 Overview</h6>
                                <div class="dropdown no-arrow">
                                    <a class="dropdown-toggle" href="#" role="button" id="dropdownMenuLink"
                                       data-toggle="dropdown" aria-haspopup="true" aria-expanded="false">
                                        <i class="fas fa-ellipsis-v fa-sm fa-fw text-gray-400"></i>
                                    </a>
                                    <div class="dropdown-menu dropdown-menu-right shadow animated--fade-in" style="min-width: 250px;" aria-labelledby="dropdownMenuLink">
                                        <div class="dropdown-header">매출 종류</div>
                                        <div class="dropdown-item">
                                            <label for="day-input">일별 매출</label>
                                            <input id="month_value" class="form-control" type="number" id="day-input" min="1" max="12" placeholder="월 입력" style="width: 30%; display: inline-block;">
                                            <button class="btn btn-primary mt-2" style="display: inline-block;" onclick="getTradeInfo('day')">조회</button>
                                        </div>
                                        <div class="dropdown-item">
                                            <label for="month-input">월별 매출</label>
                                            <input id="year_value" class="form-control" type="number" id="month-input" min="1" max="12" placeholder="연도 입력" style="width: 30%; display: inline-block;">
                                            <button class="btn btn-primary mt-2" style="display: inline-block;" onclick="getTradeInfo('month')">조회</button>
                                        </div>
                                        <a class="dropdown-item" onclick="getTradeInfo('year')">연별 매출</a>
                                        <!--<div class="dropdown-divider"></div>
                                        <a class="dropdown-item" href="#">Something else here</a>-->
                                    </div>
                                </div>
                            </div>


                            <!-- Card Body -->
                            <div class="card-body">
                                <div class="chart-area">
                                    <canvas id="myAreaChart"></canvas>
                                </div>
                            </div>
                        </div>

                    </div>

                    <!-- Pie Chart -->
                    <div class="col-xl-4 col-lg-5">
                        <div class="card shadow mb-4">
                            <!-- Card Header - Dropdown -->
                            <div
                                class="card-header py-3 d-flex flex-row align-items-center justify-content-between">
                                <h6 class="m-0 font-weight-bold text-primary">실시간 상담사 현황</h6>
                                <div class="dropdown no-arrow">
                                    <a class="dropdown-toggle" href="#" role="button" id="dropdownMenuLink"
                                        data-toggle="dropdown" aria-haspopup="true" aria-expanded="false">
                                        <i class="fas fa-ellipsis-v fa-sm fa-fw text-gray-400"></i>
                                    </a>
                                    <div class="dropdown-menu dropdown-menu-right shadow animated--fade-in"
                                        aria-labelledby="dropdownMenuLink">
                                        <div class="dropdown-header">Dropdown Header:</div>
                                        <a class="dropdown-item" href="#">Action</a>
                                        <a class="dropdown-item" href="#">Another action</a>
                                        <div class="dropdown-divider"></div>
                                        <a class="dropdown-item" href="#">Something else here</a>
                                    </div>
                                </div>
                            </div>
                            <!-- Card Body -->
                            <div class="card-body">
                                <div class="chart-pie pt-4 pb-2">
                                    <canvas id="myPieChart"></canvas>
                                </div>

                                <div class="mt-4 text-center small">
                                    <span class="mr-2">
                                        <i class="fas fa-circle text-primary"></i> 상담중
                                    </span>
                                    <span class="mr-2">
                                        <i class="fas fa-circle text-success"></i> 대기중
                                    </span>
                                    <span class="mr-2">
                                        <i class="fas fa-circle text-info"></i> 부재중
                                    </span>
                                </div>

                            </div>
                        </div>
                    </div>
                </div>

                <div class="row">
                    <div class="col-lg-6 mb-4">
                        <div class="card-body">
                            <div class="chart-area">
                                <canvas id="myBarChart"></canvas>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Content Row -->
                <div class="row">

                    <!-- Content Column -->
                    <div class="col-lg-6 mb-4">

                        <!-- Project Card Example -->
                        <div class="card shadow mb-4">
                            <div class="card-header py-3">
                                <h6 class="m-0 font-weight-bold text-primary">Projects</h6>
                            </div>
                            <div class="card-body">
                                <h4 class="small font-weight-bold">Server Migration <span
                                        class="float-right">20%</span></h4>
                                <div class="progress mb-4">
                                    <div class="progress-bar bg-danger" role="progressbar" style="width: 20%"
                                        aria-valuenow="20" aria-valuemin="0" aria-valuemax="100"></div>
                                </div>
                                <h4 class="small font-weight-bold">Sales Tracking <span
                                        class="float-right">40%</span></h4>
                                <div class="progress mb-4">
                                    <div class="progress-bar bg-warning" role="progressbar" style="width: 40%"
                                        aria-valuenow="40" aria-valuemin="0" aria-valuemax="100"></div>
                                </div>
                                <h4 class="small font-weight-bold">Customer Database <span
                                        class="float-right">60%</span></h4>
                                <div class="progress mb-4">
                                    <div class="progress-bar" role="progressbar" style="width: 60%"
                                        aria-valuenow="60" aria-valuemin="0" aria-valuemax="100"></div>
                                </div>
                                <h4 class="small font-weight-bold">Payout Details <span
                                        class="float-right">80%</span></h4>
                                <div class="progress mb-4">
                                    <div class="progress-bar bg-info" role="progressbar" style="width: 80%"
                                        aria-valuenow="80" aria-valuemin="0" aria-valuemax="100"></div>
                                </div>
                                <h4 class="small font-weight-bold">Account Setup <span
                                        class="float-right">Complete!</span></h4>
                                <div class="progress">
                                    <div class="progress-bar bg-success" role="progressbar" style="width: 100%"
                                        aria-valuenow="100" aria-valuemin="0" aria-valuemax="100"></div>
                                </div>
                            </div>
                        </div>

                        <!-- Color System -->
                        <div class="row">
                            <div class="col-lg-6 mb-4">
                                <div class="card bg-primary text-white shadow">
                                    <div class="card-body">
                                        Primary
                                        <div class="text-white-50 small">#4e73df</div>
                                    </div>
                                </div>
                            </div>
                            <div class="col-lg-6 mb-4">
                                <div class="card bg-success text-white shadow">
                                    <div class="card-body">
                                        Success
                                        <div class="text-white-50 small">#1cc88a</div>
                                    </div>
                                </div>
                            </div>
                            <div class="col-lg-6 mb-4">
                                <div class="card bg-info text-white shadow">
                                    <div class="card-body">
                                        Info
                                        <div class="text-white-50 small">#36b9cc</div>
                                    </div>
                                </div>
                            </div>
                            <div class="col-lg-6 mb-4">
                                <div class="card bg-warning text-white shadow">
                                    <div class="card-body">
                                        Warning
                                        <div class="text-white-50 small">#f6c23e</div>
                                    </div>
                                </div>
                            </div>
                            <div class="col-lg-6 mb-4">
                                <div class="card bg-danger text-white shadow">
                                    <div class="card-body">
                                        Danger
                                        <div class="text-white-50 small">#e74a3b</div>
                                    </div>
                                </div>
                            </div>
                            <div class="col-lg-6 mb-4">
                                <div class="card bg-secondary text-white shadow">
                                    <div class="card-body">
                                        Secondary
                                        <div class="text-white-50 small">#858796</div>
                                    </div>
                                </div>
                            </div>
                            <div class="col-lg-6 mb-4">
                                <div class="card bg-light text-black shadow">
                                    <div class="card-body">
                                        Light
                                        <div class="text-black-50 small">#f8f9fc</div>
                                    </div>
                                </div>
                            </div>
                            <div class="col-lg-6 mb-4">
                                <div class="card bg-dark text-white shadow">
                                    <div class="card-body">
                                        Dark
                                        <div class="text-white-50 small">#5a5c69</div>
                                    </div>
                                </div>
                            </div>
                        </div>

                    </div>

                    <div class="col-lg-6 mb-4">

                        <!-- Illustrations -->
                        <div class="card shadow mb-4">
                            <div class="card-header py-3">
                                <h6 class="m-0 font-weight-bold text-primary">Illustrations</h6>
                            </div>
                            <div class="card-body">
                                <div class="text-center">
                                    <img class="img-fluid px-3 px-sm-4 mt-3 mb-4" style="width: 25rem;"
                                        src="img/undraw_posting_photo.svg" alt="...">
                                </div>
                                <p>Add some quality, svg illustrations to your project courtesy of <a
                                        target="_blank" rel="nofollow" href="https://undraw.co/">unDraw</a>, a
                                    constantly updated collection of beautiful svg images that you can use
                                    completely free and without attribution!</p>
                                <a target="_blank" rel="nofollow" href="https://undraw.co/">Browse Illustrations on
                                    unDraw &rarr;</a>
                            </div>
                        </div>

                        <!-- Approach -->
                        <div class="card shadow mb-4">
                            <div class="card-header py-3">
                                <h6 class="m-0 font-weight-bold text-primary">Development Approach</h6>
                            </div>
                            <div class="card-body">
                                <p>SB Admin 2 makes extensive use of Bootstrap 4 utility classes in order to reduce
                                    CSS bloat and poor page performance. Custom CSS classes are used to create
                                    custom components and custom utility classes.</p>
                                <p class="mb-0">Before working with this theme, you should become familiar with the
                                    Bootstrap framework, especially the utility classes.</p>
                            </div>
                        </div>

                    </div>
                </div>

            </div>
            <!-- /.container-fluid -->

        </div>
        <!-- End of Main Content -->

        <!-- Footer -->
        <?php
          require_once($_SERVER['DOCUMENT_ROOT']."/app/admin/common/footer.php");
        ?>
        <!-- End of Footer -->

    </div>
    <!-- End of Content Wrapper -->

    <div id="myModal" class="modal">
        <div class="modal-content">
            <span class="close">&times;</span>
            <div id="modalTextWrapper">
                <div id="modalText"></div>
            </div>
        </div>
    </div>

</div>

<!--<script src="/app/admin/js/demo/chart-area-demo.js"></script>-->
<!--<script src="/app/admin/js/demo/chart-pie-demo.js"></script>-->
<script src="/app/admin/js/demo/chart-bar-demo.js"></script>
<script src="/app/admin/js/demo/datatables-demo.js"></script>
<?php
require_once($_SERVER['DOCUMENT_ROOT']."/app/admin/common/bottom.php");
?>
