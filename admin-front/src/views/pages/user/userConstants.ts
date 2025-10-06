import {Tableheader, SearchOptions} from "@/types/common";

// 사용자 목록 테이블 헤더 (백엔드 API 응답과 매칭)
export const userHeaders: Array<Tableheader> = [
    {value:'user_id', label:'아이디', isShow:true, type:"key", width:'', options:{}, isSortable:true},
    {value:'nickname', label:'닉네임', isShow:true, type:"key", width:'', options:{}, isSortable:true},
    {value:'email', label:'이메일', isShow:true, type:"text", width:'', options:{}, isSortable:true},
    {value:'phone', label:'휴대폰 번호', isShow:true, type:"text", width:'', options:{}, isSortable:true},
    {value:'grade_code', label:'등급', isShow:true, type:"text", width:'', options:{}, isSortable:true},
    {value:'u_point', label:'보유 포인트', isShow:true, type:"custom", width:'', options:{}, isSortable:false},
    {value:'mileage_point', label:'보유 마일리지', isShow:true, type:"number", width:'', options:{}, isSortable:true},
    {value:'created_at', label:'등록일', isShow:true, type:"date", width:'', options:{}, isSortable:true},
];

// 사용자 검색 옵션 (백엔드 API 파라미터와 매칭)
export const userSearchOptions: Array<SearchOptions> = [
    {
        key:'search_type',
        value: 'all',
        label:'검색타입',
        type:'select',
        width:'',
        options:{
            multiple:false,
            placeholder:'값을 설정해주세요',
            items:[
                {value:'all', label:'전체'},
                {value:'user_id', label:'아이디'},
                {value:'nickname', label:'닉네임'},
                {value:'email', label:'이메일'},
                {value:'phone', label:'전화번호'},
            ]
        }
    },
    {
        key:'search_name',
        value: '',
        label:'키워드',
        type:'string',
        width:'',
        options:{}
    },
    {
        key:'join_type',
        value: 'all',
        label:'가입 경로',
        type:'select',
        width:'',
        options: {
            multiple: false,
            placeholder:'값을 설정해주세요.',
            items:[
                {value:'all', label:'전체'},
                {value:'COMMON', label:'일반'},
                {value:'KAKAO', label:'Kakao'},
                {value:'NAVER', label:'Naver'},
            ]
        }
    },
    {
        key:'grade_code',
        value: 'all',
        label:'등급',
        type:'select',
        width:'',
        options: {
            multiple: false,
            placeholder:'값을 설정해주세요.',
            items:[
                {value:'all', label:'전체'},
                {value:'WHITE', label:'WHITE'},
                {value:'BRONZE', label:'BRONZE'},
                {value:'SILVER', label:'SILVER'},
                {value:'GOLD', label:'GOLD'},
                {value:'VIP', label:'VIP'},
                {value:'VIP+', label:'VIP+'},
                {value:'VVIP', label:'VVIP'},
            ]
        }
    },
    {
        key:'date_value',
        value: [],
        label:'검색기간',
        type:'date',
        width:'',
        options:{
            isRange:true,
            dateType:'date',
            format:'yyyy-MM-dd'
        }
    },
];

// 등급 옵션
export const gradeOptions = [
    {value: 'WHITE', label: 'WHITE'},
    {value: 'BRONZE', label: 'BRONZE'},
    {value: 'SILVER', label: 'SILVER'},
    {value: 'GOLD', label: 'GOLD'},
    {value: 'VIP', label: 'VIP'},
    {value: 'VIP+', label: 'VIP+'},
    {value: 'VVIP', label: 'VVIP'},
];

// 가입 경로 옵션
export const joinTypeOptions = [
    {value: 'COMMON', label: '일반'},
    {value: 'KAKAO', label: 'Kakao'},
    {value: 'NAVER', label: 'Naver'},
];

// 포인트 거래 내역 테이블 헤더
export const pointTransactionHeaders: Array<Tableheader> = [
    {value: 'transaction_id', label: '거래 ID', isShow: true, type: "number", width: '100', options: {}, isSortable: true},
    {value: 'transaction_type', label: '거래 유형', isShow: true, type: "text", width: '120', options: {}, isSortable: true},
    {value: 'currency_type', label: '화폐 타입', isShow: true, type: "text", width: '100', options: {}, isSortable: true},
    {value: 'amount', label: '금액', isShow: true, type: "custom", width: '120', options: {}, isSortable: true},
    {value: 'balance_after', label: '잔액', isShow: true, type: "custom", width: '120', options: {}, isSortable: true},
    {value: 'reference_type', label: '참조 유형', isShow: true, type: "text", width: '120', options: {}, isSortable: false},
    {value: 'reference_id', label: '참조 ID', isShow: true, type: "text", width: '120', options: {}, isSortable: false},
    {value: 'description', label: '설명', isShow: true, type: "text", width: '', options: {}, isSortable: false},
    {value: 'created_at', label: '생성일', isShow: true, type: "date", width: '180', options: {}, isSortable: true},
];

// 알림톡 로그 테이블 헤더
export const notificationLogHeaders: Array<Tableheader> = [
    {value: 'log_id', label: '로그 ID', isShow: true, type: "number", width: '100', options: {}, isSortable: true},
    {value: 'channel', label: '채널', isShow: true, type: "text", width: '100', options: {}, isSortable: true},
    {value: 'content', label: '내용', isShow: true, type: "text", width: '', options: {}, isSortable: false},
    {value: 'send_status', label: '발송 상태', isShow: true, type: "text", width: '100', options: {}, isSortable: true},
    {value: 'sent_at', label: '발송일', isShow: true, type: "date", width: '180', options: {}, isSortable: true},
    {value: 'read_at', label: '읽은일', isShow: true, type: "date", width: '180', options: {}, isSortable: true},
    {value: 'created_at', label: '생성일', isShow: true, type: "date", width: '180', options: {}, isSortable: true},
];
