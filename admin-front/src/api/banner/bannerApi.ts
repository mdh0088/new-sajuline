/**
 * 배너 API 엔드포인트 정의 (새 백엔드 API 규격)
 * 백엔드 API: /api/v1/banners
 */

const BASE_URL = '/api/v1/banners';

export const getBannerListURL = `${BASE_URL}/list`;
export const getBannerDetailURL = `${BASE_URL}/detail`;
export const createBannerURL = `${BASE_URL}/create`;
export const updateBannerURL = `${BASE_URL}/update`;
export const deleteBannerURL = `${BASE_URL}/delete`;
