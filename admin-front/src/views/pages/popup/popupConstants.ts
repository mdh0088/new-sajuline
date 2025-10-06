export const popupHeader:Array<Tableheader> = [
    {value:'popup_idx', label:'인덱스', isShow:false, type:"key", width:'', options:{}, isSortable:false},
    {value:'ord',label:'순번', isShow:true, type:"custom", width:'', options:{}, isSortable:false},
    {value:'showYn',label:'노출여부', isShow:true, type:"custom", width:'', options:{}, isSortable:false},
    {value:'popupNm',label:'팝업 명', isShow:true, type:"key", width:'', options:{}, isSortable:false},
    {value:'fileNm',label:'업로드 파일명', isShow:true, type:"text", width:'', options:{}, isSortable:false},
    {value:'clickable',label:'클릭 가능 여부', isShow:true, type:"text", width:'', options:{}, isSortable:false},
    {value:'startDate',label:'시작일', isShow:true, type:"text", width:'', options:{}, isSortable:false},
    {value:'endDate',label:'종료일', isShow:true, type:"text", width:'', options:{}, isSortable:false},
    {value:'registDate',label:'등록일', isShow:true, type:"date", width:'', options:{}, isSortable:false},
]


export const popupSearchOption:Array<SearchOptions> = [
    {
        key:'type',value: 'total',label:'검색타입',type:'select',width:'',
        options:{
            multiple:false,
            placeholder:'값을 설정해주세요',
            items:[
                {value:'total',label:'전체'},
                {value:'PopupNm',label:'팝업 이름'},
                {value:'fileNm',label:'업로드 파일명'},
            ]
        }
    },
    {key:'searchName',value: '',label:'키워드',type:'string',width:'',options:{}},
    {
        key:'showYn',value: 'total',label:'노출여부',type:'select',width:'',
        options: {
            multiple: false,
            placeholder:'값을 서정해주세요.',
            items:[
                {value:'total',label:'전체'},
                {value:'Y',label:'Y'},
                {value:'N',label:'N'},
            ]
        }
    },
    {key:'dateValue',value: [],label:'검색기간',type:'date',width:'',
        options:{
            isRange:true,
            dateType:'date',
            format:'yyyy-MM-dd'
        }
    },
]
