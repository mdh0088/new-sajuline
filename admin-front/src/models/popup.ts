
export class PopupClass implements PopupInfo{
    popup_idx: number | null = null;
    popupNm: string | null = null;
    popupImg: string | null = null;
    fileNm: string | null = null;
    showYn: "Y" | "N" = "N";
    ord: number | null = null;
    target: "BLANK" | "SELF" = "SELF";
    clickable:  "Y" | "N" = "N";
    randingUrl: string | null = null;
    startDate: string | null = null;
    endDate: string | null = null;
    description: string | null = null;
    registUser: string | null = null;
    registDate: string | null = null;
    updateUser: string | null = null;
    updateDate: string | null = null;

    constructor(data?: Partial<PopupInfo>) {
        if (data) {
            Object.assign(this as PopupInfo, data);
        }
    }


    from(data: Partial<PopupInfo>): this {
        Object.assign(this as PopupInfo, data);
        return this; // 메서드 체이닝 가능
    }

    static fromArray(dataArray: Partial<PopupInfo>[]): PopupClass[] {
        return dataArray.map((data) => new PopupClass().from(data));
    }

}

