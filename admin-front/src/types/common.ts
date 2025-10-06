
export interface Tableheader {
    value: string;
    label: string;
    isShow: boolean;
    type: "key" | "text" | "number" | "date" | "switch" | "button" | "custom";  // 필요시 추가
    width?: string;
    isSortable: boolean;
    options:any;
}

export interface TableOptions<T=any> {
    headers: Array<Tableheader>;
    rowItems: Array<number>;
    currentPage:number;
    totalCnt:number;
    rowPage:number;
    isLoading:boolean;
    isDrawerActive:boolean;
    isSelectActive: boolean;
    isNumberActive: boolean;
    isPagination: boolean;
    chooseRow:object;
    selectedItems: Array<T>;
    items: Array<T>;
    page?: number;  // API 페이지 번호
    pageSize?: number;  // API 페이지 크기
}


export interface SearchOptions {
    key: string;
    value: any;
    label: string;
    type: "string" | "select" | "date"; // 필요시 추가
    width?: string|number;
    options: any;  // 조건마다 다르기 때문 any 선언 
}

export interface SearchOptionsList {
    optionsList: Array<SearchOptions>;
}
