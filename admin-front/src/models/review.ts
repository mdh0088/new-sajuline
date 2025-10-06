export class CsReivewClass implements CsReviewInfo {
    idx:number|null = null;
    userIdx:number|null = null;
    csIdx:number|null = null;
    chatlogIdx:number|null = null;
    userCont:string = "";
    csCont:string = "";
    bestYn:string = "";
    showYn:string = "";
    userRegistDate:string = "";
    csRegistDate:string = "";
    csUpdateDate:string = "";

    constructor(data?: Partial<CsReviewInfo>) {
        if (data) {
            Object.assign(this as CsReviewInfo, data);
        }
    }
}

export class DumyReviewClass implements  DumyReviewInfo {
    idx:number|null = null;
    userId:string = "";
    csIdx:number|null = null;
    chatlogIdx:number|null = null;
    chatTime:string = "";
    userCont:string = "";
    userRegistDate:string = "";
    csCont:string = "";
    csRegistDate:string = "";
    registDate:string = "";

    constructor(data?: Partial<DumyReviewInfo>) {
        if (data) {
            Object.assign(this as DumyReviewInfo, data);
        }
    }
}
