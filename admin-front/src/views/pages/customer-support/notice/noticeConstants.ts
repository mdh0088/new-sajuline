/**
 * 공지사항 관리 상수 정의 (새 백엔드 API 규격)
 * 백엔드 API: /api/v1/notices
 */

// 공지사항 목록 테이블 헤더
export const noticeHeaders: Array<Tableheader> = [
    {value:'notice_id', label:'공지 ID', isShow:true, type:"number", width:'', options:{}, isSortable:false},
    {value:'title', label:'제목', isShow:true, type:"key", width:'', options:{}, isSortable:false},
    {value:'target_audience', label:'대상', isShow:true, type:"custom", width:'', options:{}, isSortable:false},
    {value:'notice_type', label:'타입', isShow:true, type:"text", width:'', options:{}, isSortable:false},
    {value:'is_important', label:'중요', isShow:true, type:"custom", width:'', options:{}, isSortable:false},
    {value:'is_active', label:'활성', isShow:true, type:"custom", width:'', options:{}, isSortable:false},
    {value:'view_count', label:'조회수', isShow:true, type:"number", width:'', options:{}, isSortable:false},
    {value:'created_at', label:'등록일', isShow:true, type:"date", width:'', options:{}, isSortable:false},
];

// 공지사항 목록 검색 옵션
export const noticeSearchOptions: Array<SearchOptions> = [
    {
        key:'search_type', value: 'all', label:'검색타입', type:'select', width:'',
        options:{
            multiple:false,
            placeholder:'값을 설정해주세요',
            items:[
                {value:'all', label:'전체'},
                {value:'title', label:'제목'},
                {value:'content', label:'내용'},
            ]
        }
    },
    {key:'search_name', value: '', label:'키워드', type:'string', width:'', options:{}},
    {
        key:'target_audience', value: 'all', label:'대상', type:'select', width:'',
        options: {
            multiple: false,
            placeholder:'값을 설정해주세요.',
            items:[
                {value:'all', label:'전체'},
                {value:'ALL', label:'전체 공개'},
                {value:'USER', label:'사용자'},
                {value:'COUNSELOR', label:'상담사'},
            ]
        }
    },
    {
        key:'is_important', value: 'all', label:'중요 공지', type:'select', width:'',
        options: {
            multiple: false,
            placeholder:'값을 설정해주세요.',
            items:[
                {value:'all', label:'전체'},
                {value:true, label:'예'},
                {value:false, label:'아니오'},
            ]
        }
    },
    {
        key:'is_active', value: 'all', label:'활성 상태', type:'select', width:'',
        options: {
            multiple: false,
            placeholder:'값을 설정해주세요.',
            items:[
                {value:'all', label:'전체'},
                {value:true, label:'활성'},
                {value:false, label:'비활성'},
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

// 대상 옵션
export const targetAudienceOptions = [
    {value: 'ALL', label: '전체 공개'},
    {value: 'USER', label: '사용자'},
    {value: 'COUNSELOR', label: '상담사'},
];

// 공지 타입 옵션
export const noticeTypeOptions = [
    {value: 'GENERAL', label: '일반'},
    {value: 'EVENT', label: '이벤트'},
    {value: 'SYSTEM', label: '시스템'},
];
