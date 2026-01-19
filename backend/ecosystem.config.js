module.exports = {
  apps: [{
    name: 'fastapi-sajuline',
    script: 'uv',
    args: 'run gunicorn src.main:app -w 2 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000 --timeout 120 --graceful-timeout 30 --keep-alive 5 --access-logfile - --error-logfile -',
    cwd: '/data/www/new-sajuline/backend',
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
    },
    env_production: {
      APP_ENV: 'production',
      ENVIRONMENT: 'production'
    },
    env_development: {
      APP_ENV: 'development',
      ENVIRONMENT: 'development'
    }
  }]
}
