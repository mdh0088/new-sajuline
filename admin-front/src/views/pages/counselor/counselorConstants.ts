import {reactive, ref} from "vue";

// 새로운 백엔드 API에 맞춘 테이블 헤더
export const counselorHeaders: Array<Tableheader> = [
    {value:'counselor_id', label:'이메일(ID)', isShow:true, type:"key", width:'', options:{}, isSortable:false},
    {value:'name', label:'이름', isShow:true, type:"text", width:'', options:{}, isSortable:false},
    {value:'nickname', label:'닉네임', isShow:true, type:"text", width:'', options:{}, isSortable:false},
    {value:'phone', label:'휴대폰 번호', isShow:true, type:"text", width:'', options:{}, isSortable:false},
    {value:'after_amount', label:'선불 금액', isShow:true, type:"number", width:'', options:{}, isSortable:false},
    {value:'created_at', label:'등록일', isShow:true, type:"date", width:'', options:{}, isSortable:false},
    {value:'m_state', label:'상담상태태', isShow:true, type:"custom", width:'', options:{}, isSortable:false},
    {value:'is_show', label:'노출여부', isShow:true, type:"custom", width:'', options:{}, isSortable:false}
]

// 새로운 백엔드 API에 맞춘 검색 옵션
export const counselorSearchOptions: Array<SearchOptions> = [
    {
        key:'search_type', value: 'all', label:'검색타입', type:'select', width:'',
        options:{
            multiple:false,
            placeholder:'값을 설정해주세요',
            items:[
                {value:'all', label:'전체'},
                {value:'name', label:'이름'},
                {value:'nickname', label:'닉네임'},
                {value:'counselor_id', label:'이메일'}
            ]
        }
    },
    {key:'search_name', value: '', label:'키워드', type:'string', width:'', options:{}},
    {
        key:'specialties', value: 'all', label:'상담사 타입', type:'select', width:'',
        options: {
            multiple: false,
            placeholder:'값을 설정해주세요.',
            items:[
                {value:'all', label:'전체'},
                {value:'TARO', label:'타로'},
                {value:'FORTHUN', label:'신점'},
                {value:'SAJU', label:'사주'},
            ]
        }
    },
    {
        key:'is_show', value: 'all', label:'노출유무', type:'select', width:'',
        options: {
            multiple: false,
            placeholder:'값을 설정해주세요.',
            items:[
                {value:'all', label:'전체'},
                {value:true, label:'Y'},
                {value:false, label:'N'},
            ]
        }
    },
    {
        key:'is_out', value: 'all', label:'탈퇴유무', type:'select', width:'',
        options: {
            multiple: false,
            placeholder:'값을 설정해주세요.',
            items:[
                {value:'all', label:'전체'},
                {value:true, label:'Y'},
                {value:false, label:'N'},
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
]

// 등급 옵션 (백엔드와 일치)
export const csGradeOptions = [
    {value: 'GOLD', label: 'GOLD'},
    {value: 'SILVER', label: 'SILVER'},
    {value: 'BRONZE', label: 'BRONZE'},
]

// 상담사 상태 옵션
export const counselorStateOptions = [
    {value: '1', label: '대기중'},
    {value: '2', label: '상담중'},
    {value: '3', label: '부재중'},
]

// 전문 분야 옵션
export const specialtyOptions = [
    {value: 'TARO', label: '타로'},
    {value: 'FORTHUN', label: '신점'},
    {value: 'SAJU', label: '사주'},
]

// 상담사 타입 리스트 (CounselorDetailDrawer에서 사용)
// 참고: 이 값은 구 API 구조를 위한 것이며, 신규 API에서는 specialty_types 배열 사용
export const csTypeList = ['taroYn','luckYn','fortuneYn','easyYn']

/* =========================
   기존 코드 (참고용 주석 처리)
   ========================= */

// export const counselorHeaders:Array<Tableheader> = [
//     {value:'idx', label:'Index', isShow:false, type:"key", width:'', options:{}, isSortable:false},
//     {value:'name', label:'이름', isShow:true, type:"key",width:'', options:{}, isSortable:false},
//     {value:'nickName',label:'닉네임', isShow:true, type:"key", width:'', options:{}, isSortable:false},
//     {value:'email',label:'이메일', isShow:true, type:"text", width:'', options:{}, isSortable:false},
//     {value:'phone',label:'휴대폰 번호', isShow:true, type:"text", width:'', options:{}, isSortable:false},
//     {value:'afterAmount',label:'선불 금액', isShow:true, type:"number", width:'', options:{}, isSortable:false},
//     {value:'csDate',label:'등록일', isShow:true, type:"date", width:'', options:{}, isSortable:false},
//     {value:'callCnt',label:'상담내역', isShow:true, type:"date", width:'', options:{}, isSortable:false},
//     {value:'showYn',label:'노출여부', isShow:true, type:"custom", width:'', options:{}, isSortable:false}
// ]

// export const applicantHeaders:Array<Tableheader> = [
//     {value:'idx', label:'Index', isShow:false, type:"key", width:'', options:{}, isSortable:false},
//     {value:'name', label:'이름', isShow:true, type:"key",width:'', options:{}, isSortable:false},
//     {value:'nickName',label:'닉네임', isShow:true, type:"key", width:'', options:{}, isSortable:false},
//     {value:'email',label:'이메일', isShow:true, type:"text", width:'', options:{}, isSortable:false},
//     {value:'phone',label:'휴대폰 번호', isShow:true, type:"text", width:'', options:{}, isSortable:false},
//     {value:'csType',label:'신청타입', isShow:true, type:"custom", width:'', options:{}, isSortable:false},
//     {value:'recruitDate',label:'신청일', isShow:true, type:"date", width:'', options:{}, isSortable:false}
// ]

// export const outHeaders:Array<Tableheader> = [
//     {value:'idx', label:'Index', isShow:false, type:"key", width:'', options:{}, isSortable:false},
//     {value:'name', label:'이름', isShow:true, type:"key",width:'', options:{}, isSortable:false},
//     {value:'nickName',label:'닉네임', isShow:true, type:"key", width:'', options:{}, isSortable:false},
//     {value:'email',label:'이메일', isShow:true, type:"text", width:'', options:{}, isSortable:false},
//     {value:'phone',label:'휴대폰 번호', isShow:true, type:"text", width:'', options:{}, isSortable:false},
//     {value:'outDate',label:'탈퇴일', isShow:true, type:"date", width:'', options:{}, isSortable:false}
// ]

// export const counselorSearchOptions:Array<SearchOptions> = [
//     {
//         key:'type',value: 'total',label:'검색타입',type:'select',width:'',
//         options:{
//             multiple:false,
//             placeholder:'값을 설정해주세요',
//             items:[
//                 {value:'total',label:'전체'},
//                 {value:'name',label:'이름'},
//                 {value:'nickName',label:'닉네임'},
//                 {value:'email',label:'이메일'}
//             ]
//         }
//     },
//     {key:'searchName',value: '',label:'키워드',type:'string',width:'',options:{}},
//     {
//         key:'csType',value: 'total',label:'상담사 타입',type:'select',width:'',
//         options: {
//             multiple: false,
//             placeholder:'값을 서정해주세요.',
//             items:[
//                 {value:'total',label:'전체'},
//                 {value:'1',label:'타로'},
//                 {value:'2',label:'신점'},
//                 {value:'3',label:'역학'},
//                 {value:'4',label:'사주'},
//             ]
//         }
//     },
//     {
//         key:'showYn',value: 'total',label:'노출유무',type:'select',width:'',
//         options: {
//             multiple: false,
//             placeholder:'값을 서정해주세요.',
//             items:[
//                 {value:'total',label:'전체'},
//                 {value:'Y',label:'Y'},
//                 {value:'N',label:'N'},
//             ]
//         }
//     },
//     {key:'dateValue',value: [],label:'검색기간',type:'date',width:'',
//         options:{
//             isRange:true,
//             dateType:'date',
//             format:'yyyy-MM-dd'
//         }
//     }
// ]

// export const applicantSearchOptions:Array<SearchOptions> = [
//     {
//         key:'type',value: 'total',label:'검색타입',type:'select',width:'',
//         options:{
//             multiple:false,
//             placeholder:'값을 설정해주세요',
//             items:[
//                 {value:'total',label:'전체'},
//                 {value:'name',label:'이름'},
//                 {value:'nickName',label:'닉네임'},
//                 {value:'email',label:'이메일'}
//             ]
//         }
//     },
//     {key:'searchName',value: '',label:'키워드',type:'string',width:'',options:{}},
//     {
//         key:'taroYn',value: 'total',label:'타로',type:'select',width:'',
//         options: {
//             multiple: false,
//             placeholder:'값을 서정해주세요.',
//             items:[
//                 {value:'total',label:'전체'},
//                 {value:'Y',label:'Y'},
//                 {value:'N',label:'N'},
//             ]
//         }
//     },
//     {
//         key:'luckYn',value: 'total',label:'사주/운세',type:'select',width:'',
//         options: {
//             multiple: false,
//             placeholder:'값을 서정해주세요.',
//             items:[
//                 {value:'total',label:'전체'},
//                 {value:'Y',label:'Y'},
//                 {value:'N',label:'N'},
//             ]
//         }
//     },
//     {
//         key:'fortuneYn',value: 'total',label:'신점',type:'select',width:'',
//         options: {
//             multiple: false,
//             placeholder:'값을 서정해주세요.',
//             items:[
//                 {value:'total',label:'전체'},
//                 {value:'Y',label:'Y'},
//                 {value:'N',label:'N'},
//             ]
//         }
//     },
//     {
//         key:'easyYn',value: 'total',label:'역학',type:'select',width:'',
//         options: {
//             multiple: false,
//             placeholder:'값을 서정해주세요.',
//             items:[
//                 {value:'total',label:'전체'},
//                 {value:'Y',label:'Y'},
//                 {value:'N',label:'N'},
//             ]
//         }
//     },
//     {key:'dateValue',value: [],label:'검색기간',type:'date',width:'',
//         options:{
//             isRange:true,
//             dateType:'date',
//             format:'yyyy-MM-dd'
//         }
//     }
// ]

// export const csTypeList = ['taroYn','luckYn','fortuneYn','easyYn'];

// export const csGradeOptions = [
//     {value: 'GOLD', label: 'GOLD'},
//     {value: 'SILVER', label: 'SILVER'},
//     {value: 'BRONZE', label: 'BRONZE'},
// ]
