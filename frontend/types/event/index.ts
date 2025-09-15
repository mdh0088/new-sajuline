// 이벤트 타입 정의
export interface IEvent {
  id: number
  icon: string
  title: string
  period: string
  status: 'ongoing' | 'completed'
  description: string
  buttonText: string
  content?: string
  createdAt?: string
  updatedAt?: string
}

export interface IEventComment {
  id: number
  eventId: number
  userId: number
  userName: string
  content: string
  likeCount: number
  isLiked: boolean
  isAuthor: boolean
  createdAt: string
  updatedAt?: string
}