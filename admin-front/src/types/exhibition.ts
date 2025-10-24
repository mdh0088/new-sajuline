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
    replayList: Array<ExhibitionReplyInfo> | [];
    // 백엔드 t_event 테이블 필드들
    event_code?: string|null;
    event_type?: string|null;
    description?: string|null;
    terms?: string|null;
    reward_type?: string|null;
    reward_value?: number|null;
    max_participants?: number|null;
    current_participants?: number|null;
    metadata_json?: any;
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
