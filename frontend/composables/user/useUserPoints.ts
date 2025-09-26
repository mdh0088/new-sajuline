import { useState } from 'nuxt/app'

export const useUserPoints = () => {
  const points = useState<number>('current_user_points', () => 0)

  const setPoints = (value: number | string | null | undefined) => {
    const n = typeof value === 'string' ? Number(value) : Number(value ?? 0)
    points.value = isNaN(n) ? 0 : n
  }

  return { points, setPoints }
}


