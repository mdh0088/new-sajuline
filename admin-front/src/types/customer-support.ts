interface CsNoticeInfo {
    idx: number|null;
    adminIdx: number|null;
    title: string;
    cont: string;
    attachFile: string;
    registDate: string;
    updateDate: string;
}

interface CsAdminFaqInfo {
    idx: number|null;
    csIdx: number|null;
    adminIdx: number|null;
    csCont: string
    csRegistDate: string
    adminCont: string
    attachFile: string
    adminRegistDate: string
    adminUpdateDate: string
    nickName:string
}

interface AdminFaqInfo {
    idx: number|null;
    userIdx: number|null;
    userType: string
    userTitle: string
    userRegistDate: string
    userCont: string
    adminIdx: number|null;
    adminCont: string
    attachFile: string
    adminRegistDate: string
    adminUpdateDate: string
    userId:string
    userNickName:string
}

interface CsFaqInfo {
    idx: number|null;
    userIdx: number|null;
    csIdx: number|null;
    userCont: string
    userRegistDate: string
    csCont: string
    csRegistDate: string
    csUpdateDate: string
    userId:string
    nickName:string
    userNickName:string
}

interface CustomerSupportRequest {
    searchName: string|null;
    type: string|null;
    startDt: string|null;
    endDt: string|null;
    page: number;
    pageSize: number;
}
