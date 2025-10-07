import type { Tableheader, SearchOptions } from '@/models/common';

// ===================================================
// 상담사 문의 (CS_TO_ADMIN) - /inquiries/list
// ===================================================
export const counselorInquiryHeaders: Array<Tableheader> = [
  { value: 'counselor_id', label: '상담사 ID', isShow: true, type: 'custom', width: '', options: {}, isSortable: false },
  { value: 'counselor_name', label: '상담사명', isShow: true, type: 'custom', width: '', options: {}, isSortable: false },
  { value: 'counselor_nickname', label: '닉네임', isShow: true, type: 'custom', width: '', options: {}, isSortable: false },
  { value: 'cs_contnet', label: '상담사 문의', isShow: true, type: 'custom', width: '', options: {}, isSortable: false },
  { value: 'inquiry_category', label: '카테고리', isShow: true, type: 'custom', width: '', options: {}, isSortable: false },
  { value: 'inquiry_created_at', label: '등록일', isShow: true, type: 'custom', width: '', options: {}, isSortable: false },
  { value: 'inquiry_reply_content', label: '답변여부', isShow: true, type: 'custom', width: '', slotName: 'reply_status', options: {}, isSortable: false },
  { value: 'inquiry_answered_at', label: '답변일', isShow: true, type: 'custom', width: '', options: {}, isSortable: false },
];

export const counselorInquirySearchOptions: Array<SearchOptions> = [
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
        { value: 'user_title', label: '제목' },
        { value: 'user_content', label: '내용' },
        { value: 'reply_content', label: '답변내용' },
      ]
    }
  },
  { key: 'search_name', value: '', label: '키워드', type: 'string', width: '', options: {} },
  { key: 'counselor_id', value: '', label: '상담사ID', type: 'string', width: '', options: {} },
  {
    key: 'dateValue',
    value: [],
    label: '등록일',
    type: 'date',
    width: '',
    options: {
      isRange: true,
      dateType: 'date',
      format: 'yyyy-MM-dd'
    }
  },
];

// ===================================================
// 1:1 고객센터 문의 (USER_TO_ADMIN) - /inquiries/user/list
// ===================================================
export const userInquiryHeaders: Array<Tableheader> = [
  { value: 'user_name', label: '사용자명', isShow: true, type: 'custom', width: '', options: {}, isSortable: false },
  { value: 'user_nickname', label: '닉네임', isShow: true, type: 'custom', width: '', options: {}, isSortable: false },
  { value: 'inquiry_category', label: '카테고리', isShow: true, type: 'custom', width: '', options: {}, isSortable: false },
  { value: 'inquiry_user_title', label: '제목', isShow: true, type: 'custom', width: '', options: {}, isSortable: false },
  { value: 'inquiry_user_content', label: '유저 내용', isShow: true, type: 'custom', width: '', options: {}, isSortable: false },
  { value: 'inquiry_created_at', label: '등록일', isShow: true, type: 'custom', width: '', options: {}, isSortable: false },
  { value: 'inquiry_reply_content', label: '답변여부', isShow: true, type: 'custom', width: '', slotName: 'reply_status', options: {}, isSortable: false },
  { value: 'inquiry_answered_at', label: '답변일', isShow: true, type: 'custom', width: '', options: {}, isSortable: false },
];

export const userInquirySearchOptions: Array<SearchOptions> = [
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
        { value: 'title', label: '제목' },
        { value: 'content', label: '내용' },
      ]
    }
  },
  { key: 'search_name', value: '', label: '키워드', type: 'string', width: '', options: {} },
  { key: 'user_id', value: '', label: '사용자ID', type: 'string', width: '', options: {} },
  {
    key: 'dateValue',
    value: [],
    label: '등록일',
    type: 'date',
    width: '',
    options: {
      isRange: true,
      dateType: 'date',
      format: 'yyyy-MM-dd'
    }
  },
];

// ===================================================
// 1:1 상담사 문의 (USER_TO_CS) - /inquiries/user-to-cs/list
// ===================================================
export const userToCsHeaders: Array<Tableheader> = [
  { value: 'user_id', label: '사용자 ID', isShow: true, type: 'custom', width: '', options: {}, isSortable: false },
  { value: 'user_nickname', label: '사용자 닉네임', isShow: true, type: 'custom', width: '', options: {}, isSortable: false },
  { value: 'user_content', label: '유저 내용', isShow: true, type: 'custom', width: '', options: {}, isSortable: false },
  { value: 'counselor_id', label: '상담사명', isShow: true, type: 'custom', width: '', options: {}, isSortable: false },
  { value: 'counselor_name', label: '상담사명', isShow: true, type: 'custom', width: '', options: {}, isSortable: false },
  { value: 'counselor_nickname', label: '상담사명', isShow: true, type: 'custom', width: '', options: {}, isSortable: false },
  { value: 'inquiry_reply_content', label: '상담사 답변', isShow: true, type: 'custom', width: '', options: {}, isSortable: false },
  { value: 'inquiry_category', label: '카테고리', isShow: true, type: 'custom', width: '', options: {}, isSortable: false },
  { value: 'inquiry_created_at', label: '등록일', isShow: true, type: 'custom', width: '', options: {}, isSortable: false },
  { value: 'inquiry_answered_at', label: '답변일', isShow: true, type: 'custom', width: '', options: {}, isSortable: false },
];

export const userToCsSearchOptions: Array<SearchOptions> = [
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
        { value: 'user_title', label: '제목' },
        { value: 'user_content', label: '내용' },
        { value: 'reply_content', label: '답변내용' },
      ]
    }
  },
  { key: 'search_name', value: '', label: '키워드', type: 'string', width: '', options: {} },
  { key: 'user_id', value: '', label: '사용자ID', type: 'string', width: '', options: {} },
  { key: 'counselor_id', value: '', label: '상담사ID', type: 'string', width: '', options: {} },
  {
    key: 'dateValue',
    value: [],
    label: '등록일',
    type: 'date',
    width: '',
    options: {
      isRange: true,
      dateType: 'date',
      format: 'yyyy-MM-dd'
    }
  },
];
