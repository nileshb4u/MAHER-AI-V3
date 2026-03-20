# MAHER AI - Production Deployment Guide

This guide explains how to deploy MAHER AI in production mode using Waitress WSGI server.

## 🚨 Important: Development vs Production

**NEVER use `python app.py` in production!** This runs Flask's development server, which is:
- Not designed for production workloads
- Single-threaded and slow
- Lacks security hardening
- Can't handle concurrent requests efficiently

**ALWAYS use the production startup scripts** described below.

---

## Quick Start (Production Mode)

### For Windows:
```bash
# Run the production startup script
start_server.bat
```

### For Linux/Mac:
```bash
# Run the production startup script
./start_server.sh
```

That's it! The script will:
1. ✅ Check prerequisites
2. ✅ Activate virtual environment
3. ✅ Build frontend if needed
4. ✅ Start Waitress production server

---

## First-Time Setup

### 1. Install Dependencies

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install Python packages
pip install -r backend/requirements.txt

# Install Node.js packages
npm install
```

### 2. Configure Environment Variables

Create `backend/.env` file:

```bash
# Required: Your Gemini API Key
GEMINI_API_KEY=your_gemini_api_key_here

# Optional: Server Configuration
HOST=0.0.0.0
PORT=8080
THREADS=4

# Optional: Security
SECRET_KEY=your_secret_key_here
ALLOWED_ORIGINS=*

# Optional: HTTPS (if using reverse proxy)
USE_HTTPS=false
```

### 3. Build Frontend

```bash
npm run build
```

This creates the `dist/` folder with optimized production assets.

---

## Production Server Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `HOST` | `0.0.0.0` | Server bind address (0.0.0.0 = all interfaces) |
| `PORT` | `8080` | Server port |
| `THREADS` | `4` | Number of worker threads |
| `GEMINI_API_KEY` | *Required* | Your Google Gemini API key |
| `SECRET_KEY` | *Auto-generated* | Flask session secret key |
| `ALLOWED_ORIGINS` | `*` | CORS allowed origins (comma-separated) |
| `USE_HTTPS` | `false` | Set to `true` if behind HTTPS reverse proxy |

### Custom Configuration

Set environment variables before starting the server:

**Windows:**
```cmd
set HOST=127.0.0.1
set PORT=5000
set THREADS=8
start_server.bat
```

**Linux/Mac:**
```bash
export HOST=127.0.0.1
export PORT=5000
export THREADS=8
./start_server.sh
```

---

## Manual Production Start

If you prefer to run the production server manually:

```bash
# Activate virtual environment
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Change to backend directory
cd backend

# Run production server
python run_production.py
```

---

## Server Architecture

### Waitress WSGI Server

MAHER AI uses **Waitress**, a production-quality pure-Python WSGI server:

- ✅ **Multi-threaded**: Handles concurrent requests efficiently
- ✅ **Cross-platform**: Works on Windows, Linux, and Mac
- ✅ **Stable**: Battle-tested in production environments
- ✅ **Easy to configure**: No complex setup required
- ✅ **Pure Python**: No compilation needed

### Configuration Details

From `backend/run_production.py`:

```python
serve(
    app,
    host='0.0.0.0',
    port=8080,
    threads=4,                    # Worker threads
    connection_limit=1000,        # Max concurrent connections
    cleanup_interval=30,          # Connection cleanup (seconds)
    channel_timeout=120,          # Request timeout (seconds)
    asyncore_use_poll=True        # Better performance on Linux
)
```

---

## Security Features

MAHER AI includes several production security features:

### 1. API Key Protection
- ✅ Gemini API key stored server-side only
- ✅ Never exposed to client/browser
- ✅ All AI requests proxied through backend

### 2. Rate Limiting
- ✅ 60 requests/minute per IP for chat
- ✅ 20 requests/hour for knowledge uploads
- ✅ Prevents API abuse

### 3. Security Headers
- ✅ `X-Content-Type-Options: nosniff`
- ✅ `X-Frame-Options: DENY`
- ✅ `X-XSS-Protection: 1; mode=block`
- ✅ `Strict-Transport-Security` (HSTS)

### 4. CORS Configuration
- ✅ Configurable allowed origins
- ✅ Restricts API access to trusted domains

### 5. File Upload Validation
- ✅ File type validation (PDF, DOCX, TXT only)
- ✅ Size limits (10MB per file, 50MB total)
- ✅ Secure filename handling

---

## Monitoring and Logs

### Log File

The production server writes logs to `backend/maher_ai.log`:

```bash
# View recent logs (Linux/Mac)
tail -f backend/maher_ai.log

# View recent logs (Windows)
type backend\maher_ai.log
```

### Log Format

```
2025-11-12 14:54:57,569 - app - INFO - Starting MAHER AI Production Server on 0.0.0.0:8080
2025-11-12 14:54:57,570 - app - INFO - Using 4 threads
2025-11-12 15:00:01,234 - app - INFO - Chat request received
2025-11-12 15:00:02,567 - app - INFO - Chat response generated successfully
```

---

## Reverse Proxy Configuration (Optional)

For production deployments, consider using a reverse proxy like Nginx or Apache.

### Nginx Example

```nginx
server {
    listen 80;
    server_name yourdomain.com;

    location / {
        proxy_pass http://127.0.0.1:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # Timeouts for long AI responses
        proxy_read_timeout 300s;
        proxy_connect_timeout 75s;
    }

    # Increase upload size for knowledge files
    client_max_body_size 50M;
}
```

### Apache Example

```apache
<VirtualHost *:80>
    ServerName yourdomain.com

    ProxyPreserveHost On
    ProxyPass / http://127.0.0.1:8080/
    ProxyPassReverse / http://127.0.0.1:8080/

    # Timeouts for long AI responses
    ProxyTimeout 300

    # Increase upload size for knowledge files
    LimitRequestBody 52428800
</VirtualHost>
```

---

## Troubleshooting

### Issue: "dist folder not found"

**Problem:** Frontend hasn't been built yet.

**Solution:**
```bash
npm install
npm run build
```

### Issue: "Virtual environment not found"

**Problem:** Python virtual environment not created.

**Solution:**
```bash
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac
pip install -r backend/requirements.txt
```

### Issue: "GEMINI_API_KEY not found"

**Problem:** Environment variable not set.

**Solution:** Create `backend/.env` file with:
```
GEMINI_API_KEY=your_key_here
```

### Issue: Port already in use

**Problem:** Another process is using port 8080.

**Solution 1 - Use different port:**
```bash
export PORT=5000  # Linux/Mac
set PORT=5000     # Windows
```

**Solution 2 - Find and stop conflicting process:**

**Windows:**
```cmd
netstat -ano | findstr :8080
taskkill /PID <PID> /F
```

**Linux/Mac:**
```bash
lsof -i :8080
kill -9 <PID>
```

### Issue: 404 errors for static files

**Problem:** Frontend not built or dist folder missing.

**Solution:**
```bash
npm run build
```

### Issue: CORS errors in browser

**Problem:** Frontend domain not in ALLOWED_ORIGINS.

**Solution:** Update `backend/.env`:
```
ALLOWED_ORIGINS=https://yourdomain.com,http://localhost:3000
```

---

## Performance Tuning

### Adjust Worker Threads

For high-traffic deployments, increase thread count:

```bash
export THREADS=8  # Or higher based on CPU cores
./start_server.sh
```

**Recommendation:** Set threads to 2-4x your CPU cores.

### Connection Limits

Edit `backend/run_production.py`:

```python
serve(
    app,
    # ...
    connection_limit=2000,  # Increase for high traffic
    threads=8               # Match your CPU capacity
)
```

### Database Optimization

If you add database support, consider:
- Connection pooling
- Query optimization
- Caching layer (Redis)

---

## Systemd Service (Linux)

For automatic startup on Linux servers, create a systemd service:

**File: `/etc/systemd/system/maher-ai.service`**

```ini
[Unit]
Description=MAHER AI Virtual Maintenance Assistant
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/opt/maher-ai
Environment="PATH=/opt/maher-ai/venv/bin"
ExecStart=/opt/maher-ai/venv/bin/python /opt/maher-ai/backend/run_production.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

**Enable and start:**
```bash
sudo systemctl daemon-reload
sudo systemctl enable maher-ai
sudo systemctl start maher-ai
sudo systemctl status maher-ai
```

---

## Windows Service

For automatic startup on Windows, use **NSSM** (Non-Sucking Service Manager):

1. Download NSSM: https://nssm.cc/download
2. Install service:

```cmd
nssm install MAHER-AI "C:\path\to\venv\Scripts\python.exe" "C:\path\to\backend\run_production.py"
nssm set MAHER-AI AppDirectory "C:\path\to\backend"
nssm set MAHER-AI DisplayName "MAHER AI Virtual Assistant"
nssm set MAHER-AI Description "Production server for MAHER AI"
nssm start MAHER-AI
```

---

## Health Checks

Add health check endpoint to `backend/app.py`:

```python
@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint for monitoring"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat()
    }), 200
```

Use for monitoring:
```bash
curl http://localhost:8080/health
```

---

## Backup and Maintenance

### Backup Knowledge Storage

```bash
# Backup agent knowledge files
tar -czf knowledge_backup_$(date +%Y%m%d).tar.gz backend/knowledge_storage/
```

### Log Rotation

**Linux (logrotate):**

**File: `/etc/logrotate.d/maher-ai`**
```
/opt/maher-ai/backend/maher_ai.log {
    daily
    rotate 14
    compress
    delaycompress
    missingok
    notifempty
}
```

---

## Additional Resources

- **Flask Documentation**: https://flask.palletsprojects.com/
- **Waitress Documentation**: https://docs.pylonsproject.org/projects/waitress/
- **Gemini API**: https://ai.google.dev/docs
- **MAHER AI Repository**: [Your Git Repository URL]

---

## Support

For issues and questions:
1. Check this documentation
2. Review logs: `backend/maher_ai.log`
3. Check environment variables
4. Ensure all dependencies are installed

---

**Last Updated:** 2025-11-12
**Version:** 1.0.0
