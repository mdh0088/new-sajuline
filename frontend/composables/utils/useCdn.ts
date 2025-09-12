// 단순 CDN URL 유틸
// - 사용 예시
//   cdnUrl('cs', 'file.png')           => <BASE>/cs/file.png
//   cdnUrl('avatars', 'a/b.png')       => <BASE>/avatars/a/b.png
//   cdnUrl('cs/file.png')              => <BASE>/cs/file.png
//   cdnUrl('https://foo/bar.png')      => 그대로 반환
// - 인자가 없거나 BASE가 없으면 '' 반환
export const useCdn = () => {
  const config = useRuntimeConfig()
  // 우선 runtimeConfig.public.cdnBase → 클라이언트 빌드 상수(import.meta.env.NUXT_PUBLIC_CDN_BASE)
  const baseRaw: string =((config.public as any).cdnBase as string) ||''
  const base = baseRaw ? (baseRaw.endsWith('/') ? baseRaw : `${baseRaw}/`) : ''

  const isAbsoluteUrl = (v: string) => /^https?:\/\//i.test(v)
  const trimSlashes = (v: string) => v.replace(/^\/+|\/+$/g, '')

  const cdnUrl = (pathOrDir?: string | null, filename?: string | null): string => {
    if (!base) return ''
    const a = (pathOrDir || '').trim()
    const b = (filename || '').trim()

    if (!a && !b) return ''

    // 단일 인자: 절대 URL이면 그대로, 상대면 BASE와 결합
    if (!b) {
      if (isAbsoluteUrl(a)) return a
      const rel = trimSlashes(a)
      return rel ? `${base}${rel}` : ''
    }

    // 두 인자: 디렉터리/경로 + 파일명 결합
    const dir = trimSlashes(a)
    const name = trimSlashes(b)
    if (!name) return ''
    const joined = dir ? `${dir}/${name}` : name

    return `${base}${joined}`
  }

  return { cdnUrl }
}

