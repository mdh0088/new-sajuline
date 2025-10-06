export class ProductClass implements ProductInfo {
    idx: number|null = null;
    productName: string = "";
    productValue: number = 0;
    discountValue: number = 0;
    saveValue: number = 0;
    startDt: string = "";
    endDt: string = "";
    ord: string = "";
    isUse: string = "";
    registDate: string = "";

    constructor(data?: Partial<ProductInfo>) {
        if (data) {
            Object.assign(this as ProductInfo, data);
        }
    }
}
