export class TableOptionsClass<T = any> implements TableOptions<T> {
    headers: Array<Tableheader> = [];
    rowItems: Array<number> = [10, 50, 100];
    currentPage: number = 1;
    totalCnt: number = 0;
    rowPage: number = 10;
    isLoading: boolean = false;
    isDrawerActive: boolean = false;
    isSelectActive: boolean = true; // 선택 checkbox 활성화 여부
    isNumberActive: boolean = false; // 좌측 순번 노출 여부
    isPagination: boolean = true;
    isSortable: boolean = false;
    chooseRow: object = {};
    selectedItems: Array<T> = [];
    items: Array<T> = [];


    constructor(data?: Partial<TableOptions<T>>) {
        if (data) {
            Object.assign(this, data);
        }
    }

/*    static from(data: Partial<TableOptionsClass>): TableOptionsClass {
        const banner = new TableOptionsClass();
        Object.assign(banner, data); // 자동으로 매핑
        return banner;
    }*/

    // 데이터 매핑을 위한 인스턴스 메서드
    from(data: Partial<TableOptions<T>>): this {
        Object.assign(this, data);
        return this; // 체이닝 가능
    }

    // 배열 데이터를 처리하는 정적 메서드 (인스턴스 생성 후 매핑)
    static fromArray<T = any>(dataArray: Partial<TableOptions<T>>[]): TableOptionsClass<T>[] {
        return dataArray.map((data) => new TableOptionsClass().from(data));
    }
}

export class SearchOptionsClass implements SearchOptions{
    key:string = "";
    value:string | number = "";
    label:string = "";
    type: "string" | "select" | "date" = "string";
    width:string | number = "";
    options:any = "";

    constructor(data?: Partial<SearchOptions>) {
        if (data) {
            Object.assign(this as SearchOptions, data);
        }
    }

    // constructor(data?:Partial<SearchOptions>) {
    //     if (data) {
    //         this.key = data.key || "";
    //         this.value = Array.isArray(data.value) ? data.value : [];
    //         this.label = data.label || "";
    //         this.type = data.type || "string";
    //         this.width = data.width || "";
    //         this.options = data.options ? { ...data.options, items: [...(data.options.items || [])] } : null;
    //     }
    // }
}

export class SearchOptionsClassList {
    optionsList:Array<SearchOptionsClass> = [];

    constructor(dataArray?:Partial<SearchOptions>[]) {
        this.optionsList = Array.isArray(dataArray)
            ? dataArray.map(data => new SearchOptionsClass(data))
            : [];
    }

    // 🔹 특정 옵션 가져오기 (인스턴스 메서드)
    getOptionByKey(key:string) {
        return this.optionsList.find(option => option.key === key) || null;
    }

    // 🔹 특정 옵션의 value 변경 (인스턴스 메서드)
    setOptionValue(key:string, newValue:string | number) {
        const option = this.getOptionByKey(key);
        if (option) {
            option.value = newValue;
        }
    }
}



// export class SearchOptionsClass implements SearchOptions{
//     key: string = "";
//     value: string | number = "";
//     label: string = "";
//     type: "string" | "select" | "date" = "string";
//     width?: string | number = "";
//     options: any = "";

//     constructor(data?: Partial<SearchOptions>) {
//         if (data) {
//             Object.assign(this as SearchOptions, data);
//         }
//     }

//     // 주입 받은 데이터 형태로 세팅
//     static from(data: Partial<SearchOptions>): SearchOptions {
//         return new SearchOptionsClass(data);
//     }

//     static fromArray(dataArray: Partial<SearchOptions>[]): SearchOptionsClass[] {
//         return dataArray.map((data) => this.from(data));
//     }

//     static getValueByKey(
//         searchOptions: Array<SearchOptions>,
//         key: string
//     ): any {
//         const option = searchOptions.find((item) => item.key === key);

//         if (!option) {
//             return null; // Key not found
//         }

//         if (key === "dateValue" && Array.isArray(option.value)) {
//             // Special handling for dateValue
//             return {
//                 startDt: option.value[0] || null,
//                 endDt: option.value[1] || null,
//             };
//         }

//         // Default return value
//         return option.value;
//     }
// }
