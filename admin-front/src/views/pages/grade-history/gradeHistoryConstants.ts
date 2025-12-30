/**
 * 등급 변경 이력 관리 상수 정의
 * 백엔드 API: /api/v1/grades/change-logs/list
 */

// 테이블 헤더
export const gradeHistoryHeaders: Array<Tableheader> = [
    {value:'log_id', label:'로그 ID', isShow:true, type:"text", width:'100', options:{}, isSortable:false},
    {value:'user_id', label:'사용자 ID', isShow:true, type:"text", width:'', options:{}, isSortable:false},
    {value:'grade_before', label:'이전 등급', isShow:true, type:"text", width:'120', options:{}, isSortable:false},
    {value:'grade_after', label:'변경 후 등급', isShow:true, type:"text", width:'120', options:{}, isSortable:false},
    {value:'purchase_amount', label:'구매 금액', isShow:true, type:"number", width:'', options:{}, isSortable:false},
    {value:'change_reason', label:'변경 사유', isShow:true, type:"custom", width:'120', options:{}, isSortable:false},
    {value:'created_at', label:'변경일시', isShow:true, type:"date", width:'', options:{}, isSortable:false}
]

// 검색 옵션
export const gradeHistorySearchOptions: Array<SearchOptions> = [
    {
        key:'year', value: new Date().getFullYear(), label:'연도', type:'select', width:'',
        options:{
            multiple:false,
            placeholder:'연도 선택',
            items: generateYearOptions()
        }
    },
    {
        key:'month', value: '', label:'월', type:'select', width:'',
        options:{
            multiple:false,
            placeholder:'전체',
            items:[
                {value:'', label:'전체'},
                {value:1, label:'1월'},
                {value:2, label:'2월'},
                {value:3, label:'3월'},
                {value:4, label:'4월'},
                {value:5, label:'5월'},
                {value:6, label:'6월'},
                {value:7, label:'7월'},
                {value:8, label:'8월'},
                {value:9, label:'9월'},
                {value:10, label:'10월'},
                {value:11, label:'11월'},
                {value:12, label:'12월'}
            ]
        }
    },
    {key:'user_id', value: '', label:'사용자 ID', type:'string', width:'', options:{}},
    {
        key:'change_reason', value: '', label:'변경 사유', type:'select', width:'',
        options: {
            multiple: false,
            placeholder:'전체',
            items:[
                {value:'', label:'전체'},
                {value:'AUTO_BATCH', label:'자동 배치'},
                {value:'MANUAL', label:'수동 변경'}
            ]
        }
    }
]

// 변경 사유 옵션
export const changeReasonOptions = [
    {value: 'AUTO_BATCH', label: '자동 배치'},
    {value: 'MANUAL', label: '수동 변경'}
]

// 연도 옵션 생성 함수 (현재 연도 기준 5년 전부터)
function generateYearOptions() {
    const currentYear = new Date().getFullYear();
    const years = [];
    for (let i = 0; i < 5; i++) {
        const year = currentYear - i;
        years.push({value: year, label: `${year}년`});
    }
    return years;
}
