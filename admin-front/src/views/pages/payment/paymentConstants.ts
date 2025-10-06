/**
 * 결제 관리 상수 정의
 * 백엔드 API: /api/v1/payments
 */

// 결제 목록 테이블 헤더
export const paymentHeaders: Array<Tableheader> = [
    {value:'payment_id', label:'결제 ID', isShow:true, type:"text", width:'', options:{}, isSortable:false},
    {value:'order_no', label:'주문번호', isShow:true, type:"key", width:'', options:{}, isSortable:false},
    {value:'user_id', label:'회원 ID', isShow:true, type:"text", width:'', options:{}, isSortable:false},
    {value:'amount', label:'결제 금액', isShow:true, type:"number", width:'', options:{}, isSortable:false},
    {value:'payment_method', label:'결제 수단', isShow:true, type:"text", width:'', options:{}, isSortable:false},
    {value:'payment_status', label:'결제 상태', isShow:true, type:"custom", width:'', options:{}, isSortable:false},
    {value:'paid_at', label:'결제 완료일', isShow:true, type:"date", width:'', options:{}, isSortable:false},
    {value:'created_at', label:'생성일', isShow:true, type:"date", width:'', options:{}, isSortable:false},
    {value:'actions', label:'관리', isShow:true, type:"custom", width:'100px', options:{}, isSortable:false}
]

// 결제 목록 검색 옵션
export const paymentSearchOptions: Array<SearchOptions> = [
    {
        key:'search_type', value: 'all', label:'검색타입', type:'select', width:'',
        options:{
            multiple:false,
            placeholder:'값을 설정해주세요',
            items:[
                {value:'all', label:'전체'},
                {value:'user_id', label:'회원 ID'},
                {value:'nickname', label:'닉네임'},
                {value:'email', label:'이메일'},
                {value:'phone', label:'휴대폰 번호'}
            ]
        }
    },
    {key:'search_name', value: '', label:'키워드', type:'string', width:'', options:{}},
    {
        key:'payment_method', value: 'all', label:'결제 수단', type:'select', width:'',
        options: {
            multiple: false,
            placeholder:'값을 설정해주세요.',
            items:[
                {value:'all', label:'전체'},
                {value:'CARD', label:'신용카드'},
                {value:'BANK', label:'계좌이체'},
                {value:'VBANK', label:'가상계좌'},
                {value:'MOBILE', label:'휴대폰'},
                {value:'KAKAOPAY', label:'카카오페이'},
            ]
        }
    },
    {
        key:'payment_status', value: 'all', label:'결제 상태', type:'select', width:'',
        options: {
            multiple: false,
            placeholder:'값을 설정해주세요.',
            items:[
                {value:'all', label:'전체'},
                {value:'SUCCESS', label:'결제 완료'},
                {value:'HOLD', label:'보류'},
                {value:'FAIL', label:'결제 실패'},
                {value:'CANCEL', label:'결제 취소'},
            ]
        }
    },
    {key:'amount', value: null, label:'결제 금액', type:'number', width:'', options:{}},
    {
        key:'date_value', value: [], label:'검색기간', type:'date', width:'',
        options:{
            isRange:true,
            dateType:'date',
            format:'yyyy-MM-dd'
        }
    }
]

// 결제 상태 옵션 (뱃지 색상 매핑)
export const paymentStatusOptions = {
    SUCCESS: {label: '결제 완료', type: 'success'},
    HOLD: {label: '보류', type: 'warning'},
    FAIL: {label: '결제 실패', type: 'danger'},
    CANCEL: {label: '결제 취소', type: 'info'},
}

// 결제 수단 한글 매핑
export const paymentMethodLabels: Record<string, string> = {
    CARD: '신용카드',
    BANK: '계좌이체',
    VBANK: '가상계좌',
    MOBILE: '휴대폰',
    KAKAOPAY: '카카오페이',
}
