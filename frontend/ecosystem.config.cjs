module.exports = {
  apps: [{
    name: 'nuxt-sajuline',
    script: '.output/server/index.mjs',
    cwd: '/data/www/new-sajuline/frontend',
    interpreter: 'node',
    exec_mode: 'cluster',
    instances: 1,
    autorestart: true,
    watch: false,
    max_memory_restart: '1G',
    error_file: './logs/pm2-error.log',
    out_file: './logs/pm2-out.log',
    log_date_format: 'YYYY-MM-DD HH:mm:ss',
    env: {
      NODE_ENV: 'development',
      PORT: 3000,
      HOST: '0.0.0.0',
      NUXT_PUBLIC_CDN_BASE: 'https://cdn.sajuline.com/dev-upload/',
      NUXT_PUBLIC_API_BASE: '/api',
      NUXT_PROXY_TARGET: 'http://localhost:8000'

    }
  }]
}
