module.exports = {
  apps: [{
    name: 'fastapi-sajuline',
    script: '/data/www/new-sajuline/backend/.venv/bin/uvicorn',
    args: 'src.main:app --host 0.0.0.0 --port 8000',
    cwd: '/data/www/new-sajuline/backend',
    interpreter: 'none',
    exec_mode: 'fork',
    instances: 1,
    autorestart: true,
    watch: false,
    max_memory_restart: '1G',
    error_file: './logs/pm2-error.log',
    out_file: './logs/pm2-out.log',
    log_date_format: 'YYYY-MM-DD HH:mm:ss',
    env: {
      NODE_ENV: 'development'
    }
  }]
}
