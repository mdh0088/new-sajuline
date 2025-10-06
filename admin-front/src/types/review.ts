interface CsReviewInfo {
    idx:number|null;
    userIdx:number|null;
    csIdx:number|null;
    chatlogIdx:number|null;
    userCont:string;
    csCont:string;
    bestYn:string;
    showYn:string;
    userRegistDate:string;
    csRegistDate:string;
    csUpdateDate:string;
}

interface DumyReviewInfo {
    idx:number|null;
    userId:string;
    csIdx:number|null;
    chatlogIdx:number|null;
    chatTime:string;
    userCont:string;
    userRegistDate:string;
    csCont:string;
    csRegistDate:string;
    registDate:string;
}

interface ReviewRequest {
    searchName: string|null;
    type: string|null;
    startDt: string|null;
    endDt: string|null;
    bestYn: string|null;
    showYn: string|null;
    page: number;
    pageSize: number;
}
