/**
 * RSS 피드 서버 라우트
 * 공지사항과 이벤트를 RSS 2.0 형식으로 제공
 */

interface NoticeItem {
  notice_id: number
  title: string
  content: string
  notice_type: string
  is_important: boolean
  created_at: string
}

interface EventItem {
  event_id: number
  event_name: string
  description: string | null
  valid_from: string
  valid_until: string
  created_at: string
}

interface APIResponse<T> {
  success: boolean
  data: T
  error?: { message: string }
}

// XML 특수문자 이스케이프
const escapeXml = (str: string): string => {
  return str
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&apos;')
}

// RSS 아이템 생성
const createRssItem = (
  title: string,
  link: string,
  description: string,
  pubDate: string,
  category: string
): string => {
  return `
    <item>
      <title><![CDATA[${title}]]></title>
      <link>${link}</link>
      <description><![CDATA[${description.slice(0, 300)}${description.length > 300 ? '...' : ''}]]></description>
      <pubDate>${new Date(pubDate).toUTCString()}</pubDate>
      <guid isPermaLink="true">${link}</guid>
      <category>${escapeXml(category)}</category>
    </item>`
}

export default defineEventHandler(async (event) => {
  const config = useRuntimeConfig()
  const siteUrl = config.public.siteUrl || 'https://sajuline.com'
  const apiBase = config.public.apiBase || '/api/v1'

  const items: string[] = []

  try {
    // 공지사항 가져오기
    const noticesRes = await $fetch<APIResponse<NoticeItem[]>>(`${apiBase}/notices/public`, {
      method: 'GET'
    }).catch(() => null)

    if (noticesRes?.success && noticesRes.data) {
      for (const notice of noticesRes.data.slice(0, 10)) {
        items.push(createRssItem(
          notice.title,
          `${siteUrl}/notices/${notice.notice_id}`,
          notice.content || '',
          notice.created_at,
          '공지사항'
        ))
      }
    }

    // 이벤트 가져오기
    const eventsRes = await $fetch<APIResponse<EventItem[]>>(`${apiBase}/events/public`, {
      method: 'GET'
    }).catch(() => null)

    if (eventsRes?.success && eventsRes.data) {
      for (const evt of eventsRes.data.slice(0, 10)) {
        items.push(createRssItem(
          evt.event_name,
          `${siteUrl}/events/${evt.event_id}`,
          evt.description || '',
          evt.created_at,
          '이벤트'
        ))
      }
    }
  } catch (err) {
    console.error('[RSS] Failed to fetch data:', err)
  }

  // 날짜 기준 정렬 (최신순)
  const sortedItems = items.length > 0 ? items : [
    createRssItem(
      '사주라인에 오신 것을 환영합니다',
      siteUrl,
      'AI와 전문가의 하이브리드 사주 상담 플랫폼입니다.',
      new Date().toISOString(),
      '안내'
    )
  ]

  const feed = `<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">
  <channel>
    <title>사주라인</title>
    <link>${siteUrl}</link>
    <description>AI와 전문가의 하이브리드 사주 상담 플랫폼 - 타로, 사주, 신점 전문 상담</description>
    <language>ko</language>
    <lastBuildDate>${new Date().toUTCString()}</lastBuildDate>
    <atom:link href="${siteUrl}/rss.xml" rel="self" type="application/rss+xml"/>
    <image>
      <url>${siteUrl}/images/og-image.jpg</url>
      <title>사주라인</title>
      <link>${siteUrl}</link>
    </image>
    <copyright>Copyright ${new Date().getFullYear()} 사주라인. All rights reserved.</copyright>
    <managingEditor>support@sajuline.com (사주라인)</managingEditor>
    <webMaster>support@sajuline.com (사주라인)</webMaster>
    <ttl>60</ttl>${sortedItems.join('')}
  </channel>
</rss>`

  setHeader(event, 'Content-Type', 'application/xml; charset=utf-8')
  setHeader(event, 'Cache-Control', 'max-age=3600, s-maxage=3600')

  return feed
})
