const http = require('http')

const options = {
  host: 'localhost',
  port: process.env.NUXT_PORT || 3000,
  timeout: 2000,
  method: 'GET',
  path: '/health'
}

const request = http.request(options, (res) => {
  console.log(`Health Check: ${res.statusCode}`)
  if (res.statusCode === 200) {
    process.exit(0)
  } else {
    process.exit(1)
  }
})

request.on('error', (err) => {
  console.error('Health Check Error:', err.message)
  process.exit(1)
})

request.on('timeout', () => {
  console.error('Health Check Timeout')
  request.abort()
  process.exit(1)
})

request.setTimeout(options.timeout)
request.end() 