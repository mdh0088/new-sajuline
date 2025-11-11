// 상담사 신청 목록 테이블 헤더
export const recruitmentHeaders: Array<Tableheader> = [
    {value:'application_id', label:'신청ID', isShow:true, type:"text", width:'', options:{}, isSortable:false},
    {value:'name', label:'이름', isShow:true, type:"key", width:'', options:{}, isSortable:false},
    {value:'nickname', label:'닉네임', isShow:true, type:"text", width:'', options:{}, isSortable:false},
    {value:'email', label:'이메일', isShow:true, type:"text", width:'', options:{}, isSortable:false},
    {value:'phone', label:'휴대폰', isShow:true, type:"text", width:'', options:{}, isSortable:false},
    {value:'created_at', label:'신청일시', isShow:true, type:"date", width:'', options:{}, isSortable:false},
    {value:'application_status', label:'상태', isShow:true, type:"custom", width:'', options:{}, isSortable:false}
];

// 상담사 신청 검색 옵션
export const recruitmentSearchOptions: Array<SearchOptions> = [
    {
        key:'search_type', value: 'all', label:'검색타입', type:'select', width:'',
        options:{
            multiple:false,
            placeholder:'값을 설정해주세요',
            items:[
                {value:'all', label:'전체'},
                {value:'name', label:'이름'},
                {value:'nickname', label:'닉네임'},
                {value:'email', label:'이메일'}
            ]
        }
    },
    {key:'search_name', value: '', label:'키워드', type:'string', width:'', options:{}},
    {
        key:'specialties', value: 'all', label:'전문분야', type:'select', width:'',
        options: {
            multiple: false,
            placeholder:'값을 설정해주세요.',
            items:[
                {value:'all', label:'전체'},
                {value:'TARO', label:'타로'},
                {value:'SAJU', label:'사주'},
                {value:'FORTUNE', label:'운세'},
                {value:'EASY', label:'쉬운상담'}
            ]
        }
    },
    {
        key:'application_status', value: 'all', label:'신청상태', type:'select', width:'',
        options: {
            multiple: false,
            placeholder:'값을 설정해주세요.',
            items:[
                {value:'all', label:'전체'},
                {value:'PENDING', label:'대기중'},
                {value:'APPROVED', label:'승인됨'},
                {value:'REJECTED', label:'거절됨'}
            ]
        }
    },
    {
        key:'date_value', value: [], label:'검색기간', type:'date', width:'',
        options:{
            isRange:true,
            dateType:'date',
            format:'yyyy-MM-dd'
        }
    }
];

// 신청 상태 옵션
export const applicationStatusOptions = [
    {value: 'PENDING', label: '대기중'},
    {value: 'APPROVED', label: '승인됨'},
    {value: 'REJECTED', label: '거절됨'}
];

// 전문분야 옵션
export const specialtyOptionsForApplication = [
    {value: 'TARO', label: '타로'},
    {value: 'SAJU', label: '사주'},
    {value: 'FORTUNE', label: '운세'},
    {value: 'EASY', label: '쉬운상담'}
];
