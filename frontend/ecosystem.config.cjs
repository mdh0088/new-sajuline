module.exports = {
  apps: [{
    name: 'nuxt-sajuline',
    script: '.output/server/index.mjs',
    cwd: '/data/www/new-sajuline/frontend',
    interpreter: 'node',
    exec_mode: 'cluster',
    instances: 2,
    autorestart: true,
    watch: false,
    max_memory_restart: '400M',
    error_file: './logs/pm2-error.log',
    out_file: './logs/pm2-out.log',
    log_date_format: 'YYYY-MM-DD HH:mm:ss',
    node_args: '--max-old-space-size=384',
    env: {
      NODE_ENV: 'development',
      PORT: 3000,
      HOST: '0.0.0.0',
      NUXT_PUBLIC_CDN_BASE: 'https://cdn.sajuline.com/dev-upload/',
      NUXT_PUBLIC_API_BASE: '/api',
      NUXT_PROXY_TARGET: 'http://localhost:8000'
    },
    env_production: {
      NODE_ENV: 'production',
      PORT: 3000,
      HOST: '0.0.0.0',
      NUXT_PUBLIC_CDN_BASE: 'https://cdn.sajuline.com/upload/',
      NUXT_PUBLIC_API_BASE: '/api',
      NUXT_PROXY_TARGET: 'http://localhost:8000'
    },
    env_development: {
      NODE_ENV: 'development',
      PORT: 3000,
      HOST: '0.0.0.0',
      NUXT_PUBLIC_CDN_BASE: 'https://cdn.sajuline.com/dev-upload/',
      NUXT_PUBLIC_API_BASE: '/api',
      NUXT_PROXY_TARGET: 'http://localhost:8000'
    }
  }]
}
