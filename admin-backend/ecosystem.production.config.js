module.exports = {
  apps: [{
    name: 'admin-api-sajuline',
    script: 'uv',
    args: 'run uvicorn src.main:app --host 0.0.0.0 --port 8001 --timeout-keep-alive 5 --access-log',
    cwd: '/data/www/new-sajuline/admin-backend',
    interpreter: 'none',
    exec_mode: 'fork',
    instances: 1,
    autorestart: true,
    watch: false,
    max_memory_restart: '512M',
    error_file: './logs/pm2-error.log',
    out_file: './logs/pm2-out.log',
    log_date_format: 'YYYY-MM-DD HH:mm:ss',
    env: {
      APP_ENV: 'production',
      ENVIRONMENT: 'production'
    }
  }]
}
