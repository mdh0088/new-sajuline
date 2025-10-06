export class MileageProductClass implements MileageProductInfo {
    m_product_idx: number|null = 0;
    m_product_name: string|null = null;
    m_product_value: number|null = 0;
    charge_point: number|null = 0;
    m_product_img: string|null = null;
    file_nm: string|null = null;
    start_dt: string|null = null;
    end_dt: string|null = null;
    description:string|null=null;
    ord: number|null = 0;
    is_use: string|null = "N";
    regist_date: string|null = null;
    update_date: string|null = null;

    constructor(data?: Partial<MileageProductInfo>) {
        if (data) {
            Object.assign(this as MileageProductInfo, data);
        }
    }

    from(data: Partial<MileageProductInfo>): this {
        Object.assign(this as MileageProductInfo, data);
        return this; // 메서드 체이닝 가능
    }

    static fromArray(dataArray: Partial<MileageProductInfo>[]): MileageProductClass[] {
        return dataArray.map((data) => new MileageProductClass().from(data));
    }
}
