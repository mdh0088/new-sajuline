export type UserType = 'USER' | 'CS';

export interface KakaoAlarmHistoryInfo {
    idx: number | null;
    user_type: UserType | null;
    user_idx: number | null;
    no: string | null;
    code: string | null;
    send_cont: string | null;
    result_code: number | null;
    regist_date: string | null;
}

export interface KakaoAlarmTemplateInfo {
    idx: number | null;
    code: string | null;
    name: string | null;
    content: string | null;
    pc_link: string | null;
    mo_link: string | null;
}

export interface KakaoAlarmWaitInfo {
    user_idx: number | null;
    cs_idx: number | null;
    regist_date: string | null;
}
