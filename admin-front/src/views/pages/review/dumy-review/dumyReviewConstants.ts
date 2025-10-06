
export const dumyReviewHeader:Array<Tableheader> = [
    {value:'idx', label:'인덱스', isShow:false, type:"key",width:'', options:{}, isSortable:false},
    {value:'userId',label:'유저 아이디', isShow:true, type:"key", width:'', options:{}, isSortable:false},
    {value:'userCont',label:'유저 내용', isShow:true, type:"text", width:'', options:{}, isSortable:false},
    {value:'userRegistDate',label:'등록일', isShow:true, type:"date", width:'', options:{}, isSortable:false},
    {value:'code',label:'상담사 코드', isShow:true, type:"text", width:'', options:{}, isSortable:false},
    {value:'nickName',label:'상담사 닉네임', isShow:true, type:"text", width:'', options:{}, isSortable:false},
    {value:'csCont',label:'리뷰 댓글', isShow:true, type:"text", width:'', options:{}, isSortable:false},
    {value:'csRegistDate',label:'리뷰 등록일', isShow:true, type:"date", width:'', options:{}, isSortable:false},
]

export const dumySearchOptions :Array<SearchOptions> = [
    {
        key:'type',value: 'total',label:'검색타입',type:'select',width:'',
        options:{
            multiple:false,
            placeholder:'값을 설정해주세요',
            items:[
                {value:'total',label:'전체'},
                {value:'userCont',label:'유저 내용'},
                {value:'csCont',label:'상담 내용'},
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
