// 멤버십 관련 타입 정의

// 멤버십 등급 타입
export type MembershipTier = 'white' | 'bronze' | 'silver' | 'gold' | 'vip' | 'vip-plus' | 'vvip';

// 멤버십 등급 정보
export interface IMembershipTier {
  id: MembershipTier;
  name: string;
  icon: string;
  minAmount: number; // 최소 결제 금액 (원)
  maxAmount?: number; // 최대 결제 금액 (원), VVIP는 없음
  mileageRate: number; // 마일리지 적립률 (%)
  displayOrder: number;
}

// 멤버십 혜택 정보
export interface IMembershipBenefit {
  tier: MembershipTier;
  benefits: string[];
  additionalPerks?: string[];
}

// 사용자 멤버십 정보
export interface IUserMembership {
  currentTier: MembershipTier;
  previousMonthSpending: number; // 전월 결제 금액
  currentMonthSpending: number; // 당월 결제 금액
  totalMileage: number; // 총 보유 마일리지
  availableMileage: number; // 사용 가능 마일리지
  nextTier?: MembershipTier; // 다음 등급
  amountToNextTier?: number; // 다음 등급까지 필요 금액
  tierStartDate: string; // 현재 등급 시작일
  tierEndDate: string; // 현재 등급 종료일
}

// 마일리지 거래 내역
export interface IMileageTransaction {
  id: number;
  type: 'earn' | 'use' | 'expire';
  amount: number;
  balance: number; // 거래 후 잔액
  description: string;
  createdAt: string;
}

// 마일리지 정책
export interface IMileagePolicy {
  expirationPeriod: number; // 만료 기간 (일)
  minimumUsage: number; // 최소 사용 단위
  maximumUsage?: number; // 최대 사용 한도
  conversionRate: number; // 포인트 전환 비율 (1 마일리지 = ? 포인트)
}