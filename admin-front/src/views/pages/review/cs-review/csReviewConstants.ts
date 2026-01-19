/**
 * 상담 후기 관리 상수 정의
 * 백엔드 API 규격에 맞춰 작성
 */

// 후기 태그 옵션
export const REVIEW_TAG_OPTIONS = [
  { value: '정확해요', label: '정확해요' },
  { value: '친절해요', label: '친절해요' },
  { value: '속시원해요', label: '속시원해요' },
  { value: '위로가 돼요', label: '위로가 돼요' },
  { value: '공감력 좋아요', label: '공감력 좋아요' },
  { value: '해결책 제시', label: '해결책 제시' }
];

export const csReviewHeader: Array<Tableheader> = [
  {
    value: 'user_nickname',
    label: '사용자',
    isShow: true,
    type: "text",
    width: '100px',
    options: {},
    isSortable: false
  },
  {
    value: 'counselor_nickname',
    label: '상담사',
    isShow: true,
    type: "key",
    width: '100px',
    options: {},
    isSortable: false
  },
  {
    value: 'rating',
    label: '별점',
    isShow: true,
    type: "number",
    width: '80px',
    options: {},
    isSortable: false
  },
  {
    value: 'content',
    label: '후기 내용',
    isShow: true,
    type: "text",
    width: '',
    options: {},
    isSortable: false
  },
  {
    value: 'counselor_reply',
    label: '상담사 답변',
    isShow: true,
    type: "text",
    width: '',
    options: {},
    isSortable: false
  },
  {
    value: 'is_best',
    label: '베스트',
    isShow: true,
    type: "custom",
    width: '80px',
    options: {},
    isSortable: false
  },
  {
    value: 'is_visible',
    label: '노출',
    isShow: true,
    type: "custom",
    width: '80px',
    options: {},
    isSortable: false
  },
  {
    value: 'like_count',
    label: '좋아요',
    isShow: true,
    type: "number",
    width: '80px',
    options: {},
    isSortable: false
  },
  {
    value: 'created_at',
    label: '등록일',
    isShow: true,
    type: "date",
    width: '120px',
    options: {},
    isSortable: false
  },
  {
    value: 'counselor_replied_at',
    label: '답변일',
    isShow: true,
    type: "date",
    width: '120px',
    options: {},
    isSortable: false
  }
];

export const csReviewSearchOptions: Array<SearchOptions> = [
  {
    key: 'search_type',
    value: 'all',
    label: '검색타입',
    type: 'select',
    width: '',
    options: {
      multiple: false,
      placeholder: '검색 타입 선택',
      items: [
        { value: 'all', label: '전체' },
        { value: 'content', label: '후기 내용' },
        { value: 'reply_content', label: '상담사 답변' },
      ]
    }
  },
  {
    key: 'search_name',
    value: '',
    label: '키워드',
    type: 'string',
    width: '',
    options: {}
  },
  {
    key: 'user_id',
    value: '',
    label: '사용자 ID',
    type: 'string',
    width: '',
    options: {}
  },
  {
    key: 'counselor_id',
    value: '',
    label: '상담사 ID',
    type: 'string',
    width: '',
    options: {}
  },
  {
    key: 'date_value',
    value: [],
    label: '검색기간',
    type: 'date',
    width: '',
    options: {
      isRange: true,
      dateType: 'date',
      format: 'yyyy-MM-dd'
    }
  },
];
