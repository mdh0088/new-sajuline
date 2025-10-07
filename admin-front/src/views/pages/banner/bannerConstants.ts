/**
 * 배너 관리 상수 정의 (새 백엔드 API 규격)
 * 백엔드 API: /api/v1/banners
 */

// 테이블 헤더
export const bannerHeaders: Array<Tableheader> = [
    {value:'banner_name', label:'배너명', isShow:true, type:"key", width:'', options:{}, isSortable:false},
    {value:'banner_type', label:'배너 타입', isShow:true, type:"text", width:'', options:{}, isSortable:false},
    {value:'display_order', label:'노출 순서', isShow:true, type:"custom", width:'', options:{}, isSortable:false},
    {value:'is_active', label:'활성 여부', isShow:true, type:"custom", width:'', options:{}, isSortable:false},
    {value:'link_target', label:'링크 타겟', isShow:true, type:"custom", width:'', options:{}, isSortable:false},
    {value:'valid_from', label:'시작일', isShow:true, type:"date", width:'', options:{}, isSortable:false},
    {value:'valid_until', label:'종료일', isShow:true, type:"date", width:'', options:{}, isSortable:false},
    {value:'click_count', label:'클릭수', isShow:true, type:"number", width:'', options:{}, isSortable:false},
    {value:'created_at', label:'등록일', isShow:true, type:"date", width:'', options:{}, isSortable:false}
]

// 검색 옵션
export const bannerSearchOptions: Array<SearchOptions> = [
    {
        key:'search_type', value: 'all', label:'검색타입', type:'select', width:'',
        options:{
            multiple:false,
            placeholder:'값을 설정해주세요',
            items:[
                {value:'all', label:'전체'},
                {value:'banner_name', label:'배너명'},
                {value:'banner_code', label:'배너 코드'},
                {value:'banner_type', label:'배너 타입'}
            ]
        }
    },
    {key:'search_name', value: '', label:'키워드', type:'string', width:'', options:{}},
    {
        key:'is_active', value: 'all', label:'활성 여부', type:'select', width:'',
        options: {
            multiple: false,
            placeholder:'값을 설정해주세요.',
            items:[
                {value:'all', label:'전체'},
                {value:true, label:'활성'},
                {value:false, label:'비활성'}
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

// 링크 타겟 옵션 (백엔드 API와 일치)
export const linkTargetOptions = [
    {value: 'SELF', label: '현재창'},
    {value: 'BLANK', label: '새창'}
]

// 배너 타입 옵션
export const bannerTypeOptions = [
    {value: 'MAIN', label: '메인 배너'},
    {value: 'POPUP', label: '팝업 배너'},
    {value: 'SUB', label: '서브 배너'}
]
