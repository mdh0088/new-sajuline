interface ExhibitionInfo {
    exhibition_idx: number|null;
    exhibitionNm: string|null;
    bannerImg: string|null;
    fileNm: string|null;
    startDate: string|null;
    endDate: string|null;
    showYn: "Y"|"N";
    registUser: string|null;
    registDate: string|null;
    updateUser: string|null;
    updateDate: string|null;
    replayList: Array<ExhibitionReplyInfo> | []
}

interface ExhibitionReplyInfo {
    reply_idx: number|null;
    exhibition_idx: number|null;
    userIdx: number|null;
    userCont: string|null;
    registDate: string|null;
    userNickName: string|null;
}

interface ExhibitionRequest {
    searchName: string|null;
    type: string|null;
    startDt: string|null;
    endDt: string|null;
    showYn: string|null;
    page: number;
    pageSize: number;
}
