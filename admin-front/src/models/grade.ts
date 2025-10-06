export class GradeClass implements GradeInfo {
    grade:string|null = null;
    gradeNm:string|null = null;
    purchaseAmount:number|null = 0;
    conditionType:conditionType = "GTE";
    saveValue:number|null = 0;
    discountValue:number|null = 0;
    userGradeCount:number|null = 0;
    gradeImg:string | null = null;
    fileNm:string | null = null;
    description:string | null = null;
    registUser:string | null = null;
    registDate:string | null = null;
    updateUser:string | null = null;
    updateDate:string | null = null;

    constructor(data?: Partial<GradeInfo>) {
        if (data) {
            Object.assign(this as GradeInfo, data);
        }
    }

    from(data: Partial<GradeInfo>): this {
        Object.assign(this as GradeInfo, data);
        return this; // 메서드 체이닝 가능
    }

    static fromArray(dataArray: Partial<GradeInfo>[]): GradeClass[] {
        return dataArray.map((data) => new GradeClass().from(data));
    }
}

export class GradeBatchConfigClass implements GradeBatchConfigInfo {
    period_month:number|null= 0;
    period_day:number|null= 0;
    isUse: "Y" | "N"= "Y";
    updateUser:string | null= null;
    updateDate:string | null= null;

    constructor(data?: Partial<GradeBatchConfigInfo>) {
        if (data) {
            Object.assign(this as GradeBatchConfigInfo, data);
        }
    }

    from(data: Partial<GradeBatchConfigInfo>): this {
        Object.assign(this as GradeBatchConfigInfo, data);
        return this; // 메서드 체이닝 가능
    }
}
