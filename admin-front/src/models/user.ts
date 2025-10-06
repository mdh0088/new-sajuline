export class UserClass implements UserInfo {
    idx:number|null = null
    nickName:string = '';
    userId:string = '';
    email:string= '';
    phone:string ='';
    userStatus:string ='';
    joinType:string ='';
    grade:string='';
    registDate:string ='';
    updateDate:string ='';
    lastLogin:string ='';
    userPoint:string ='';
    password:string = '';
    arsInfo:ArsUserInfo = new ArsUserClass();

    constructor(data?: Partial<UserInfo>) {
        if (data) {
            Object.assign(this as UserInfo, data);
        }

        if (data?.arsInfo) {
            this.arsInfo = new ArsUserClass(data.arsInfo);
        }
    }

    from(data: Partial<UserInfo>): this {
        Object.assign(this as UserInfo, data);

        // arsInfo가 있는 경우 처리
        if (data?.arsInfo) {
            this.arsInfo = new ArsUserClass(data.arsInfo);
        }

        return this; // 메서드 체이닝 가능
    }

    static fromArray(dataArray: Partial<UserInfo>[]): UserClass[] {
        return dataArray.map((data) => new UserClass().from(data));
    }
}

export class ArsUserClass implements ArsUserInfo {
    idx: number|null = null;
    u_id: string|null = "";
    u_tel: string|null = "";
    u_passwd: string|null = "";
    u_kname: string|null = "";
    u_memcd: string|null = "";
    u_login: string|null = "";
    u_state: string|null = "";
    u_point: string|null = "";
    u_fdate: string|null = "";
    u_rdate: string|null = "";
    regdate: string|null = "";
    u_memo: string|null = "";

    constructor(data?: Partial<ArsUserInfo>) {
        if (data) {
            Object.assign(this as ArsUserInfo, data);
        }
    }
}
