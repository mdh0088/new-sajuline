export class BannerClass implements BannerInfo{
    banner_idx: number | null = null;
    bannerNm: string | null = null;
    bannerImg: string | null = null;
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

    constructor(data?: Partial<BannerInfo>) {
        if (data) {
            Object.assign(this as BannerInfo, data);
        }
    }


    from(data: Partial<BannerInfo>): this {
        Object.assign(this as BannerInfo, data);
        return this; // 메서드 체이닝 가능
    }

    static fromArray(dataArray: Partial<BannerInfo>[]): BannerClass[] {
        return dataArray.map((data) => new BannerClass().from(data));
    }

}

