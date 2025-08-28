// 폼 검증 유틸리티 함수들

export interface ValidationResult {
  isValid: boolean
  message?: string
}

// 이름 검증
export const validateName = (name: string): ValidationResult => {
  const trimmedName = name.trim()
  
  if (!trimmedName) {
    return { isValid: false, message: '이름을 입력해주세요.' }
  }
  
  if (trimmedName.length < 2) {
    return { isValid: false, message: '이름은 2글자 이상 입력해주세요.' }
  }
  
  if (trimmedName.length > 10) {
    return { isValid: false, message: '이름은 10글자 이하로 입력해주세요.' }
  }
  
  // 특수문자 제외 (한글, 영문, 숫자만 허용)
  const nameRegex = /^[가-힣a-zA-Z0-9\s]+$/
  if (!nameRegex.test(trimmedName)) {
    return { isValid: false, message: '이름에는 한글, 영문, 숫자만 사용할 수 있습니다.' }
  }
  
  return { isValid: true }
}

// 사용자 ID 검증
export const validateUserId = (userId: string): ValidationResult => {
  const trimmedUserId = userId.trim()
  
  if (!trimmedUserId) {
    return { isValid: false, message: '사용자 ID를 입력해주세요.' }
  }
  
  if (trimmedUserId.length < 4) {
    return { isValid: false, message: '사용자 ID는 4자 이상 입력해주세요.' }
  }
  
  if (trimmedUserId.length > 20) {
    return { isValid: false, message: '사용자 ID는 20자 이하로 입력해주세요.' }
  }
  
  // 영숫자, 언더스코어, 하이픈만 허용
  const userIdRegex = /^[a-zA-Z0-9_-]+$/
  if (!userIdRegex.test(trimmedUserId)) {
    return { isValid: false, message: '사용자 ID는 영문, 숫자, 언더스코어(_), 하이픈(-)만 사용할 수 있습니다.' }
  }
  
  // 첫 글자는 영문으로 시작해야 함 (선택사항이지만 일반적인 규칙)
  if (!/^[a-zA-Z]/.test(trimmedUserId)) {
    return { isValid: false, message: '사용자 ID는 영문으로 시작해야 합니다.' }
  }
  
  return { isValid: true }
}

// 생년월일 검증
export const validateBirthDate = (birthDate: string): ValidationResult => {
  if (!birthDate) {
    return { isValid: false, message: '생년월일을 선택해주세요.' }
  }
  
  const selectedDate = new Date(birthDate)
  const currentDate = new Date()
  const minDate = new Date('1900-01-01')
  
  // 유효한 날짜인지 확인
  if (isNaN(selectedDate.getTime())) {
    return { isValid: false, message: '올바른 날짜를 선택해주세요.' }
  }
  
  // 미래 날짜 체크
  if (selectedDate > currentDate) {
    return { isValid: false, message: '생년월일은 오늘 이전 날짜여야 합니다.' }
  }
  
  // 너무 과거 날짜 체크
  if (selectedDate < minDate) {
    return { isValid: false, message: '1900년 이후 날짜를 입력해주세요.' }
  }
  
  // 나이 체크 (150세 이상 불가)
  const age = currentDate.getFullYear() - selectedDate.getFullYear()
  if (age > 150) {
    return { isValid: false, message: '올바른 생년월일을 입력해주세요.' }
  }
  
  return { isValid: true }
}

// 출생시간 검증
export const validateBirthTime = (birthTime: string): ValidationResult => {
  if (!birthTime) {
    return { isValid: false, message: '출생시간을 선택해주세요.' }
  }
  
  // 시간 형식 검증 (HH:MM)
  const timeRegex = /^([01]?[0-9]|2[0-3]):[0-5][0-9]$/
  if (!timeRegex.test(birthTime)) {
    return { isValid: false, message: '올바른 시간 형식을 선택해주세요.' }
  }
  
  return { isValid: true }
}

// 성별 검증
export const validateGender = (gender: string): ValidationResult => {
  if (!gender || !['M', 'F'].includes(gender)) {
    return { isValid: false, message: '성별을 선택해주세요.' }
  }
  
  return { isValid: true }
}

// 달력 종류 검증
export const validateCalendarType = (calendarType: string): ValidationResult => {
  if (!calendarType || !['solar', 'lunar'].includes(calendarType)) {
    return { isValid: false, message: '달력 종류를 선택해주세요.' }
  }
  
  return { isValid: true }
}

// 전체 폼 검증
export interface UserFormData {
  name: string
  birthDate: string
  birthTime: string
  gender: string
  calendarType: string
}

export const validateUserForm = (formData: UserFormData): ValidationResult => {
  // 각 필드별 검증
  const nameResult = validateName(formData.name)
  if (!nameResult.isValid) return nameResult
  
  const birthDateResult = validateBirthDate(formData.birthDate)
  if (!birthDateResult.isValid) return birthDateResult
  
  const birthTimeResult = validateBirthTime(formData.birthTime)
  if (!birthTimeResult.isValid) return birthTimeResult
  
  const genderResult = validateGender(formData.gender)
  if (!genderResult.isValid) return genderResult
  
  const calendarResult = validateCalendarType(formData.calendarType)
  if (!calendarResult.isValid) return calendarResult
  
  return { isValid: true }
}

// 실시간 검증을 위한 디바운스 함수
export const debounce = <T extends (...args: any[]) => any>(
  func: T,
  wait: number
): ((...args: Parameters<T>) => void) => {
  let timeout: NodeJS.Timeout | null = null
  
  return (...args: Parameters<T>) => {
    if (timeout) {
      clearTimeout(timeout)
    }
    
    timeout = setTimeout(() => {
      func(...args)
    }, wait)
  }
}

// 날짜 형식 변환 유틸리티
export const formatDate = (dateString: string): string => {
  if (!dateString) return ''
  
  const date = new Date(dateString)
  return date.toLocaleDateString('ko-KR', {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  })
}

// 시간 형식 변환 유틸리티
export const formatTime = (timeString: string): string => {
  if (!timeString) return ''
  
  const [hours, minutes] = timeString.split(':')
  const hour = parseInt(hours, 10)
  const period = hour >= 12 ? '오후' : '오전'
  const displayHour = hour === 0 ? 12 : hour > 12 ? hour - 12 : hour
  
  return `${period} ${displayHour}시 ${minutes}분`
}

// 나이 계산 유틸리티
export const calculateAge = (birthDate: string): number => {
  if (!birthDate) return 0
  
  const birth = new Date(birthDate)
  const today = new Date()
  
  let age = today.getFullYear() - birth.getFullYear()
  const monthDiff = today.getMonth() - birth.getMonth()
  
  if (monthDiff < 0 || (monthDiff === 0 && today.getDate() < birth.getDate())) {
    age--
  }
  
  return age
} 