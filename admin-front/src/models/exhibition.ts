export class ExhibitionClass implements ExhibitionInfo{
    exhibition_idx: number | null = null;
    exhibitionNm: string | null = null;
    bannerImg: string | null = null;
    fileNm: string | null = null;
    startDate: string | null = null;
    endDate: string | null = null;
    showYn: "Y" | "N" = "N";
    registUser: string | null = null;
    registDate: string | null = null;
    updateUser: string | null = null;
    updateDate: string | null = null;
    replayList: Array<ExhibitionReplyInfo> | [] = [];

    constructor(data?: Partial<ExhibitionInfo>) {
        if (data) {
            Object.assign(this as ExhibitionInfo, data);
        }

        if (data?.replayList) {
            this.replayList = ExhibitionReplyInfoClass.fromArray(data.replayList);
        }
    }

    from(data: Partial<ExhibitionInfo>): this {
        Object.assign(this as ExhibitionInfo, data);
        return this; // 메서드 체이닝 가능
    }

    static fromArray(dataArray: Partial<ExhibitionInfo>[]): ExhibitionClass[] {
        return dataArray.map((data) => new ExhibitionClass().from(data));
    }

}

export class ExhibitionReplyInfoClass implements ExhibitionReplyInfo {
    reply_idx: number|null = null;
    exhibition_idx: number|null = null;
    userIdx: number|null = null;
    userCont: string|null = "";
    registDate: string|null = "";
    userNickName: string|null = "";

    constructor(data?: Partial<ExhibitionReplyInfo>) {
        if (data) {
            Object.assign(this as ExhibitionReplyInfo, data);
        }
    }
    from(data: Partial<ExhibitionReplyInfo>): this {
        Object.assign(this as ExhibitionReplyInfo, data);
        return this; // 메서드 체이닝 가능
    }

    static fromArray(dataArray: Partial<ExhibitionReplyInfo>[]): ExhibitionReplyInfoClass[] {
        return dataArray.map((data) => new ExhibitionReplyInfoClass().from(data));
    }
}
