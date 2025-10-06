import http from '@/api/_config/http';
import {getCounselorsListURL, modifyCounselorURL} from "@/api/counselor/counselorApi";
const proxyURL = '/api/customer-support';
export const getCsNoticeListURL = `${proxyURL}/cs-notices`;
export const createCsNoticeURL = `${proxyURL}/create-cs-notice`;
export const modifyCsNoticeURL = `${proxyURL}/modify-cs-notice`;


export const getCsAdminFaqListURL = `${proxyURL}/cs-admin-faqs`;
export const modifyCsAdminFaqURL = `${proxyURL}/modify-cs-admin-faq`;


export const getAdminFaqListURL = `${proxyURL}/admin-faqs`;
export const modifyAdminFaqURL = `${proxyURL}/modify-admin-faq`;


export const getCsFaqListURL = `${proxyURL}/cs-faqs`;
export const modifyCsFaqURL = `${proxyURL}/modify-cs-faq`;


// 공지사항 조회
export async function getCsNoticeInfo(idx) {
    return http.get(proxyURL+'/cs-notice/'+idx);
}

// 공지사항 목록 조회
export async function getCsNoticeList(data) {
    return http.post(getCsNoticeListURL, data);
}


export async function createCsNotice(data: any, formData: any) {
    return http.post(createCsNoticeURL, data, {
        headers: {
            'Content-Type': 'multipart/form-data',
        },
        params: {
            'dataType': 'formData'
        },
        env: {
            FormData: formData
        } as any
    });
}

export async function modifyCsNotice(data: any, formData: any) {
    return http.patch(modifyCsNoticeURL, data, {
        headers: {
            'Content-Type': 'multipart/form-data',
        },
        params: {
            'dataType': 'formData'
        },
        env: {
            FormData: formData
        } as any
    });
}

// 공지상항 삭제
export async function deleteCsNoticeInfo(idx) {
    return http.delete(proxyURL+'/cs-notice/'+idx);
}

/////////////////////////////////////////////////////////////

// 관리자 상담사 문의 조회
export async function getCsAdminFaq(idx) {
    return http.get(proxyURL+'/cs-admin-faq/'+idx);
}

// 관리자 상담사 문의 목록 조회
export async function getCsAdminFaqList(data) {
    return http.post(getCsAdminFaqListURL, data);
}


// 관리자 상담사 문의 수정
export async function modifyCsAdminFaq(data) {
    return http.patch(modifyCsAdminFaqURL, data);
}


// 관리자 상담사 문의 삭제
export async function deleteCsAdminFaq(idx) {
    return http.delete(proxyURL+'/cs-admin-faq/'+idx);
}

/////////////////////////////////////////////////////////////

// 관리자 고객 문의 조회
export async function getAdminFaq(idx) {
    return http.get(proxyURL+'/admin-faq/'+idx);
}

// 관리자 고객 문의 목록 조회
export async function getAdminFaqList(data) {
    return http.post(getAdminFaqListURL, data);
}


// 관리자 고객 문의 수정
export async function modifyAdminFaq(data) {
    return http.patch(modifyAdminFaqURL, data);
}


// 관리자 고객 문의 삭제
export async function deleteAdminFaq(idx) {
    return http.delete(proxyURL+'/admin-faq/'+idx);
}

/////////////////////////////////////////////////////////////

// 상담사 고객 문의 조회
export async function getCsFaq(idx) {
    return http.get(proxyURL+'/cs-faq/'+idx);
}

// 상담사 고객 문의 목록 조회
export async function getCsFaqList(data) {
    return http.post(getCsFaqListURL, data);
}


// 상담사 고객 문의 수정
export async function modifyCsFaq(data) {
    return http.patch(modifyCsFaqURL, data);
}

// 관리자 고객 문의 삭제
export async function deleteCsFaq(idx) {
    return http.delete(proxyURL+'/cs-faq/'+idx);
}


