/**
 * 결제 관리 API 엔드포인트 정의
 * 백엔드: /api/v1/payments
 */

const proxyURL = '/api/v1/payments';

export const getPaymentListURL = `${proxyURL}/list`;
export const getPaymentDetailURL = `${proxyURL}/detail`;
export const cancelPaymentURL = `${proxyURL}/cancel`;
