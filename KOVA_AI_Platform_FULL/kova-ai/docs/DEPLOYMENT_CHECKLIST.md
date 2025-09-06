# 🚀 Kova AI System - Deployment Checklist

## Pre-Deployment

### 1. Environment Setup
- [ ] Server/VM provisioned with Docker and Docker Compose
- [ ] Domain name configured (if applicable)
- [ ] SSL certificates obtained (Let's Encrypt recommended)
- [ ] Firewall configured (ports 80, 443, 22)

### 2. API Keys & Secrets
- [ ] **OpenAI API Key** - Get from https://platform.openai.com/api-keys
- [ ] **Anthropic API Key** - Get from https://console.anthropic.com/
- [ ] **GitHub Token** - Get from https://github.com/settings/tokens
- [ ] **Pinecone API Key** - Get from https://www.pinecone.io/
- [ ] **Google OAuth** (optional) - https://console.developers.google.com/
- [ ] **Slack Bot Token** (optional) - https://api.slack.com/apps

### 3. Database & Cache
- [ ] PostgreSQL configured or managed service ready
- [ ] Redis configured or managed service ready
- [ ] Database backups strategy planned
- [ ] Connection strings secured

## Deployment Steps

### 1. System Preparation
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Install Docker Compose
sudo apt install docker-compose-plugin
```

### 2. Code Deployment
```bash
# Clone repository
git clone <your-repo-url>
cd Kova-ai-SYSTEM/KOVA_AI_Platform_FULL/kova-ai

# Copy environment file
cp .env.example .env
```

### 3. Environment Configuration
Edit `.env` file with production values:
```bash
# Database (use managed service URLs for production)
DATABASE_URL=postgresql+asyncpg://user:pass@your-db-host:5432/kova
REDIS_URL=redis://your-redis-host:6379

# API Keys (REQUIRED)
OPENAI_API_KEY=sk-your-actual-key
ANTHROPIC_API_KEY=sk-ant-your-actual-key
GITHUB_TOKEN=ghp_your-actual-token
PINECONE_API_KEY=your-actual-key

# Production settings
DEBUG=false
API_HOST=0.0.0.0
API_PORT=8000
```

### 4. Launch System
```bash
# Deploy
./setup_kova_system.sh

# Or manually:
docker compose up -d
```

## Post-Deployment

### 1. Health Checks
- [ ] API health: `curl https://yourdomain.com/health`
- [ ] Database connectivity verified
- [ ] Redis connectivity verified
- [ ] All endpoints responding correctly

### 2. Security Hardening
- [ ] Change default passwords
- [ ] Enable HTTPS with SSL certificates
- [ ] Configure firewall rules
- [ ] Set up API rate limiting
- [ ] Restrict metrics endpoint access
- [ ] Enable access logs

### 3. Monitoring Setup
- [ ] Prometheus metrics collection configured
- [ ] Grafana dashboards imported
- [ ] Alerting rules configured
- [ ] Log aggregation setup (ELK stack)
- [ ] Uptime monitoring (external service)

### 4. Backup & Recovery
- [ ] Database backup automated
- [ ] Configuration backup scheduled
- [ ] Recovery procedures documented
- [ ] Disaster recovery plan tested

### 5. OAuth Configuration (Optional)

For Google OAuth integration:
1. Go to https://console.developers.google.com/
2. Create new project or select existing
3. Enable Google+ API
4. Create OAuth 2.0 credentials
5. Set redirect URI: `https://yourdomain.com/oauth/google/callback`
6. Update .env with:
   ```
   GOOGLE_CLIENT_ID=your-client-id
   GOOGLE_CLIENT_SECRET=your-client-secret
   ```

## Production Considerations

### Performance
- [ ] Use managed databases (AWS RDS, Google Cloud SQL)
- [ ] Use managed Redis (AWS ElastiCache, Google Memorystore)
- [ ] Configure CDN for static assets
- [ ] Enable database connection pooling
- [ ] Set up horizontal scaling with load balancer

### Security
- [ ] Enable WAF (Web Application Firewall)
- [ ] Use secrets management (AWS Secrets Manager, HashiCorp Vault)
- [ ] Enable API authentication/authorization
- [ ] Set up VPC/private networking
- [ ] Regular security audits

### Monitoring
- [ ] Set up centralized logging
- [ ] Configure performance monitoring (APM)
- [ ] Set up error tracking (Sentry)
- [ ] Configure alerting (PagerDuty, Slack)

## Troubleshooting

### Common Issues
1. **SSL Certificate errors**
   ```bash
   # Check certificate
   openssl x509 -in cert.pem -text -noout
   
   # Renew Let's Encrypt
   certbot renew
   ```

2. **Database connection issues**
   ```bash
   # Test connection
   docker compose exec db psql -U kova -d kova -c "SELECT 1;"
   
   # Check logs
   docker compose logs db
   ```

3. **API not responding**
   ```bash
   # Check logs
   docker compose logs api
   
   # Restart service
   docker compose restart api
   ```

### Support
- Check logs: `docker compose logs -f`
- Health endpoint: `/health`
- Metrics: `/metrics`
- API docs: `/docs`

---

## Success Criteria ✅

Your deployment is successful when:
- [ ] All health checks pass
- [ ] API documentation accessible at `/docs`
- [ ] All required endpoints responding
- [ ] Database schema properly initialized
- [ ] Monitoring dashboards showing data
- [ ] SSL certificate valid (production)
- [ ] Backup procedures tested