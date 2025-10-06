interface BannerInfo {
    banner_idx: number | null;
    bannerNm: string | null;
    bannerImg: string | null;
    fileNm: string | null;
    showYn: "Y" | "N";
    ord: number | null;
    target: "BLANK" | "SELF";
    clickable:"Y" | "N";
    randingUrl: string | null;
    startDate: string | null;
    endDate: string | null;
    description: string | null;
    registUser: string | null;
    registDate: string | null;
    updateUser: string | null;
    updateDate: string | null;
}

interface BannerRequest {
    searchName: string|null;
    type: string|null;
    startDt: string|null;
    endDt: string|null;
    showYn: string|null;
    page: number;
    pageSize: number;
}
