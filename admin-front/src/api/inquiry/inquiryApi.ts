/**
 * 문의사항 API 엔드포인트
 */

const BASE_URL = '/api/v1/inquiries';

// 상담사 문의 (CS_TO_ADMIN)
export const getCounselorInquiryListURL = `${BASE_URL}/list`;
export const getCounselorInquiryDetailURL = `${BASE_URL}/detail`;
export const replyCounselorInquiryURL = `${BASE_URL}/reply`;
export const updateCounselorInquiryURL = `${BASE_URL}/update`;
export const deleteCounselorInquiryURL = `${BASE_URL}/delete`;

// 1:1 고객센터 문의 (USER_TO_ADMIN)
export const getUserInquiryListURL = `${BASE_URL}/user/list`;
export const getUserInquiryDetailURL = `${BASE_URL}/user/detail`;
export const replyUserInquiryURL = `${BASE_URL}/user/reply`;
export const updateUserInquiryURL = `${BASE_URL}/user/update`;
export const deleteUserInquiryURL = `${BASE_URL}/user/delete`;

// 1:1 상담사 문의 (USER_TO_CS)
export const getUserToCsListURL = `${BASE_URL}/user-to-cs/list`;
export const getUserToCsDetailURL = `${BASE_URL}/user-to-cs/detail`;
export const replyUserToCsURL = `${BASE_URL}/user-to-cs/reply`;
export const updateUserToCsURL = `${BASE_URL}/user-to-cs/update`;
export const deleteUserToCsURL = `${BASE_URL}/user-to-cs/delete`;
