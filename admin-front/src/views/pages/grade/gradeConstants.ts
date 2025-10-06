import {Tableheader} from "@/types/common";

// 등급 목록 테이블 헤더 (백엔드 GradeItem과 매칭)
export const gradeHeaders: Array<Tableheader> = [
    {value:'grade_code', label:'등급 코드', isShow:true, type:"key", width:'', options:{}, isSortable:false},
    {value:'grade_name', label:'등급명', isShow:true, type:"text", width:'', options:{}, isSortable:false},
    {value:'grade_level', label:'등급 레벨', isShow:true, type:"number", width:'', options:{}, isSortable:false},
    {value:'min_purchase_amount', label:'최소 구매 금액', isShow:true, type:"number", width:'', options:{}, isSortable:false},
    {value:'point_earn_rate', label:'포인트 적립률', isShow:true, type:"custom", width:'', options:{}, isSortable:false},
    {value:'discount_rate', label:'할인율', isShow:true, type:"custom", width:'', options:{}, isSortable:false},
    {value:'is_active', label:'활성화 여부', isShow:true, type:"custom", width:'', options:{}, isSortable:false},
    {value:'created_at', label:'등록일', isShow:true, type:"date", width:'', options:{}, isSortable:false},
    {value:'actions', label:'액션', isShow:true, type:"custom", width:'150', options:{}, isSortable:false}
];

// 등급별 유저 목록 테이블 헤더 (백엔드 UsersByGradeItem과 매칭)
export const usersByGradeHeaders: Array<Tableheader> = [
    {value:'user_id', label:'아이디', isShow:true, type:"key", width:'', options:{}, isSortable:false},
    {value:'email', label:'이메일', isShow:true, type:"text", width:'', options:{}, isSortable:false},
    {value:'nickname', label:'닉네임', isShow:true, type:"text", width:'', options:{}, isSortable:false},
    {value:'phone', label:'휴대폰 번호', isShow:true, type:"text", width:'', options:{}, isSortable:false},
    {value:'join_type', label:'가입 유형', isShow:true, type:"text", width:'', options:{}, isSortable:false},
    {value:'created_at', label:'등록일', isShow:true, type:"date", width:'', options:{}, isSortable:false}
];
