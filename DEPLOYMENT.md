# 🚀 MAHER AI - Production Deployment Guide

This guide provides comprehensive instructions for deploying MAHER AI to production using Flask and Waitress.

## 📋 Table of Contents

1. [Prerequisites](#prerequisites)
2. [Security Overview](#security-overview)
3. [Quick Start](#quick-start)
4. [Detailed Setup](#detailed-setup)
5. [Environment Configuration](#environment-configuration)
6. [Building for Production](#building-for-production)
7. [Deployment Options](#deployment-options)
8. [Reverse Proxy Setup](#reverse-proxy-setup)
9. [SSL/TLS Configuration](#ssltls-configuration)
10. [Monitoring & Maintenance](#monitoring--maintenance)
11. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### System Requirements

- **Operating System**: Linux (Ubuntu 20.04+ recommended), macOS, or Windows
- **Python**: 3.8 or higher
- **Node.js**: 18.x or higher
- **RAM**: Minimum 2GB, 4GB+ recommended
- **Storage**: At least 500MB free space

### Required Software

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install -y python3 python3-pip python3-venv nodejs npm nginx

# macOS (using Homebrew)
brew install python node nginx

# Verify installations
python3 --version
node --version
npm --version
```

---

## Security Overview

### 🔐 Security Features Implemented

1. **API Key Protection**
   - Gemini API key stored server-side only
   - Never exposed to client browser
   - Environment variable based configuration

2. **Rate Limiting**
   - 200 requests per day per IP
   - 50 requests per hour per IP
   - Specific endpoint limits (e.g., 30/min for chat)

3. **CORS Protection**
   - Configurable allowed origins
   - Prevents unauthorized cross-origin requests

4. **Security Headers**
   - X-Content-Type-Options: nosniff
   - X-Frame-Options: DENY
   - X-XSS-Protection: 1; mode=block
   - Strict-Transport-Security (HSTS)

5. **Input Validation**
   - Request size limits (16MB max)
   - Content-type validation
   - Timeout protection

---

## Quick Start

### 1. Clone & Configure

```bash
# Navigate to your project directory
cd /path/to/MAHER_NEW_UI

# Copy environment template
cp .env.example .env

# Edit .env and add your API keys
nano .env
```

**Required environment variables:**
```env
GEMINI_API_KEY=your_actual_gemini_api_key_here
SECRET_KEY=generate_a_secure_random_key_here
ALLOWED_ORIGINS=https://yourdomain.com
```

**Generate a secure SECRET_KEY:**
```bash
python3 -c "import secrets; print(secrets.token_hex(32))"
```

### 2. Deploy

```bash
# Make deployment script executable
chmod +x deploy.sh

# Run deployment
./deploy.sh
```

### 3. Start Server

```bash
# Activate virtual environment
source venv/bin/activate

# Start production server
cd backend && python wsgi.py
```

Your application will be available at `http://localhost:8080`

---

## Detailed Setup

### Step 1: Environment Configuration

Create a `.env` file in the project root with the following variables:

```env
# ================================
# GEMINI API CONFIGURATION
# ================================
# Get your API key from: https://makersuite.google.com/app/apikey
GEMINI_API_KEY=your_gemini_api_key_here

# ================================
# FLASK CONFIGURATION
# ================================
# Generate with: python -c "import secrets; print(secrets.token_hex(32))"
SECRET_KEY=your_secret_key_here

# Environment: development or production
FLASK_ENV=production

# ================================
# SERVER CONFIGURATION
# ================================
HOST=0.0.0.0
PORT=8080
THREADS=4

# ================================
# CORS CONFIGURATION
# ================================
# For production, replace * with your actual domain
ALLOWED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com

# ================================
# LOGGING
# ================================
LOG_LEVEL=INFO
```

### Step 2: Install Dependencies

#### Frontend Dependencies

```bash
npm install
```

#### Backend Dependencies

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate  # Linux/macOS
# or
venv\Scripts\activate  # Windows

# Install Python packages
pip install -r backend/requirements.txt
```

### Step 3: Build Frontend

```bash
npm run build
```

This creates an optimized production build in the `dist/` directory.

### Step 4: Test Backend

```bash
cd backend
python app.py
```

Visit `http://localhost:8080/api/health` to verify the backend is running.

---

## Building for Production

### Frontend Build

The production build is optimized with:
- Minification (Terser)
- Console.log removal
- Code splitting (vendor, markdown chunks)
- Tree shaking

```bash
npm run build
```

Output: `dist/` directory containing static files

### Backend Configuration

The backend (`backend/wsgi.py`) uses Waitress WSGI server:
- Production-grade WSGI server
- Handles concurrent requests efficiently
- Recommended for production deployment

---

## Deployment Options

### Option 1: Manual Start (Development/Testing)

```bash
source venv/bin/activate
cd backend
python wsgi.py
```

### Option 2: Systemd Service (Recommended for Production)

#### Setup Systemd Service

1. **Edit the service file** with your paths:

```bash
nano maher-ai.service
```

Update these lines:
```ini
WorkingDirectory=/path/to/MAHER_NEW_UI
Environment="PATH=/path/to/MAHER_NEW_UI/venv/bin"
EnvironmentFile=/path/to/MAHER_NEW_UI/.env
ExecStart=/path/to/MAHER_NEW_UI/venv/bin/python /path/to/MAHER_NEW_UI/backend/wsgi.py
```

2. **Install and start the service:**

```bash
# Copy service file
sudo cp maher-ai.service /etc/systemd/system/

# Reload systemd
sudo systemctl daemon-reload

# Enable service (start on boot)
sudo systemctl enable maher-ai

# Start service
sudo systemctl start maher-ai

# Check status
sudo systemctl status maher-ai
```

3. **Manage the service:**

```bash
# Stop service
sudo systemctl stop maher-ai

# Restart service
sudo systemctl restart maher-ai

# View logs
sudo journalctl -u maher-ai -f
```

### Option 3: Docker (Alternative)

Create a `Dockerfile`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install Node.js
RUN apt-get update && apt-get install -y nodejs npm

# Copy project files
COPY . .

# Build frontend
RUN npm install && npm run build

# Install Python dependencies
RUN pip install -r backend/requirements.txt

# Expose port
EXPOSE 8080

# Start server
CMD ["python", "backend/wsgi.py"]
```

Build and run:
```bash
docker build -t maher-ai .
docker run -p 8080:8080 --env-file .env maher-ai
```

---

## Reverse Proxy Setup

### Why Use a Reverse Proxy?

- SSL/TLS termination
- Load balancing
- Caching
- Better security
- Standard ports (80/443)

### Nginx Configuration

1. **Install Nginx:**

```bash
sudo apt install nginx
```

2. **Configure Nginx:**

```bash
# Copy example configuration
sudo cp nginx.conf.example /etc/nginx/sites-available/maher-ai

# Edit configuration with your domain
sudo nano /etc/nginx/sites-available/maher-ai

# Enable site
sudo ln -s /etc/nginx/sites-available/maher-ai /etc/nginx/sites-enabled/

# Test configuration
sudo nginx -t

# Reload Nginx
sudo systemctl reload nginx
```

3. **Update ALLOWED_ORIGINS in `.env`:**

```env
ALLOWED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
```

---

## SSL/TLS Configuration

### Using Let's Encrypt (Free SSL)

```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx

# Obtain certificate
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com

# Test auto-renewal
sudo certbot renew --dry-run
```

Certbot will automatically configure Nginx for HTTPS.

---

## Monitoring & Maintenance

### View Application Logs

```bash
# Application logs (if using systemd)
sudo journalctl -u maher-ai -f

# Application log file
tail -f maher_ai.log

# Nginx access logs
sudo tail -f /var/log/nginx/maher-ai-access.log

# Nginx error logs
sudo tail -f /var/log/nginx/maher-ai-error.log
```

### Health Check

```bash
curl http://localhost:8080/api/health
```

Expected response:
```json
{
  "status": "healthy",
  "service": "MAHER AI Backend",
  "version": "1.0.0"
}
```

### Performance Monitoring

Monitor server resources:

```bash
# CPU and memory usage
htop

# Active connections
sudo netstat -tuln | grep 8080

# Application process
ps aux | grep python
```

### Backup Strategy

**Important files to backup:**
- `.env` (API keys and configuration)
- Any user data or databases (if added in future)
- Custom configuration files

```bash
# Example backup script
tar -czf maher-backup-$(date +%Y%m%d).tar.gz \
  .env \
  backend/ \
  dist/
```

---

## Troubleshooting

### Common Issues

#### 1. API Key Not Found

**Error:** `GEMINI_API_KEY not found in environment variables`

**Solution:**
```bash
# Verify .env file exists
ls -la .env

# Check .env contents (don't share output publicly!)
cat .env | grep GEMINI_API_KEY

# Ensure no extra spaces or quotes
GEMINI_API_KEY=your_key_here  # Correct
GEMINI_API_KEY="your_key_here"  # May cause issues
GEMINI_API_KEY = your_key_here  # Spaces cause issues
```

#### 2. Port Already in Use

**Error:** `Address already in use`

**Solution:**
```bash
# Find process using port 8080
sudo lsof -i :8080

# Kill the process
sudo kill -9 <PID>

# Or change port in .env
PORT=8081
```

#### 3. CORS Errors

**Error:** `CORS policy: No 'Access-Control-Allow-Origin' header`

**Solution:**
```bash
# Update ALLOWED_ORIGINS in .env
ALLOWED_ORIGINS=https://yourdomain.com

# Restart the service
sudo systemctl restart maher-ai
```

#### 4. Rate Limit Exceeded

**Error:** `429 Too Many Requests`

**Solution:**
- Wait for rate limit window to reset
- Adjust rate limits in `backend/app.py`:
  ```python
  default_limits=["500 per day", "100 per hour"]
  ```

#### 5. Static Files Not Loading

**Issue:** Frontend shows blank page

**Solution:**
```bash
# Rebuild frontend
npm run build

# Verify dist/ directory exists
ls -la dist/

# Check backend static_folder setting in app.py
# Should be: static_folder='../dist'

# Restart backend
sudo systemctl restart maher-ai
```

### Debug Mode

For debugging issues, temporarily enable debug mode:

```env
# .env
FLASK_ENV=development
LOG_LEVEL=DEBUG
```

**⚠️ NEVER use debug mode in production!**

### Getting Help

If you encounter issues:
1. Check logs: `sudo journalctl -u maher-ai -f`
2. Verify environment variables: `cat .env`
3. Test health endpoint: `curl http://localhost:8080/api/health`
4. Review this documentation
5. Check Gemini API status: https://status.cloud.google.com/

---

## Security Best Practices

### ✅ Production Checklist

- [ ] `.env` file is not committed to git (check `.gitignore`)
- [ ] `GEMINI_API_KEY` is kept secret and secure
- [ ] `SECRET_KEY` is a strong random value
- [ ] `ALLOWED_ORIGINS` is set to your actual domain (not *)
- [ ] HTTPS/SSL is configured via reverse proxy
- [ ] Security headers are enabled (automatic in backend)
- [ ] Rate limiting is configured appropriately
- [ ] Server OS and packages are updated
- [ ] Firewall is configured (allow only 80, 443, SSH)
- [ ] Regular backups are scheduled
- [ ] Monitoring/alerting is set up
- [ ] Log files are rotated
- [ ] API usage is monitored

### Regular Maintenance

```bash
# Update system packages monthly
sudo apt update && sudo apt upgrade -y

# Rotate logs
sudo logrotate /etc/logrotate.d/nginx

# Monitor API usage and costs
# Check your Google Cloud Console
```

---

## Performance Optimization

### Backend Optimization

Adjust in `.env`:
```env
THREADS=8  # Increase for more concurrent requests
PORT=8080  # Default
```

### Frontend Optimization

Already configured:
- Gzip compression (via Nginx)
- Code splitting
- Minification
- Tree shaking

### Database (Future Enhancement)

Consider adding Redis for:
- Distributed rate limiting
- Session storage
- Caching responses

```bash
# Install Redis
sudo apt install redis-server

# Update .env
REDIS_URL=redis://localhost:6379/0
```

---

## Scaling

### Horizontal Scaling

Use multiple backend instances behind a load balancer:

```bash
# Start multiple instances on different ports
PORT=8080 python backend/wsgi.py &
PORT=8081 python backend/wsgi.py &
PORT=8082 python backend/wsgi.py &

# Configure Nginx load balancing
upstream maher_backend {
    server 127.0.0.1:8080;
    server 127.0.0.1:8081;
    server 127.0.0.1:8082;
}
```

---

## Support

For additional help or questions:
- Review the main README.md
- Check the Flask documentation: https://flask.palletsprojects.com/
- Waitress documentation: https://docs.pylonsproject.org/projects/waitress/
- Gemini API docs: https://ai.google.dev/docs

---

**Last Updated:** 2025-01-10
**Version:** 1.0.0
