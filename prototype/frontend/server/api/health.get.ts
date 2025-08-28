/**
 * 프론트엔드 건강 체크 엔드포인트
 * 
 * Docker 컨테이너 상태 확인용
 * 로드밸런서 헬스체크에 사용
 */

export default defineEventHandler(async (event) => {
  try {
    // 기본 응용 프로그램 상태 확인
    const timestamp = new Date().toISOString()
    const uptime = process.uptime()
    const nodeVersion = process.version
    const platform = process.platform
    const arch = process.arch
    
    // 메모리 사용량 확인
    const memoryUsage = process.memoryUsage()
    const memory = {
      rss: Math.round(memoryUsage.rss / 1024 / 1024), // MB
      heapTotal: Math.round(memoryUsage.heapTotal / 1024 / 1024), // MB
      heapUsed: Math.round(memoryUsage.heapUsed / 1024 / 1024), // MB
      external: Math.round(memoryUsage.external / 1024 / 1024) // MB
    }
    
    // CPU 사용량 확인 (간단한 버전)
    const loadAverage = process.platform !== 'win32' ? require('os').loadavg() : [0, 0, 0]
    
    return {
      status: 'healthy',
      service: 'sajuline-frontend',
      version: '1.0.0',
      timestamp,
      uptime: Math.round(uptime),
      environment: process.env.NODE_ENV || 'development',
      system: {
        nodeVersion,
        platform,
        arch,
        memory,
        loadAverage: loadAverage.map((load: number) => Math.round(load * 100) / 100)
      },
      checks: {
        server: 'ok',
        memory: memory.heapUsed < 500 ? 'ok' : 'warning', // 500MB 이상 시 경고
        uptime: uptime > 5 ? 'ok' : 'starting' // 5초 이상 가동 시 정상
      }
    }
  } catch (error) {
    setResponseStatus(event, 503)
    return {
      status: 'unhealthy',
      service: 'sajuline-frontend',
      timestamp: new Date().toISOString(),
      error: error instanceof Error ? error.message : 'Unknown error',
      checks: {
        server: 'error'
      }
    }
  }
}) 