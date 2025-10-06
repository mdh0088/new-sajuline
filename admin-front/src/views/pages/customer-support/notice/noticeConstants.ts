import {reactive, ref} from "vue";

export const noticeHeader:Array<Tableheader> = [
    {value:'idx', label:'인덱스', isShow:false, type:"key",width:'', options:{}, isSortable:false},
    {value:'title',label:'제목', isShow:true, type:"key", width:'', options:{}, isSortable:false},
    {value:'registDate',label:'등록일', isShow:true, type:"date", width:'', options:{}, isSortable:false},
]

export const noticeSearchOptions:Array<SearchOptions> = [
    {
        key:'type',value: 'total',label:'검색타입',type:'select',width:'',
        options:{
            multiple:false,
            placeholder:'값을 설정해주세요',
            items:[
                {value:'total',label:'전체'},
                {value:'title',label:'제목'},
                {value:'cont',label:'내용'},
            ]
        }
    },
    {key:'searchName',value: '',label:'키워드',type:'string',width:'',options:{}},
    {key:'dateValue',value: [],label:'검색기간',type:'date',width:'',
        options:{
            isRange:true,
            dateType:'date',
            format:'yyyy-MM-dd'
        }
    },
]
