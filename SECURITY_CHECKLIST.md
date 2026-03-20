# 🔒 Production Security Checklist

Use this checklist before deploying MAHER AI to production.

## ✅ Pre-Deployment Security Checklist

### Environment & Configuration

- [ ] `.env` file created with all required variables
- [ ] `GEMINI_API_KEY` is valid and has appropriate quotas
- [ ] `SECRET_KEY` is a strong, randomly generated value (32+ characters)
- [ ] `.env` is listed in `.gitignore` and NOT committed to git
- [ ] `.env.example` exists with template values (no real secrets)
- [ ] `FLASK_ENV` is set to `production` (not `development`)
- [ ] `ALLOWED_ORIGINS` is set to specific domains (not `*`)

**Verify:**
```bash
# Check .env is gitignored
git status .env  # Should show: "fatal: pathspec '.env' did not match any files"

# Verify SECRET_KEY length
cat .env | grep SECRET_KEY | wc -c  # Should be > 40

# Verify ALLOWED_ORIGINS is not wildcard
cat .env | grep ALLOWED_ORIGINS  # Should NOT be "*"
```

---

### API Key Security

- [ ] Gemini API key is NEVER exposed in client-side code
- [ ] API key is only stored in `.env` file
- [ ] API key has appropriate usage limits set in Google Cloud Console
- [ ] API proxy is implemented (backend/app.py)
- [ ] Frontend uses `/api/*` endpoints, not direct Gemini API calls

**Verify:**
```bash
# Check frontend doesn't contain API keys
grep -r "AIza" components/ dist/  # Should return nothing

# Check API client is used instead of GoogleGenAI
grep -r "GoogleGenAI" components/  # Should return nothing
grep -r "apiClient" components/  # Should find usage
```

---

### Backend Security

- [ ] Flask is in production mode (`FLASK_ENV=production`)
- [ ] Debug mode is disabled (`debug=False` in app.py)
- [ ] Rate limiting is configured and tested
- [ ] CORS is properly configured with specific origins
- [ ] Security headers are enabled (automatic in app.py)
- [ ] Request size limits are set (16MB max)
- [ ] Timeouts are configured for API requests

**Verify:**
```bash
# Check Flask is not in debug mode
grep "debug=True" backend/app.py  # Should return nothing

# Test rate limiting
for i in {1..100}; do curl http://localhost:8080/api/health; done
# Should eventually get 429 Too Many Requests

# Test security headers
curl -I http://localhost:8080/api/health | grep -i "x-content-type-options"
```

---

### Frontend Security

- [ ] Production build is optimized and minified
- [ ] Console logs are removed in production build
- [ ] Source maps are disabled
- [ ] Dependencies are up-to-date with no known vulnerabilities
- [ ] XSS protection through React's built-in escaping
- [ ] No inline scripts in index.html

**Verify:**
```bash
# Build production version
npm run build

# Check console.log is removed
grep -r "console.log" dist/  # Should return minimal results

# Check for vulnerabilities
npm audit

# Update dependencies if needed
npm audit fix
```

---

### Server & Infrastructure

- [ ] Waitress WSGI server is used (not Flask dev server)
- [ ] Server is behind a reverse proxy (Nginx/Apache)
- [ ] HTTPS/SSL is configured with valid certificate
- [ ] Firewall is configured (allow only 80, 443, SSH)
- [ ] SSH is secured (key-based auth, disabled root login)
- [ ] Server OS and packages are updated
- [ ] Automatic security updates are enabled

**Verify:**
```bash
# Check Waitress is running (not Flask dev server)
ps aux | grep waitress

# Test HTTPS
curl -I https://yourdomain.com  # Should return 200 OK with SSL info

# Check firewall
sudo ufw status  # Should show only 80, 443, 22

# Check for updates
sudo apt update && sudo apt list --upgradable
```

---

### HTTPS/SSL Configuration

- [ ] Valid SSL certificate installed (Let's Encrypt or commercial)
- [ ] HTTP redirects to HTTPS
- [ ] HSTS header is enabled
- [ ] TLS 1.2+ only (no SSLv3, TLS 1.0, TLS 1.1)
- [ ] Strong cipher suites configured
- [ ] SSL certificate auto-renewal is configured

**Verify:**
```bash
# Test SSL configuration
openssl s_client -connect yourdomain.com:443

# Check certificate expiry
echo | openssl s_client -servername yourdomain.com -connect yourdomain.com:443 2>/dev/null | openssl x509 -noout -dates

# Test SSL rating
# Visit: https://www.ssllabs.com/ssltest/
```

---

### Access Control & Authentication

- [ ] No default passwords are used
- [ ] Database credentials are secure (if applicable)
- [ ] Admin interfaces are protected or disabled
- [ ] File permissions are properly set
- [ ] Server runs as non-root user

**Verify:**
```bash
# Check file permissions
ls -la .env  # Should be 600 or 640
ls -la backend/  # Should not be world-writable

# Check server user
ps aux | grep python  # Should NOT be root

# Set correct permissions
chmod 600 .env
chmod 755 backend/
```

---

### Logging & Monitoring

- [ ] Application logging is configured
- [ ] Log rotation is set up
- [ ] Error logs are monitored
- [ ] Access logs are reviewed regularly
- [ ] Uptime monitoring is configured
- [ ] API usage monitoring is enabled
- [ ] Alerts are configured for errors/downtime

**Verify:**
```bash
# Check logs exist
ls -lh maher_ai.log
sudo ls -lh /var/log/nginx/

# Check log rotation
cat /etc/logrotate.d/nginx

# Test logging
tail -f maher_ai.log  # Make a request and watch logs
```

---

### Rate Limiting & DDoS Protection

- [ ] Rate limiting is enabled and tested
- [ ] Rate limits are appropriate for your use case
- [ ] Cloudflare or similar CDN/protection is considered
- [ ] Nginx rate limiting is configured (if applicable)
- [ ] Fail2ban is installed and configured (optional)

**Verify:**
```bash
# Test rate limiting
ab -n 1000 -c 10 http://localhost:8080/api/health
# Should show some requests get 429 status

# Check rate limit settings
grep "default_limits" backend/app.py
```

---

### Data Protection

- [ ] No sensitive data in logs
- [ ] No API keys in error messages
- [ ] User data is encrypted in transit (HTTPS)
- [ ] Backup strategy is in place
- [ ] Recovery plan is documented
- [ ] GDPR/privacy compliance considered (if applicable)

**Verify:**
```bash
# Check logs don't contain secrets
grep -i "api_key\|password\|secret" maher_ai.log
# Should return nothing or show masked values

# Test backup
tar -czf backup-test.tar.gz .env backend/ dist/
```

---

### Dependency Security

- [ ] All npm dependencies are up-to-date
- [ ] All Python dependencies are up-to-date
- [ ] No known vulnerabilities in dependencies
- [ ] Dependency updates are regularly scheduled
- [ ] Lock files are committed (package-lock.json)

**Verify:**
```bash
# Check npm vulnerabilities
npm audit

# Check Python vulnerabilities
pip list --outdated
pip install safety && safety check

# Update dependencies
npm audit fix
pip install --upgrade -r backend/requirements.txt
```

---

### Testing

- [ ] Health endpoint is accessible
- [ ] API endpoints return expected responses
- [ ] Rate limiting works correctly
- [ ] CORS is properly configured
- [ ] Error handling works correctly
- [ ] Frontend loads and functions properly
- [ ] Chat functionality works end-to-end

**Verify:**
```bash
# Test health endpoint
curl http://localhost:8080/api/health

# Test chat endpoint
curl -X POST http://localhost:8080/api/chat/generate \
  -H "Content-Type: application/json" \
  -d '{"model":"gemini-2.5-flash","contents":[{"role":"user","parts":[{"text":"Hello"}]}]}'

# Test CORS (from different origin)
curl -H "Origin: https://example.com" \
  -H "Access-Control-Request-Method: POST" \
  -X OPTIONS http://localhost:8080/api/chat/generate
```

---

### Documentation & Compliance

- [ ] README.md is up-to-date
- [ ] DEPLOYMENT.md is comprehensive
- [ ] Environment variables are documented
- [ ] API usage limits are documented
- [ ] Terms of service compliance checked
- [ ] Gemini API usage policies reviewed
- [ ] Privacy policy created (if applicable)

---

## 🚨 Critical Security Issues to Avoid

### Never Do This:

❌ Commit `.env` file to git
❌ Expose API keys in client-side code
❌ Use `debug=True` in production
❌ Use `ALLOWED_ORIGINS=*` in production
❌ Run Flask dev server in production
❌ Run server as root user
❌ Use HTTP without HTTPS
❌ Ignore security updates
❌ Store secrets in code or config files
❌ Use default passwords

---

## ✅ Security Best Practices

### Always Do This:

✅ Use environment variables for secrets
✅ Enable HTTPS with valid certificates
✅ Implement rate limiting
✅ Keep dependencies updated
✅ Monitor logs regularly
✅ Use strong passwords and keys
✅ Follow principle of least privilege
✅ Document security procedures
✅ Test security measures
✅ Have incident response plan

---

## 🔍 Regular Security Audits

Perform these checks monthly:

```bash
# Update system packages
sudo apt update && sudo apt upgrade -y

# Check npm vulnerabilities
npm audit

# Check Python vulnerabilities
pip install safety && safety check

# Review access logs
sudo tail -100 /var/log/nginx/maher-ai-access.log

# Check for failed login attempts
sudo tail -100 /var/log/auth.log | grep "Failed"

# Review SSL certificate expiry
echo | openssl s_client -servername yourdomain.com -connect yourdomain.com:443 2>/dev/null | openssl x509 -noout -dates

# Check disk space
df -h
```

---

## 📞 Incident Response

If you suspect a security breach:

1. **Immediately** rotate all API keys
2. Check logs for unauthorized access
3. Review recent code changes
4. Change all passwords
5. Document the incident
6. Notify affected users (if applicable)
7. Review and update security measures

---

## 📚 Additional Resources

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [Flask Security Best Practices](https://flask.palletsprojects.com/en/stable/security/)
- [Gemini API Security](https://ai.google.dev/docs/security)
- [Mozilla SSL Configuration Generator](https://ssl-config.mozilla.org/)

---

**Last Updated:** 2025-01-10
**Version:** 1.0.0
