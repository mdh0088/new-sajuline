interface PopupInfo {
    popup_idx: number|null;
    popupNm: string|null;
    popupImg: string|null;
    fileNm: string|null;
    showYn: "Y"|"N";
    ord: number|null;
    target: "BLANK"|"SELF";
    clickable: "Y"|"N";
    randingUrl: string|null;
    startDate: string|null;
    endDate: string|null;
    description: string|null;
    registUser: string|null;
    registDate: string|null;
    updateUser: string|null;
    updateDate: string|null;
}

interface PopupRequest {
    searchName: string|null;
    type: string|null;
    startDt: string|null;
    endDt: string|null;
    showYn: string|null;
    page: number;
    pageSize: number;
}
