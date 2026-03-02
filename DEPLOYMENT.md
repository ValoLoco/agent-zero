# OneBot OS Deployment Guide

Complete guide for deploying Agent Zero OneBot OS locally and to production (Railway + Vercel).

## Local Development

### Prerequisites
- Docker Desktop (Mac/Windows) or Docker Engine (Linux)
- Git
- VS Code with Foam extension (optional, for PKM)

### Quick Start

```bash
# 1. Clone repository
git clone https://github.com/ValoLoco/agent-zero.git
cd agent-zero

# 2. Copy environment template
cp .env.example .env

# 3. Start stack
docker compose up -d

# 4. Install Ollama models
docker exec ollama ollama pull gemma2:9b
docker exec ollama ollama pull nomic-embed-text

# 5. Access services
open http://localhost:8000  # Agent Zero UI
open http://localhost:5678  # n8n
code docker-volumes/foam-repo  # Foam PKM
```

### Service Ports
| Service | Port | URL |
|---------|------|-----|
| Agent Zero | 8000 | http://localhost:8000 |
| n8n | 5678 | http://localhost:5678 |
| Ollama | 11434 | http://localhost:11434 |
| Postgres | 5432 | localhost:5432 |

### Verify Installation

```bash
# Check services
docker compose ps

# View logs
docker compose logs -f agent-zero

# Test Ollama
docker exec ollama ollama list

# Test n8n API
curl http://localhost:5678/healthz
```

---

## Production Deployment

### Architecture

```
Vercel (Frontend)          Railway (Backend)
    ↓                           ↓
Agent Zero UI    ←→    Docker Stack (Agent Zero + n8n + Ollama)
                              ↓
                        Persistent Volumes
                        (Memory + Foam)
```

### Option 1: Railway (Full Stack)

**Cost**: ~$10/month (Hobby plan)

#### Steps

1. **Create Railway Account**
   - Go to [railway.app](https://railway.app)
   - Connect GitHub account

2. **Deploy from GitHub**
   ```bash
   # Railway CLI (optional)
   npm install -g @railway/cli
   railway login
   railway init
   railway up
   ```

   Or use Railway dashboard:
   - New Project → Deploy from GitHub
   - Select `ValoLoco/agent-zero`
   - Branch: `main`

3. **Add Environment Variables**
   ```
   OLLAMA_URL=http://ollama:11434
   N8N_URL=http://n8n:5678
   N8N_API_KEY=your_generated_key
   ```

4. **Configure Volumes**
   - agent-memory: `/app/memory`
   - foam-repo: `/app/foam`

5. **Deploy Services**
   Railway auto-detects `docker-compose.yml`

6. **Custom Domain** (optional)
   - Settings → Domains → Add custom domain
   - Point DNS: `CNAME → yourapp.up.railway.app`

#### Post-Deployment

```bash
# SSH into Railway container
railway run bash

# Install Ollama models
ollama pull gemma2:9b nomic-embed-text

# Check logs
railway logs
```

### Option 2: Vercel (Frontend) + Railway (Backend)

**Frontend**: Vercel (Free tier)  
**Backend**: Railway ($10/month)

#### Vercel Setup

1. **Deploy Frontend**
   ```bash
   # Install Vercel CLI
   npm install -g vercel
   
   # Deploy
   cd webui
   vercel --prod
   ```

2. **Environment Variables** (Vercel dashboard)
   ```
   NEXT_PUBLIC_AGENT_API=https://your-railway-app.railway.app
   NEXT_PUBLIC_N8N_URL=https://your-n8n.railway.app
   ```

3. **Configure Proxy** (vercel.json)
   ```json
   {
     "rewrites": [
       {
         "source": "/api/:path*",
         "destination": "https://your-railway-app.railway.app/api/:path*"
       }
     ]
   }
   ```

#### Railway Backend

Same as Option 1, but expose API endpoints:
- Agent Zero: `https://agent.yourapp.com`
- n8n: `https://n8n.yourapp.com`

### Option 3: Self-Hosted (VPS)

**Cost**: $5-20/month (DigitalOcean, Linode, Hetzner)

#### Requirements
- Ubuntu 22.04 LTS
- 2+ CPU cores
- 4+ GB RAM
- 40+ GB SSD

#### Setup

```bash
# SSH into VPS
ssh root@your-vps-ip

# Install Docker
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker $USER

# Install Docker Compose
sudo apt install docker-compose-plugin

# Clone repo
git clone https://github.com/ValoLoco/agent-zero.git
cd agent-zero

# Configure
cp .env.example .env
nano .env  # Edit as needed

# Start services
docker compose up -d

# Install models
docker exec ollama ollama pull gemma2:9b nomic-embed-text
```

#### Reverse Proxy (Nginx + SSL)

```bash
# Install Nginx & Certbot
sudo apt install nginx certbot python3-certbot-nginx

# Configure Nginx
sudo nano /etc/nginx/sites-available/onebot
```

```nginx
server {
    listen 80;
    server_name yourdomain.com;

    location / {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }

    location /n8n {
        proxy_pass http://localhost:5678;
    }
}
```

```bash
# Enable site
sudo ln -s /etc/nginx/sites-available/onebot /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx

# Add SSL
sudo certbot --nginx -d yourdomain.com
```

---

## Multi-Tenant SaaS

### Architecture

```
Vercel Frontend
    ↓
Supabase Auth
    ↓
Railway (Main Agent Zero)
    ↓
GitHub Orgs (per-tenant repos)
    ↓
Foam Vaults (per-tenant)
```

### Setup

1. **Supabase Project**
   - Create at [supabase.com](https://supabase.com)
   - Enable auth (email/password)

2. **GitHub Org per Tenant**
   ```python
   # Auto-create on signup
   gh org create client-name-onebot
   gh repo create client-name-onebot/foam-vault --template ValoLoco/agent-zero
   ```

3. **Environment per Tenant**
   ```
   FOAM_REPO_URL=https://github.com/client-name-onebot/foam-vault
   SUPABASE_TENANT_ID=uuid
   ```

4. **Deploy**
   - Main app: Railway
   - Frontend: Vercel
   - Auth: Supabase
   - Data: GitHub (per-tenant repos)

---

## Monitoring

### Health Checks

```bash
# Agent Zero
curl http://localhost:8000/health

# n8n
curl http://localhost:5678/healthz

# Ollama
curl http://localhost:11434/api/tags
```

### Logs

```bash
# All services
docker compose logs -f

# Specific service
docker compose logs -f agent-zero

# Follow errors only
docker compose logs -f | grep ERROR
```

### Metrics (Railway)

- CPU/Memory: Railway dashboard
- Request logs: Railway logs
- Uptime: Railway metrics

---

## Backup & Recovery

### Backup

```bash
# Create backup
tar -czf onebot-backup-$(date +%Y%m%d).tar.gz \
  docker-volumes/agent-memory \
  docker-volumes/foam-repo

# Upload to S3/B2 (optional)
aws s3 cp onebot-backup-*.tar.gz s3://your-bucket/
```

### Restore

```bash
# Stop services
docker compose down

# Extract backup
tar -xzf onebot-backup-20260302.tar.gz

# Restart
docker compose up -d
```

---

## Troubleshooting

### Ollama Model Not Found

```bash
# List installed models
docker exec ollama ollama list

# Pull missing model
docker exec ollama ollama pull gemma2:9b
```

### n8n Database Error

```bash
# Reset database
docker compose down -v
docker compose up -d
```

### Foam Vault Empty

```bash
# Check volume
ls -la docker-volumes/foam-repo/

# Re-clone template
rm -rf docker-volumes/foam-repo
git submodule update --init
```

### Port Conflicts

Edit `docker-compose.yml` to use different ports:
```yaml
ports:
  - "8001:8000"  # Agent Zero
  - "5679:5678"  # n8n
```

---

## Scaling

### Horizontal (Multiple Instances)

```yaml
# docker-compose.scale.yml
services:
  agent-zero:
    deploy:
      replicas: 3
```

```bash
docker compose -f docker-compose.yml -f docker-compose.scale.yml up -d
```

### Vertical (More Resources)

```yaml
services:
  agent-zero:
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 4G
```

---

## Cost Estimates

| Setup | Monthly Cost | Best For |
|-------|-------------|----------|
| Local Dev | $0 | Development, testing |
| Railway Hobby | $10 | Small teams, MVPs |
| Railway + Vercel | $10 | Production SaaS |
| VPS (DigitalOcean) | $12 | Full control, custom domains |
| Multi-Tenant | $50+ | SaaS with multiple clients |

---

## Security

### Production Checklist

- [ ] Change default passwords (Postgres, n8n)
- [ ] Enable HTTPS (SSL certificates)
- [ ] Restrict network access (firewall rules)
- [ ] Regular backups (automated)
- [ ] Update dependencies (monthly)
- [ ] Monitor logs (errors, suspicious activity)
- [ ] API rate limiting (n8n, Agent Zero)
- [ ] Environment secrets (not in git)

---

## Support

- **Issues**: [GitHub Issues](https://github.com/ValoLoco/agent-zero/issues)
- **Discussions**: [GitHub Discussions](https://github.com/ValoLoco/agent-zero/discussions)
- **Email**: vk.buenatura@gmail.com

---

**Last Updated**: 2026-03-02  
**Version**: 1.0.0  
**License**: MIT
