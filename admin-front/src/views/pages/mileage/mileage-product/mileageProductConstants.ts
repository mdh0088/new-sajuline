/**
 * 마일리지 상품 관리 상수 정의
 * 백엔드 API 규격에 맞춰 작성
 */

export const mileageProductHeader: Array<Tableheader> = [
    {
        value: 'm_product_img',
        label: '이미지',
        isShow: true,
        type: "custom",
        width: '100px',
        options: {},
        isSortable: false
    },
    {
        value: 'm_product_name',
        label: '상품명',
        isShow: true,
        type: "key",
        width: '',
        options: {},
        isSortable: false
    },
    {
        value: 'm_product_value',
        label: '상품 금액',
        isShow: true,
        type: "number",
        width: '',
        options: {},
        isSortable: false
    },
    {
        value: 'charge_point',
        label: '충전 포인트',
        isShow: true,
        type: "number",
        width: '',
        options: {},
        isSortable: false
    },
    {
        value: 'valid_from',
        label: '판매 시작일',
        isShow: true,
        type: "date",
        width: '',
        options: {},
        isSortable: false
    },
    {
        value: 'valid_until',
        label: '판매 종료일',
        isShow: true,
        type: "date",
        width: '',
        options: {},
        isSortable: false
    },
    {
        value: 'ord',
        label: '노출 순서',
        isShow: true,
        type: "number",
        width: '',
        options: {},
        isSortable: false
    },
    {
        value: 'is_active',
        label: '활성화',
        isShow: true,
        type: "custom",
        width: '',
        options: {},
        isSortable: false
    },
    {
        value: 'created_at',
        label: '등록일',
        isShow: true,
        type: "date",
        width: '',
        options: {},
        isSortable: false
    }
];
