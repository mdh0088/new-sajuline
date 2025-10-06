export const exhibitionHeader:Array<Tableheader> = [
    {value:'exhibition_idx', label:'인덱스', isShow:false, type:"key", width:'', options:{}, isSortable:false},
    {value:'showYn',label:'노출여부', isShow:true, type:"custom", width:'', options:{}, isSortable:false},
    {value:'exhibitionNm',label:'기획전 명', isShow:true, type:"key", width:'', options:{}, isSortable:false},
    {value:'fileNm',label:'업로드 파일명', isShow:true, type:"text", width:'', options:{}, isSortable:false},
    {value:'startDate',label:'시작일', isShow:true, type:"text", width:'', options:{}, isSortable:false},
    {value:'endDate',label:'종료일', isShow:true, type:"text", width:'', options:{}, isSortable:false},
    {value:'registDate',label:'등록일', isShow:true, type:"date", width:'', options:{}, isSortable:false},
]

export const exhibitionSearchOptions:Array<SearchOptions> = [
    {
        key:'type',value: 'total',label:'검색타입',type:'select',width:'',
        options:{
            multiple:false,
            placeholder:'값을 설정해주세요',
            items:[
                {value:'total',label:'전체'},
                {value:'exhibitionNm',label:'기획전 이름'},
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

export const exhibitionInfo:ExhibitionInfo ={
    exhibition_idx: null,
    exhibitionNm: null,
    bannerImg: null,
    fileNm: null,
    startDate: null,
    endDate: null,
    showYn: "N",
    registUser: null,
    registDate: null,
    updateUser: null,
    updateDate: null,
    replayList: [] as Array<ExhibitionReplyInfo>
}

