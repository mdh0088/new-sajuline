import {reactive, ref} from "vue";

export const csAdminFaqHeader:Array<Tableheader> = [
    {value:'idx', label:'Index', isShow:false, type:"key", width:'', options:{}, isSortable:false},
    {value:'nickName', label:'상담사', isShow:true, type:"key",width:'', options:{}, isSortable:false},
    {value:'csCont', label:'상담내용', isShow:true, type:"key",width:'500', options:{}, isSortable:false},
    {value:'csRegistDate',label:"상담 등록일", isShow:true, type:"text", width:'200', options:{}, isSortable:false},
    {value:'adminCont',label:'관리자 상담 내용', isShow:true, type:"text", width:'300', options:{}, isSortable:false},
    {value:'adminRegistDate',label:'관리자 상담 등록일', isShow:true, type:"text", width:'200', options:{}, isSortable:false},
    {value:'adminUpdateDate',label:'관리자 상담 수정일', isShow:true, type:"text", width:'200', options:{}, isSortable:false},
]

export const adminFaqHeader:Array<Tableheader> = [
    {value:'idx', label:'Index', isShow:false, type:"key", width:'', options:{}, isSortable:false},
    {value:'userId', label:'유저아이디', isShow:true, type:"key",width:'200', options:{}, isSortable:false},
    {value:'userTitle', label:'제목', isShow:true, type:"key",width:'350', options:{}, isSortable:false},
    {value:'userCont',label:'상담내용', isShow:true, type:"key", width:'500', options:{}, isSortable:false},
    {value:'userRegistDate',label:'등록일', isShow:true, type:"text", width:'200', options:{}, isSortable:false},
    {value:'adminCont',label:'관리자 상담 내용', isShow:true, type:"text", width:'300', options:{}, isSortable:false},
    {value:'adminRegistDate',label:'관리자 상담 등록일', isShow:true, type:"text", width:'200', options:{}, isSortable:false},
    {value:'adminUpdateDate',label:'관리자 상담 수정일', isShow:true, type:"text", width:'200', options:{}, isSortable:false},
]

export const csFaqHeader:Array<Tableheader> = [
    {value:'idx', label:'Index', isShow:false, type:"key", width:'', options:{}, isSortable:false},
    {value:'userId', label:'유저아이디', isShow:true, type:"key",width:'200', options:{}, isSortable:false},
    {value:'userCont',label:'상담내용', isShow:true, type:"key", width:'500', options:{}, isSortable:false},
    {value:'userRegistDate',label:'등록일', isShow:true, type:"text", width:'200', options:{}, isSortable:false},
    {value:'nickName', label:'상담사', isShow:true, type:"key",width:'', options:{}, isSortable:false},
    {value:'csCont',label:'상담사 상담 내용', isShow:true, type:"text", width:'300', options:{}, isSortable:false},
    {value:'csRegistDate',label:'상담사 상담 등록일', isShow:true, type:"text", width:'200', options:{}, isSortable:false},
    {value:'csUpdateDate',label:'상담사 상담 수정일', isShow:true, type:"text", width:'200', options:{}, isSortable:false},
]

export const csAdminFaqSearchOptions:Array<SearchOptions> = [
    {
        key:'type',value: 'total',label:'검색타입',type:'select',width:'',
        options:{
            multiple:false,
            placeholder:'값을 설정해주세요',
            items:[
                {value:'total',label:'전체'},
                {value:'csCont',label:'고객 문의 내용'},
                {value:'adminCont',label:'관리자 문의 내용'},
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

export const adminFaqSearchOptions:Array<SearchOptions> = [
    {
        key:'type',value: 'total',label:'검색타입',type:'select',width:'',
        options:{
            multiple:false,
            placeholder:'값을 설정해주세요',
            items:[
                {value:'total',label:'전체'},
                {value:'userTitle',label:'고객 문의 제목'},
                {value:'userCont',label:'고객 문의 내용'},
                {value:'adminCont',label:'관리자 문의 내용'},
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

export const csFaqSearchOptions:Array<SearchOptions> = [
    {
        key:'type',value: 'total',label:'검색타입',type:'select',width:'',
        options:{
            multiple:false,
            placeholder:'값을 설정해주세요',
            items:[
                {value:'total',label:'전체'},
                {value:'userCont',label:'고객 문의 내용'},
                {value:'csCont',label:'.상담사 문의 내용'},
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
