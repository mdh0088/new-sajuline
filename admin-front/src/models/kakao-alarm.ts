import { KakaoAlarmHistoryInfo, KakaoAlarmTemplateInfo, KakaoAlarmWaitInfo, UserType } from "@/types/kakao-alarm";

export class KakaoAlarmHistoryClass implements KakaoAlarmHistoryInfo {
    idx: number | null = null;
    user_type: UserType | null = null;
    user_idx: number | null = null;
    no: string | null = null;
    code: string | null = null;
    send_cont: string | null = null;
    result_code: number | null = null;
    regist_date: string | null = null;

    constructor(data?: Partial<KakaoAlarmHistoryInfo>) {
        if (data) {
            Object.assign(this as KakaoAlarmHistoryInfo, data);
        }
    }

    from(data: Partial<KakaoAlarmHistoryInfo>): this {
        Object.assign(this as KakaoAlarmHistoryInfo, data);
        return this;
    }

    static fromArray(dataArray: Partial<KakaoAlarmHistoryInfo>[]): KakaoAlarmHistoryClass[] {
        return dataArray.map((data) => new KakaoAlarmHistoryClass().from(data));
    }
}

export class KakaoAlarmTemplateClass implements KakaoAlarmTemplateInfo {
    idx: number | null = null;
    code: string | null = null;
    name: string | null = null;
    content: string | null = null;
    pc_link: string | null = null;
    mo_link: string | null = null;

    constructor(data?: Partial<KakaoAlarmTemplateInfo>) {
        if (data) {
            Object.assign(this as KakaoAlarmTemplateInfo, data);
        }
    }

    from(data: Partial<KakaoAlarmTemplateInfo>): this {
        Object.assign(this as KakaoAlarmTemplateInfo, data);
        return this;
    }

    static fromArray(dataArray: Partial<KakaoAlarmTemplateInfo>[]): KakaoAlarmTemplateClass[] {
        return dataArray.map((data) => new KakaoAlarmTemplateClass().from(data));
    }
}

export class KakaoAlarmWaitClass implements KakaoAlarmWaitInfo {
    user_idx: number | null = null;
    cs_idx: number | null = null;
    regist_date: string | null = null;

    constructor(data?: Partial<KakaoAlarmWaitInfo>) {
        if (data) {
            Object.assign(this as KakaoAlarmWaitInfo, data);
        }
    }

    from(data: Partial<KakaoAlarmWaitInfo>): this {
        Object.assign(this as KakaoAlarmWaitInfo, data);
        return this;
    }

    static fromArray(dataArray: Partial<KakaoAlarmWaitInfo>[]): KakaoAlarmWaitClass[] {
        return dataArray.map((data) => new KakaoAlarmWaitClass().from(data));
    }
} 