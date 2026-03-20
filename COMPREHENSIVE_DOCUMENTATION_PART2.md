# MAHER AI - Comprehensive Documentation (Part 2)

*Continued from Part 1*

---

## 🔒 Security

### Security Features

#### 1. Rate Limiting

**Flask-Limiter** configuration:

```python
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"],
    storage_uri=os.environ.get('REDIS_URL', 'memory://')
)
```

**Per-Endpoint Limits:**
```python
@app.route('/api/hybrid-orchestrator/process', methods=['POST'])
@limiter.limit("30 per minute")
def hybrid_orchestrator_process():
    # Handler code
```

**Rate Limit Response:**
```json
{
  "error": "Rate limit exceeded",
  "message": "Too many requests. Please try again later."
}
```

#### 2. CORS Protection

**Configuration:**
```python
ALLOWED_ORIGINS = os.environ.get('ALLOWED_ORIGINS', '*').split(',')

CORS(app, resources={
    r"/api/*": {
        "origins": ALLOWED_ORIGINS,
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"],
        "max_age": 3600
    }
})
```

**Production Settings:**
```bash
# .env
ALLOWED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
```

#### 3. Security Headers

**Middleware:**
```python
@app.after_request
def add_security_headers(response):
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'

    # No cache for API responses
    if request.path.startswith('/api/'):
        response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'

    return response
```

#### 4. Input Validation

**File Upload Validation:**
```python
def validate_file_upload(file):
    # Check file exists
    if not file or file.filename == '':
        raise ValueError("No file provided")

    # Check file extension
    allowed_extensions = {'.pdf', '.doc', '.docx', '.xls', '.xlsx'}
    ext = os.path.splitext(file.filename.lower())[1]
    if ext not in allowed_extensions:
        raise ValueError(f"File type {ext} not allowed")

    # Check file size
    max_size = 2 * 1024 * 1024  # 2MB
    file.seek(0, os.SEEK_END)
    size = file.tell()
    file.seek(0)  # Reset
    if size > max_size:
        raise ValueError(f"File size exceeds 2MB limit ({size / (1024*1024):.2f} MB)")

    # Secure filename
    from werkzeug.utils import secure_filename
    safe_filename = secure_filename(file.filename)

    return safe_filename
```

**API Input Validation:**
```python
def validate_agent_input(data):
    required_fields = ['name', 'description', 'systemPrompt', 'category']

    for field in required_fields:
        if field not in data or not data[field]:
            raise ValueError(f'Missing required field: {field}')

    # Validate lengths
    if len(data['name']) > 200:
        raise ValueError('Name too long (max 200 characters)')

    if len(data['description']) > 5000:
        raise ValueError('Description too long (max 5000 characters)')

    # Sanitize HTML/script tags
    import re
    for field in ['name', 'description']:
        if re.search(r'<script|<iframe|javascript:', data[field], re.I):
            raise ValueError(f'Invalid content in {field}')

    return True
```

#### 5. API Key Protection

**Environment Variables:**
```bash
# Never commit API keys to git
GEMINI_API_KEY=your_secret_key_here
```

**Key Validation:**
```python
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')
if not GEMINI_API_KEY:
    logger.error("GEMINI_API_KEY not found!")
    raise ValueError("GEMINI_API_KEY must be set")
```

**Secure Key Storage:**
- Use environment variables (not hardcoded)
- Use secrets management (AWS Secrets Manager, Azure Key Vault)
- Rotate keys regularly
- Use different keys for dev/staging/prod

#### 6. SQL Injection Prevention

**SQLAlchemy ORM** (parameterized queries):
```python
# ✅ Safe - Using ORM
agent = db.query(Agent).filter(
    Agent.agent_id == agent_id
).first()

# ❌ Unsafe - Raw SQL with string concatenation
# db.execute(f"SELECT * FROM agents WHERE agent_id = '{agent_id}'")
```

#### 7. Path Traversal Prevention

**File Access Protection:**
```python
def safe_file_path(filename, base_dir):
    # Secure filename
    filename = secure_filename(filename)

    # Build full path
    full_path = os.path.abspath(os.path.join(base_dir, filename))

    # Ensure path is within base directory
    if not full_path.startswith(os.path.abspath(base_dir)):
        raise ValueError("Path traversal detected")

    return full_path
```

### Security Checklist

- [ ] **Environment Variables**: All secrets in `.env`, not in code
- [ ] **HTTPS**: SSL/TLS certificate installed
- [ ] **CORS**: Production domains whitelisted
- [ ] **Rate Limiting**: Appropriate limits per endpoint
- [ ] **Input Validation**: All user inputs validated
- [ ] **File Upload**: Size, type, and content validation
- [ ] **SQL Injection**: Using ORM, no raw SQL
- [ ] **XSS Protection**: Security headers enabled
- [ ] **CSRF Protection**: For state-changing operations
- [ ] **Error Handling**: Don't expose stack traces to users
- [ ] **Logging**: Log security events, but not sensitive data
- [ ] **Dependencies**: Keep libraries up to date
- [ ] **Access Control**: User authentication (if multi-tenant)

### Common Vulnerabilities to Avoid

#### 1. API Key Exposure

❌ **Bad:**
```python
GEMINI_API_KEY = "AIzaSyC..."  # Hardcoded
```

✅ **Good:**
```python
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')
```

#### 2. SQL Injection

❌ **Bad:**
```python
query = f"SELECT * FROM agents WHERE name = '{user_input}'"
```

✅ **Good:**
```python
agents = db.query(Agent).filter(Agent.name == user_input).all()
```

#### 3. Path Traversal

❌ **Bad:**
```python
file_path = f"uploads/{user_filename}"
```

✅ **Good:**
```python
file_path = safe_file_path(user_filename, 'uploads/')
```

#### 4. XSS Attacks

❌ **Bad:**
```javascript
innerHTML = userInput;  // Unsafe
```

✅ **Good:**
```javascript
textContent = userInput;  // Safe
// Or use React (automatically escapes)
```

---

## 🚀 Deployment

### Production Deployment Options

#### Option 1: Linux Server (Ubuntu/RHEL)

**Requirements:**
- Ubuntu 20.04+ or RHEL 8+
- Python 3.10+
- Node.js 18+
- Nginx
- systemd

**Steps:**

1. **Install Dependencies**

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python 3.10
sudo apt install python3.10 python3.10-venv python3-pip -y

# Install Node.js 18
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install nodejs -y

# Install Nginx
sudo apt install nginx -y

# Install Git
sudo apt install git -y
```

2. **Clone Repository**

```bash
cd /var/www
sudo git clone https://github.com/nileshb4u/MAHER_NEW_UI.git
cd MAHER_NEW_UI
sudo chown -R $USER:$USER .
```

3. **Configure Environment**

```bash
# Copy environment template
cp .env.example .env

# Edit with your values
nano .env
```

4. **Build Frontend**

```bash
npm install
npm run build
```

5. **Setup Backend**

```bash
cd backend

# Create virtual environment
python3.10 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Initialize database
python seed_db.py
```

6. **Configure systemd Service**

```bash
# Copy service file
sudo cp maher-ai.service /etc/systemd/system/

# Edit if needed
sudo nano /etc/systemd/system/maher-ai.service

# Enable and start
sudo systemctl daemon-reload
sudo systemctl enable maher-ai
sudo systemctl start maher-ai

# Check status
sudo systemctl status maher-ai
```

**maher-ai.service:**
```ini
[Unit]
Description=MAHER AI Backend Service
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/var/www/MAHER_NEW_UI/backend
Environment="PATH=/var/www/MAHER_NEW_UI/backend/venv/bin"
ExecStart=/var/www/MAHER_NEW_UI/backend/venv/bin/python run_production.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

7. **Configure Nginx**

```bash
# Copy Nginx config
sudo cp nginx.conf.example /etc/nginx/sites-available/maher-ai

# Create symlink
sudo ln -s /etc/nginx/sites-available/maher-ai /etc/nginx/sites-enabled/

# Test configuration
sudo nginx -t

# Reload Nginx
sudo systemctl reload nginx
```

**nginx.conf:**
```nginx
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;

    # Redirect to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com www.yourdomain.com;

    # SSL Configuration
    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;

    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;

    # Root directory for static files
    root /var/www/MAHER_NEW_UI/dist;
    index index.html;

    # Frontend routes
    location / {
        try_files $uri $uri/ /index.html;
    }

    # API proxy
    location /api/ {
        proxy_pass http://127.0.0.1:8080;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
        proxy_read_timeout 60s;
    }

    # Security headers
    add_header X-Frame-Options "DENY" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;

    # Logging
    access_log /var/log/nginx/maher-ai-access.log;
    error_log /var/log/nginx/maher-ai-error.log;
}
```

8. **Setup SSL with Let's Encrypt**

```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx -y

# Obtain certificate
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com

# Auto-renewal (already configured)
sudo systemctl status certbot.timer
```

9. **Configure Firewall**

```bash
# Allow HTTP, HTTPS, SSH
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# Enable firewall
sudo ufw enable
```

10. **Verify Deployment**

```bash
# Check service status
sudo systemctl status maher-ai

# Check Nginx status
sudo systemctl status nginx

# View logs
sudo journalctl -u maher-ai -f
sudo tail -f /var/log/nginx/maher-ai-error.log
```

#### Option 2: Docker Deployment

**Dockerfile:**
```dockerfile
# Frontend build stage
FROM node:18 AS frontend-build
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

# Backend stage
FROM python:3.10-slim
WORKDIR /app

# Install dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy backend files
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/ .
COPY --from=frontend-build /app/dist /app/dist

# Initialize database
RUN python seed_db.py

# Expose port
EXPOSE 8080

# Run application
CMD ["python", "run_production.py"]
```

**docker-compose.yml:**
```yaml
version: '3.8'

services:
  maher-ai:
    build: .
    ports:
      - "8080:8080"
    environment:
      - GEMINI_API_KEY=${GEMINI_API_KEY}
      - PORT=8080
      - FLASK_ENV=production
      - ALLOWED_ORIGINS=https://yourdomain.com
    volumes:
      - ./backend/data:/app/data
      - ./backend/knowledge_storage:/app/knowledge_storage
    restart: unless-stopped

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/conf.d/default.conf
      - ./dist:/usr/share/nginx/html
      - /etc/letsencrypt:/etc/letsencrypt:ro
    depends_on:
      - maher-ai
    restart: unless-stopped
```

**Build and Run:**
```bash
# Build image
docker-compose build

# Start containers
docker-compose up -d

# View logs
docker-compose logs -f maher-ai

# Stop containers
docker-compose down
```

#### Option 3: Windows Server

See `SANDBOX_OFFLINE_DEPLOYMENT_GUIDE.md` for detailed Windows deployment instructions.

### Environment-Specific Configuration

#### Development

```bash
# .env.development
FLASK_ENV=development
ALLOWED_ORIGINS=*
PORT=5000
```

#### Staging

```bash
# .env.staging
FLASK_ENV=production
ALLOWED_ORIGINS=https://staging.yourdomain.com
PORT=8080
REDIS_URL=redis://localhost:6379/0
```

#### Production

```bash
# .env.production
FLASK_ENV=production
ALLOWED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
PORT=8080
REDIS_URL=redis://prod-redis.yourdomain.com:6379/0
SECRET_KEY=<long-random-string>
```

### Monitoring & Logging

#### Application Logs

```bash
# systemd logs
sudo journalctl -u maher-ai -f

# Python logs
tail -f backend/logs/app.log

# Nginx logs
tail -f /var/log/nginx/maher-ai-access.log
tail -f /var/log/nginx/maher-ai-error.log
```

#### Health Monitoring

**Uptime Check:**
```bash
# Simple health check script
#!/bin/bash
response=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8080/api/health)

if [ $response -eq 200 ]; then
    echo "Service healthy"
else
    echo "Service unhealthy: HTTP $response"
    # Alert or restart service
    sudo systemctl restart maher-ai
fi
```

**Setup Cron Job:**
```bash
# Edit crontab
crontab -e

# Add health check every 5 minutes
*/5 * * * * /path/to/health_check.sh
```

#### Performance Monitoring

**Tools:**
- **Prometheus + Grafana**: Metrics and dashboards
- **ELK Stack**: Centralized logging
- **New Relic / Datadog**: APM

**Custom Metrics:**
```python
# Add to app.py
from prometheus_flask_exporter import PrometheusMetrics

metrics = PrometheusMetrics(app)
metrics.info('app_info', 'MAHER AI Application', version='1.0.0')
```

### Backup & Recovery

#### Database Backup

```bash
# Backup script
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/var/backups/maher-ai"
DB_PATH="/var/www/MAHER_NEW_UI/backend/data/maher_ai.db"

mkdir -p $BACKUP_DIR

# Backup database
cp $DB_PATH $BACKUP_DIR/maher_ai_$DATE.db

# Backup knowledge storage
tar -czf $BACKUP_DIR/knowledge_$DATE.tar.gz \
    /var/www/MAHER_NEW_UI/backend/knowledge_storage/

# Keep only last 7 days
find $BACKUP_DIR -type f -mtime +7 -delete

echo "Backup completed: $DATE"
```

**Automated Backups:**
```bash
# Daily backup at 2 AM
0 2 * * * /path/to/backup.sh
```

#### Restore

```bash
# Stop service
sudo systemctl stop maher-ai

# Restore database
cp /var/backups/maher-ai/maher_ai_20251113.db \
   /var/www/MAHER_NEW_UI/backend/data/maher_ai.db

# Restore knowledge
tar -xzf /var/backups/maher-ai/knowledge_20251113.tar.gz \
    -C /var/www/MAHER_NEW_UI/backend/

# Start service
sudo systemctl start maher-ai
```

### Scaling

#### Horizontal Scaling

1. **Load Balancer** (Nginx)

```nginx
upstream maher_backend {
    server 127.0.0.1:8080;
    server 127.0.0.1:8081;
    server 127.0.0.1:8082;
}

server {
    location /api/ {
        proxy_pass http://maher_backend;
    }
}
```

2. **Run Multiple Instances**

```bash
# Instance 1
PORT=8080 python run_production.py &

# Instance 2
PORT=8081 python run_production.py &

# Instance 3
PORT=8082 python run_production.py &
```

3. **Shared State** (Redis)

```python
# Use Redis for rate limiting
limiter = Limiter(
    app=app,
    storage_uri='redis://localhost:6379/0'
)
```

#### Vertical Scaling

- Increase server resources (CPU, RAM)
- Tune Waitress threads:
  ```python
  serve(app, host='0.0.0.0', port=8080, threads=8)
  ```
- Database optimization (indexes, query tuning)

---

## 👨‍💻 Development Guide

### Setting Up Development Environment

#### 1. Prerequisites

- Python 3.10+
- Node.js 18+
- Git
- Code editor (VS Code recommended)

#### 2. Clone and Setup

```bash
# Clone repository
git clone https://github.com/nileshb4u/MAHER_NEW_UI.git
cd MAHER_NEW_UI

# Install frontend dependencies
npm install

# Setup backend
cd backend
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows
pip install -r requirements.txt
cd ..

# Configure environment
cp .env.example .env
# Edit .env with your API keys
```

#### 3. Run Development Servers

**Terminal 1 - Backend:**
```bash
cd backend
source venv/bin/activate
python app.py
```

**Terminal 2 - Frontend:**
```bash
npm run dev
```

Open: `http://localhost:5173` (Vite dev server)

### Project Conventions

#### Code Style

**Python (PEP 8):**
- 4 spaces for indentation
- Max line length: 100 characters
- Use docstrings for functions/classes
- Type hints preferred

```python
def process_request(user_input: str, timeout: int = 30) -> Dict[str, Any]:
    """
    Process user request through orchestrator

    Args:
        user_input: User's query
        timeout: Request timeout in seconds

    Returns:
        Orchestrated response dictionary
    """
    # Implementation
```

**TypeScript/React:**
- 2 spaces for indentation
- Use functional components
- Props destructuring
- TypeScript interfaces for props

```typescript
interface ChatProps {
  messages: Message[];
  setMessages: React.Dispatch<React.SetStateAction<Message[]>>;
}

const Chat: React.FC<ChatProps> = ({ messages, setMessages }) => {
  // Component implementation
};
```

#### Naming Conventions

| Type | Convention | Example |
|------|-----------|---------|
| **Python Variables** | snake_case | `user_input`, `agent_id` |
| **Python Functions** | snake_case | `get_agent()`, `process_request()` |
| **Python Classes** | PascalCase | `HybridOrchestrator`, `Agent` |
| **Python Constants** | UPPER_SNAKE_CASE | `GEMINI_API_KEY`, `MAX_FILE_SIZE` |
| **TypeScript Variables** | camelCase | `userInput`, `agentId` |
| **TypeScript Functions** | camelCase | `getAgent()`, `processRequest()` |
| **React Components** | PascalCase | `Chat`, `Landing`, `AgentCard` |
| **TypeScript Types** | PascalCase | `Message`, `AppView`, `Agent` |
| **CSS Classes** | kebab-case | `chat-container`, `agent-card` |

#### File Structure

**Backend:**
```
backend/
├── app.py                  # Main Flask app
├── models.py               # Database models
├── hybrid_orchestrator.py  # Orchestrator logic
├── file_parser.py          # Utilities
├── workflows/              # Workflow modules
│   └── *.py
├── tools/                  # Tool modules
│   └── *.py
└── tests/                  # Tests (to be added)
    └── *.py
```

**Frontend:**
```
/
├── components/
│   ├── Chat.tsx
│   ├── Landing.tsx
│   └── icons/
├── App.tsx
├── api.ts
├── constants.ts
└── types.ts
```

### Git Workflow

#### Branching Strategy

```
main (production)
  └── develop (staging)
       └── feature/add-new-workflow
       └── bugfix/fix-rate-limiting
       └── hotfix/critical-security-fix
```

#### Commit Messages

**Format:**
```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation
- `style`: Formatting
- `refactor`: Code restructuring
- `test`: Tests
- `chore`: Maintenance

**Examples:**
```
feat(orchestrator): Add parallel execution support

- Implement asyncio.gather for parallel tasks
- Add execution_strategy field to decomposition
- Update result integration logic

Closes #123
```

```
fix(api): Handle rate limit errors gracefully

Return proper error message instead of 500 when rate limit exceeded.

Fixes #456
```

#### Pull Request Process

1. **Create Feature Branch**
```bash
git checkout -b feature/my-feature
```

2. **Make Changes and Commit**
```bash
git add .
git commit -m "feat: Add my feature"
```

3. **Push Branch**
```bash
git push origin feature/my-feature
```

4. **Create PR on GitHub**
- Fill out PR template
- Assign reviewers
- Link related issues

5. **Address Review Comments**
```bash
git add .
git commit -m "fix: Address review comments"
git push origin feature/my-feature
```

6. **Merge After Approval**

### Adding New Features

#### Example: Add New Workflow

1. **Create Workflow Module**

```python
# backend/workflows/equipment_health.py

async def check_equipment_health(equipment_id: str) -> Dict[str, Any]:
    """
    Check equipment health status

    Args:
        equipment_id: Equipment identifier

    Returns:
        Health status and recommendations
    """
    # Your implementation
    health_score = calculate_health(equipment_id)

    return {
        "success": True,
        "equipment_id": equipment_id,
        "health_score": health_score,
        "status": "good" if health_score > 80 else "needs_attention",
        "recommendations": [...]
    }
```

2. **Register in Registry**

```json
{
  "resources": {
    "workflows": [
      {
        "id": "workflow_equipment_health",
        "name": "Equipment Health Checker",
        "description": "Assesses equipment health",
        "capabilities": ["health_check", "equipment_monitoring"],
        "module_path": "workflows.equipment_health",
        "function": "check_equipment_health",
        "parameters": {
          "equipment_id": "string"
        },
        "execution_type": "async",
        "timeout": 15,
        "priority": 2,
        "dependencies": []
      }
    ]
  },
  "capability_index": {
    "health_check": ["workflow_equipment_health"],
    "equipment_monitoring": ["workflow_equipment_health"]
  }
}
```

3. **Test Workflow**

```bash
cd backend
python test_hybrid_orchestrator.py
```

4. **Update Frontend Formatting** (if needed)

```typescript
// components/Chat.tsx

// Add to result formatting
if (data.health_score) {
  responseText += `**Health Score:** ${data.health_score}/100\n`;
  responseText += `**Status:** ${data.status}\n\n`;

  if (data.recommendations) {
    responseText += `**Recommendations:**\n`;
    data.recommendations.forEach((rec: string) => {
      responseText += `- ${rec}\n`;
    });
  }
}
```

5. **Test End-to-End**

Query: "Check health of equipment PUMP-001"

Verify:
- Workflow is matched
- Executes successfully
- Results display properly

6. **Document**

Add to `HYBRID_ORCHESTRATOR_README.md` in "Available Workflows" section.

### Debugging

#### Backend Debugging

**VS Code Launch Configuration** (`.vscode/launch.json`):

```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Python: Flask",
      "type": "python",
      "request": "launch",
      "module": "flask",
      "env": {
        "FLASK_APP": "app.py",
        "FLASK_ENV": "development"
      },
      "args": [
        "run",
        "--no-debugger",
        "--no-reload"
      ],
      "jinja": true,
      "cwd": "${workspaceFolder}/backend"
    }
  ]
}
```

**Logging:**
```python
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

logger.debug("Debug message")
logger.info("Info message")
logger.error("Error message")
```

**Interactive Debugger:**
```python
# Add breakpoint
import pdb; pdb.set_trace()
```

#### Frontend Debugging

**Browser DevTools:**
- F12 to open
- Console tab for logs
- Network tab for API calls
- React DevTools extension

**Console Logging:**
```typescript
console.log('User input:', input);
console.error('Error:', error);
console.table(agents);
```

**React DevTools:**
- Install extension
- Inspect component props/state
- Profiler for performance

---

## 🐛 Troubleshooting

### Common Issues

#### 1. "Connection refused" Error

**Symptoms:**
```
Error: connect ECONNREFUSED 127.0.0.1:8080
```

**Solutions:**
- Check backend server is running: `ps aux | grep python`
- Check correct port: `PORT=8080 python run_production.py`
- Check firewall: `sudo ufw status`

#### 2. "GEMINI_API_KEY not found"

**Symptoms:**
```
ValueError: GEMINI_API_KEY must be set in environment variables
```

**Solutions:**
- Create `.env` file from `.env.example`
- Add key: `GEMINI_API_KEY=your_key_here`
- Restart server

#### 3. Rate Limit Exceeded (429)

**Symptoms:**
```json
{
  "error": "Rate limit exceeded",
  "message": "429 Client Error: Too Many Requests"
}
```

**Solutions:**
- Wait for rate limit reset
- Check Gemini API quota: https://console.cloud.google.com/apis/dashboard
- Upgrade API plan if needed
- Use workflows/tools to reduce API calls

#### 4. File Upload Failed

**Symptoms:**
```
Error: Failed to process attached files
```

**Solutions:**
- Check file size < 2MB
- Check file type (PDF, DOCX, XLSX only)
- Check `temp_uploads/` directory exists and is writable
- Check disk space: `df -h`

#### 5. Database Locked

**Symptoms:**
```
sqlite3.OperationalError: database is locked
```

**Solutions:**
- Close all database connections
- Check no other processes using DB
- Restart backend server
- For production, consider PostgreSQL

#### 6. Import Error

**Symptoms:**
```
ModuleNotFoundError: No module named 'workflows.maintenance_checklist'
```

**Solutions:**
- Check `__init__.py` exists in workflows/tools directories
- Check PYTHONPATH includes backend directory
- Activate virtual environment
- Reinstall dependencies: `pip install -r requirements.txt`

#### 7. Frontend Build Error

**Symptoms:**
```
Error: vite: not found
```

**Solutions:**
- Install dependencies: `npm install`
- Clear cache: `rm -rf node_modules package-lock.json && npm install`
- Check Node version: `node --version` (need 18+)

#### 8. "Agent not found" Error

**Symptoms:**
```json
{
  "success": false,
  "error": "Agent not found"
}
```

**Solutions:**
- Check agent_id is correct
- Verify agent exists: `GET /api/agents`
- Check agent status is "published"
- Reseed database: `python seed_db.py`

### Debugging Steps

1. **Check Logs**
```bash
# Backend logs
sudo journalctl -u maher-ai -f

# Nginx logs
sudo tail -f /var/log/nginx/error.log

# Python logs
tail -f backend/logs/app.log
```

2. **Test API Endpoints**
```bash
# Health check
curl http://localhost:8080/api/health

# List agents
curl http://localhost:8080/api/agents

# Process request
curl -X POST http://localhost:8080/api/hybrid-orchestrator/process \
  -H "Content-Type: application/json" \
  -d '{"input": "Generate a checklist"}'
```

3. **Check Database**
```bash
cd backend
sqlite3 data/maher_ai.db

# List agents
SELECT agent_id, name, status FROM agents;

# Exit
.quit
```

4. **Verify Environment**
```bash
# Check Python version
python --version

# Check installed packages
pip list

# Check Node version
node --version

# Check npm version
npm --version
```

5. **Test Individual Components**
```bash
# Test workflow directly
cd backend
python -c "
import asyncio
from workflows.maintenance_checklist import generate_checklist

result = asyncio.run(generate_checklist('pump', 'preventive'))
print(result)
"
```

### Performance Issues

#### Slow Response Times

**Diagnosis:**
```python
import time

start = time.time()
# Your code
duration = time.time() - start
logger.info(f"Operation took {duration:.2f}s")
```

**Solutions:**
- Use workflows/tools instead of AI agents
- Enable parallel execution
- Optimize database queries (add indexes)
- Use Redis for caching
- Increase server resources

#### High Memory Usage

**Diagnosis:**
```bash
# Check memory usage
free -h

# Check process memory
ps aux --sort=-%mem | head
```

**Solutions:**
- Limit file upload size
- Clear temp files regularly
- Use streaming for large files
- Increase server RAM
- Use connection pooling

#### High CPU Usage

**Diagnosis:**
```bash
# Check CPU usage
top

# Check process CPU
ps aux --sort=-%cpu | head
```

**Solutions:**
- Reduce Waitress threads (fewer concurrent requests)
- Optimize computationally expensive workflows
- Use asynchronous I/O
- Scale horizontally (multiple instances)

---

## 🧪 Testing

### Manual Testing

#### Test Checklist

**Frontend:**
- [ ] Landing page loads
- [ ] Can navigate to all views
- [ ] Chat interface accepts input
- [ ] File attachment works
- [ ] Markdown renders correctly
- [ ] Responsive on mobile

**Backend:**
- [ ] Health check returns 200
- [ ] Can list agents
- [ ] Can create/update/delete agents
- [ ] Can upload knowledge files
- [ ] Hybrid orchestrator processes requests
- [ ] Rate limiting works
- [ ] Error handling works

**Integration:**
- [ ] Chat sends request to orchestrator
- [ ] Results display correctly
- [ ] Workflows execute successfully
- [ ] Tools return data
- [ ] AI agents respond
- [ ] Feedback submission works

### Automated Testing

#### Backend Tests

**Create:** `backend/tests/test_orchestrator.py`

```python
import unittest
import asyncio
from hybrid_orchestrator import HybridOrchestrator

class TestHybridOrchestrator(unittest.TestCase):

    def setUp(self):
        self.orchestrator = HybridOrchestrator(
            registry_path='registry.json',
            gemini_api_key='test_key'
        )

    def test_decompose_task(self):
        """Test task decomposition"""
        result = asyncio.run(
            self.orchestrator.decompose_task("Generate a checklist")
        )

        self.assertIn('subtasks', result)
        self.assertGreater(len(result['subtasks']), 0)

    def test_match_resources(self):
        """Test resource matching"""
        subtask = {
            'required_capabilities': ['maintenance_planning']
        }

        resources = self.orchestrator.match_resources(subtask)

        self.assertGreater(len(resources), 0)
        self.assertEqual(resources[0]['type'], 'workflow')

if __name__ == '__main__':
    unittest.main()
```

**Run Tests:**
```bash
cd backend
python -m unittest discover tests/
```

#### Frontend Tests (Future)

**Using Jest + React Testing Library:**

```bash
npm install --save-dev @testing-library/react @testing-library/jest-dom jest
```

**Example:** `components/__tests__/Chat.test.tsx`

```typescript
import { render, screen, fireEvent } from '@testing-library/react';
import Chat from '../Chat';

test('renders chat input', () => {
  render(<Chat messages={[]} setMessages={() => {}} />);

  const input = screen.getByPlaceholderText(/Ask a follow-up/i);
  expect(input).toBeInTheDocument();
});

test('sends message on submit', () => {
  const setMessages = jest.fn();
  render(<Chat messages={[]} setMessages={setMessages} />);

  const input = screen.getByPlaceholderText(/Ask a follow-up/i);
  const button = screen.getByLabelText(/Send message/i);

  fireEvent.change(input, { target: { value: 'Test message' } });
  fireEvent.click(button);

  expect(setMessages).toHaveBeenCalled();
});
```

### Performance Testing

**Load Testing with Locust:**

```python
# locustfile.py
from locust import HttpUser, task, between

class MAHERUser(HttpUser):
    wait_time = between(1, 3)

    @task
    def health_check(self):
        self.client.get("/api/health")

    @task(3)
    def process_request(self):
        self.client.post("/api/hybrid-orchestrator/process", json={
            "input": "Generate a maintenance checklist"
        })

    @task(2)
    def list_agents(self):
        self.client.get("/api/agents")
```

**Run:**
```bash
locust -f locustfile.py --host=http://localhost:8080
```

---

## 📈 Performance Optimization

### Backend Optimization

1. **Use Workflows/Tools Over AI**
   - 60-80% cost reduction
   - 10-100x faster
   - Deterministic results

2. **Enable Caching**
```python
from functools import lru_cache

@lru_cache(maxsize=128)
def get_agent(agent_id: str):
    # Expensive operation
    return result
```

3. **Async I/O**
```python
import asyncio
import aiohttp

async def fetch_multiple():
    async with aiohttp.ClientSession() as session:
        tasks = [fetch_url(session, url) for url in urls]
        return await asyncio.gather(*tasks)
```

4. **Database Optimization**
```python
# Add indexes
from sqlalchemy import Index

Index('idx_agent_status', Agent.status)
Index('idx_agent_category', Agent.category)
```

5. **Connection Pooling**
```python
engine = create_engine(
    'postgresql://...',
    pool_size=10,
    max_overflow=20
)
```

### Frontend Optimization

1. **Code Splitting**
```typescript
import { lazy, Suspense } from 'react';

const AgentManagement = lazy(() => import('./components/AgentManagement'));

<Suspense fallback={<div>Loading...</div>}>
  <AgentManagement />
</Suspense>
```

2. **Memoization**
```typescript
import { useMemo, useCallback } from 'react';

const memoizedValue = useMemo(() => {
  return expensiveCalculation(data);
}, [data]);

const memoizedCallback = useCallback(() => {
  doSomething(data);
}, [data]);
```

3. **Lazy Loading Images**
```tsx
<img loading="lazy" src="/images/robot.png" alt="Robot" />
```

4. **Minification & Compression**
```typescript
// vite.config.ts
export default defineConfig({
  build: {
    minify: 'terser',
    terserOptions: {
      compress: {
        drop_console: true,
      },
    },
  },
});
```

---

## 🤝 Contributing

We welcome contributions! Please follow these guidelines:

### How to Contribute

1. **Fork the Repository**
2. **Create Feature Branch**
   ```bash
   git checkout -b feature/amazing-feature
   ```
3. **Make Changes**
4. **Test Thoroughly**
5. **Commit with Clear Messages**
   ```bash
   git commit -m "feat: Add amazing feature"
   ```
6. **Push to Branch**
   ```bash
   git push origin feature/amazing-feature
   ```
7. **Open Pull Request**

### Contribution Areas

- **New Workflows**: Add maintenance automation workflows
- **New Tools**: Add specialized utility functions
- **UI Improvements**: Enhance user interface
- **Documentation**: Improve or translate docs
- **Bug Fixes**: Fix reported issues
- **Tests**: Add unit/integration tests
- **Performance**: Optimize existing code

### Code Review Process

1. All PRs require review
2. Must pass CI/CD checks
3. Must include tests (when applicable)
4. Must update documentation
5. Approved by maintainer

### License

This project is proprietary to Saudi Aramco / MAHER AI. Contributions may be used according to the project license.

---

## 📞 Support

### Getting Help

1. **Documentation**: Check this comprehensive guide
2. **Issues**: Open GitHub issue
3. **Discussions**: GitHub Discussions forum
4. **Email**: support@maher-ai.com (if available)

### Reporting Bugs

**Bug Report Template:**
```markdown
**Describe the bug**
A clear description of the bug.

**To Reproduce**
Steps to reproduce:
1. Go to '...'
2. Click on '...'
3. See error

**Expected behavior**
What you expected to happen.

**Screenshots**
If applicable, add screenshots.

**Environment:**
- OS: [e.g., Ubuntu 22.04]
- Browser: [e.g., Chrome 120]
- Version: [e.g., 1.0.0]

**Additional context**
Any other relevant information.
```

### Feature Requests

**Feature Request Template:**
```markdown
**Is your feature request related to a problem?**
A clear description of the problem.

**Describe the solution**
What you want to happen.

**Describe alternatives**
Other solutions you've considered.

**Additional context**
Any other relevant information.
```

---

## 📚 Additional Resources

### Documentation

- [Agent Management Guide](AGENT_MANAGEMENT_GUIDE.md)
- [Knowledge Upload Feature](KNOWLEDGE_UPLOAD_FEATURE.md)
- [Hybrid Orchestrator README](backend/HYBRID_ORCHESTRATOR_README.md)
- [Frontend Testing Guide](FRONTEND_TESTING_GUIDE.md)
- [Deployment Guide](DEPLOYMENT.md)
- [Security Checklist](SECURITY_CHECKLIST.md)
- [Production Deployment](PRODUCTION_DEPLOYMENT.md)
- [Sandbox Offline Deployment](SANDBOX_OFFLINE_DEPLOYMENT_GUIDE.md)

### External Links

- [Flask Documentation](https://flask.palletsprojects.com/)
- [React Documentation](https://react.dev/)
- [Gemini API Docs](https://ai.google.dev/docs)
- [SQLAlchemy Docs](https://docs.sqlalchemy.org/)
- [Vite Documentation](https://vitejs.dev/)

---

## 🎉 Conclusion

**MAHER AI** is a production-ready, enterprise-grade maintenance assistant powered by hybrid orchestration. With intelligent resource routing, comprehensive security, and extensive documentation, it's designed to streamline maintenance operations while reducing costs.

### Key Achievements

✅ **60-80% AI Cost Reduction**
✅ **10-100x Faster Tool Execution**
✅ **Enterprise Security Features**
✅ **Comprehensive Documentation**
✅ **Production-Ready Deployment**
✅ **Extensible Architecture**

### Next Steps

1. **Deploy to Production**: Follow deployment guide
2. **Add Custom Workflows**: Extend with your domain workflows
3. **Monitor Performance**: Set up logging and metrics
4. **Collect Feedback**: Use rating system for optimization
5. **Scale as Needed**: Horizontal or vertical scaling

---

**Thank you for using MAHER AI!** 🚀

*Last Updated: November 13, 2025*
*Version: 1.0.0*
