export class CounselorClass implements CounselorInfo {
    idx: number = 0;
    showYn: string = '';
    status: string = '';
    csDate: string = '';
    name: string = '';
    nickName: string = '';
    email: string = '';
    phone: string = '';
    password: string = '';
    taroYn:  "Y"|"N" = 'Y';
    luckYn:  "Y"|"N" = 'Y';
    fortuneYn:  "Y"|"N" = 'Y';
    easyYn:  "Y"|"N" = 'Y';
    code: string = '';
    grade: string = '';
    career: string = '';
    afterAmount: number = 0;
    beforeAmount: number = 0;
    workTime: string = '';
    newYn:  "Y"|"N" = 'Y';
    approvalYn:  "Y"|"N" = 'Y';
    outYn:  "Y"|"N" = 'Y';
    shortInfo: string = '';
    notice: string = '';
    greeting: string = '';
    csKeyword: string = '';
    img: string = '';
    img1: string = '';
    img2: string = '';
    img3: string = '';
    img4: string = '';
    img5: string = '';
    recruitDate: string = '';
    type: string = '';
    updateDate: string = '';
    lastLogin: string = '';
    address: string = '';
    arsInfo: ArsCounselorInfo = new ArsCounselorClass();

    constructor(data?: Partial<CounselorInfo>) {
        if (data) {
            Object.assign(this as CounselorInfo, data);
        }


        if (data?.arsInfo) {
            this.arsInfo = new ArsCounselorClass(data.arsInfo);
        }
    }

    static from<T = any>(data: Partial<CounselorInfo>): CounselorClass {
        return new CounselorClass(data);
    }

    static fromArray(dataArray: Partial<CounselorInfo>[]): CounselorClass[] {
        return dataArray.map((data) => this.from(data));
    }
}

export class ArsCounselorClass implements ArsCounselorInfo {
    idx: number = 0;
    m_dnis: string | null = null;
    m_code: string | null = null;
    m_name: string | null = null;
    m_nickname: string | null = null;
    m_tel: string | null = null;
    m_tel1: string | null = null;
    m_tel2: string | null = null;
    m_mobile: string | null = null;
    m_state: string | null = null;
    m_nextstate: string | null = null;
    m_counselling: string | null = null;
    m_id: string | null = null;
    m_passwd: string | null = null;
    m_memo: string | null = null;
    last_chat: string | null = null;
    chat_level: string | null = null;
    class_: string | null = null;
    turn: string | null = null;
    bang: string | null = null;
    holdoff: string | null = null;
    m_bunho: string | null = null;
    m_writer: number | null = null;
    m_prate: number = 0;
    m_fdate: string | null = null;

    constructor(data?: Partial<ArsCounselorInfo>) {
        if (data) {
            Object.assign(this as ArsCounselorInfo, data);
        }
    }
}
