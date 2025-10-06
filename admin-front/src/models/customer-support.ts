export class CsNoticeClass implements CsNoticeInfo {
    idx: number|null = null;
    adminIdx: number|null = null;
    title: string = "";
    cont: string= "";
    attachFile: string = "";
    registDate: string = "";
    updateDate: string = "";

    constructor(data?: Partial<CsNoticeInfo>) {
        if (data) {
            Object.assign(this as CsNoticeInfo, data);
        }
    }
}


export class CsAdminFaqClass implements CsAdminFaqInfo {
    idx: number|null = null;
    csIdx: number|null = null;
    adminIdx: number|null = null;
    csCont: string = "";
    csRegistDate: string = "";
    adminCont: string = "";
    attachFile: string = "";
    adminRegistDate: string = "";
    adminUpdateDate: string = "";
    nickName:string = "";

    constructor(data?: Partial<CsAdminFaqInfo>) {
        if (data) {
            Object.assign(this as CsAdminFaqInfo, data);
        }
    }
}


export class AdminFaqInClass implements AdminFaqInfo {
    idx: number|null = null;
    userIdx: number|null = null;
    userType: string = "";
    userTitle: string = "";
    userRegistDate: string = "";
    userCont: string = "";
    adminIdx: number|null = null;
    adminCont: string = "";
    attachFile: string = "";
    adminRegistDate: string = "";
    adminUpdateDate: string = "";
    userId:string = "";
    userNickName:string = "";

    constructor(data?: Partial<AdminFaqInfo>) {
        if (data) {
            Object.assign(this as AdminFaqInfo, data);
        }
    }
}

export class CsFaqClass implements CsFaqInfo {
    idx: number|null = null;
    userIdx: number|null = null;
    csIdx: number|null = null;
    userCont: string = "";
    userRegistDate: string = "";
    csCont: string = "";
    csRegistDate: string = "";
    csUpdateDate: string = "";
    userId:string = "";
    nickName:string = "";
    userNickName:string = "";

    constructor(data?: Partial<CsFaqInfo>) {
        if (data) {
            Object.assign(this as CsFaqInfo, data);
        }
    }
}
