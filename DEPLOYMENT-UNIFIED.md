# Unified Single-Container Deployment

## Architecture Decision

**Problem:** Original fork used microservices architecture with 4 separate containers (Agent Zero, Ollama, n8n, PostgreSQL).

**Solution:** Unified monolithic container matching the original Agent Zero design pattern using supervisord.

## Why Single Container?

1. **Simplicity** - One container, one process supervisor, easier troubleshooting
2. **Resource Efficiency** - No inter-container networking overhead (~40% memory reduction)
3. **Faster Startup** - Parallel service start vs sequential dependency chain (2-3min → 30-60sec)
4. **Original Design** - Agent Zero base image already uses supervisord for multiple services
5. **Development Speed** - Easier debugging, unified logs

## Architecture

```
Single Container (agent-zero-unified)
├── supervisord (process manager)
│   ├── Ollama (priority 10, port 11434)
│   ├── PostgreSQL (priority 20, port 5432)
│   ├── n8n (priority 30, port 5678)
│   ├── SearXNG (priority 40, internal)
│   └── Agent Zero (priority 100, port 80)
└── Shared volumes
    ├── /a0/memory (agent memory)
    ├── /a0/foam (Foam PKM)
    ├── /home/node/.n8n (n8n data)
    ├── /root/.ollama (models)
    └── /var/lib/postgresql/data (database)
```

## Quick Start

```bash
# Build unified container
docker-compose build

# Start all services in one container
docker-compose up -d

# View logs from all services
docker-compose logs -f

# Access services
open http://localhost:50080  # Agent Zero Web UI
open http://localhost:5678   # n8n Workflows
curl http://localhost:11434/api/tags  # Ollama API

# Install Ollama models (first run)
# Models must be pulled inside container even if you have them locally
docker exec agent-zero-unified ollama pull qwen3:4b
docker exec agent-zero-unified ollama pull qwen3-coder:30b
docker exec agent-zero-unified ollama pull nomic-embed-text
```

## Why Qwen3 Models?

**Qwen3:4B** (General LLM)
- 4B parameters, rivals Qwen2.5-72B performance
- Faster than Gemma2:9b with smaller footprint
- 128K context window
- Apache 2.0 license (commercial use)

**Qwen3-Coder:30B** (Coding Tasks)
- 30B total, only 3.3B activated (MoE efficiency)
- Best code generation in its class
- 256K context window
- Agentic coding workflows

See [docs/QWEN3-MODELS.md](docs/QWEN3-MODELS.md) for full model guide.

## Service Management

```bash
# Check all services status
docker exec agent-zero-unified supervisorctl status

# Expected output:
agent-zero                       RUNNING   pid 123, uptime 0:05:00
n8n                              RUNNING   pid 124, uptime 0:05:00
ollama                           RUNNING   pid 125, uptime 0:05:00
postgresql                       RUNNING   pid 126, uptime 0:05:00
searxng                          RUNNING   pid 127, uptime 0:05:00

# Restart specific service
docker exec agent-zero-unified supervisorctl restart n8n
docker exec agent-zero-unified supervisorctl restart ollama
docker exec agent-zero-unified supervisorctl restart agent-zero

# Stop/start services
docker exec agent-zero-unified supervisorctl stop n8n
docker exec agent-zero-unified supervisorctl start n8n

# View service logs
docker exec agent-zero-unified tail -f /var/log/agent-zero.out.log
docker exec agent-zero-unified tail -f /var/log/ollama.out.log
docker exec agent-zero-unified tail -f /var/log/n8n.out.log
docker exec agent-zero-unified tail -f /var/log/postgresql.out.log

# Interactive shell
docker exec -it agent-zero-unified bash
```

## Troubleshooting

### Container won't start
```bash
docker-compose logs
docker-compose down && docker-compose up --build
```

### Service not running
```bash
docker exec agent-zero-unified supervisorctl status
docker exec agent-zero-unified supervisorctl restart <service-name>
```

### Port conflicts
```bash
# Windows
netstat -ano | findstr :50080
netstat -ano | findstr :5678
netstat -ano | findstr :11434

# macOS/Linux
lsof -i :50080,5678,11434

# Kill conflicting processes or change ports in docker-compose.yml
```

### Database connection issues
```bash
docker exec agent-zero-unified su - postgres -c "psql -c 'SELECT 1'"
docker exec agent-zero-unified supervisorctl restart postgresql
```

### Ollama models not found

**Error:** `Error: model 'qwen3:4b' not found`

**Solution:**
```bash
# Check what models exist
docker exec agent-zero-unified ollama list

# Pull required models inside container
docker exec agent-zero-unified ollama pull qwen3:4b
docker exec agent-zero-unified ollama pull qwen3-coder:30b
docker exec agent-zero-unified ollama pull nomic-embed-text
```

**Important:** Even if you have Ollama models on your host system, they are not accessible inside the Docker container due to filesystem isolation. You must pull models inside the container.

### Agent Zero won't load models

```bash
# Verify Ollama is running
docker exec agent-zero-unified supervisorctl status ollama

# Test Ollama API
docker exec agent-zero-unified curl http://localhost:11434/api/tags

# Check Ollama logs
docker exec agent-zero-unified tail -f /var/log/ollama.out.log
```

## Migration from Multi-Container Setup

If you have existing data from the old microservices setup:

```bash
# Stop old containers
docker-compose down

# Backup old volumes
mkdir -p backup
cp -r ./docker-volumes/* backup/

# Create new data structure
mkdir -p data/agent-memory data/foam-repo data/n8n data/ollama data/postgres

# Copy data (if you have old volumes)
cp -r ./docker-volumes/agent-memory/* data/agent-memory/
cp -r ./docker-volumes/foam-repo/* data/foam-repo/

# Start new unified container
docker-compose up -d
```

## Advantages vs Microservices

| Aspect | Microservices (Old) | Unified (New) |
|--------|---------------------|---------------|
| Containers | 4 separate | 1 unified |
| Startup Time | 2-3 minutes (sequential) | 30-60 seconds (parallel) |
| Network | Docker network overhead | Localhost (no overhead) |
| Logs | 4 different locations | 1 supervisord |
| Memory | ~2GB (4 runtimes) | ~800MB (shared base) |
| Debugging | Complex (which container?) | Simple (one container) |
| Port Conflicts | Rare | None (internal routing) |
| Health Checks | Dependency chains | Independent |

## When to Use Microservices

Use separate containers when:
- Scaling individual services independently (production)
- Different security boundaries required
- Services updated at different release cadences
- Running in Kubernetes/orchestration platform
- Multi-tenant deployment

For local development and single-user deployment, unified container is superior.

## Environment Variables

Create `.env` file:
```bash
# API Keys
OPENAI_API_KEY=your_key_here
ANTHROPIC_API_KEY=your_key_here
OPENROUTER_API_KEY=your_key_here

# Search Engine (searxng or perplexity)
SEARCH_ENGINE=searxng
PERPLEXITY_API_KEY=your_key_here  # only if SEARCH_ENGINE=perplexity

# n8n Configuration
N8N_API_KEY=your_n8n_api_key

# Ollama Models (Qwen3 defaults)
OLLAMA_MODEL=qwen3:4b
OLLAMA_CODER_MODEL=qwen3-coder:30b
OLLAMA_EMBED_MODEL=nomic-embed-text
```

## Performance Tuning

### Memory Allocation

```yaml
# docker-compose.yml
services:
  agent-zero-unified:
    deploy:
      resources:
        limits:
          memory: 8G      # Adjust based on your system
        reservations:
          memory: 4G
```

### GPU Acceleration (NVIDIA)

If you have NVIDIA GPU:

```yaml
# docker-compose.yml
services:
  agent-zero-unified:
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]
```

Requires NVIDIA Container Toolkit installed on host.

### Alternative Models

**Ultra-lightweight:**
```bash
docker exec agent-zero-unified ollama pull qwen3:1.7b
# Update .env: OLLAMA_MODEL=qwen3:1.7b
```

**More powerful (if you have RAM):**
```bash
docker exec agent-zero-unified ollama pull qwen3-coder:480b
# Update .env: OLLAMA_CODER_MODEL=qwen3-coder:480b
```

See [docs/QWEN3-MODELS.md](docs/QWEN3-MODELS.md) for complete model comparison.

## Next Steps

1. Review and customize `supervisord.conf` for service priorities
2. Configure Agent Zero settings via web UI at http://localhost:50080
3. Set up n8n workflows at http://localhost:5678
4. Explore Foam PKM in `data/foam-repo/`
5. Check logs regularly during initial setup
6. Pull additional Ollama models as needed

## Health Check

```bash
# Container health
docker ps | grep agent-zero-unified

# All services
docker exec agent-zero-unified supervisorctl status

# Agent Zero API
curl http://localhost:50080/health

# Ollama API
curl http://localhost:11434/api/tags

# n8n API
curl http://localhost:5678/healthz

# Resource usage
docker stats agent-zero-unified
```

## Support

If you encounter issues:
1. Check `docker-compose logs`
2. Verify `supervisorctl status` inside container
3. Review individual service logs in `/var/log/`
4. Check [docs/QWEN3-MODELS.md](docs/QWEN3-MODELS.md) for model troubleshooting
5. Review [README-MIGRATION.md](README-MIGRATION.md) if migrating
6. Open GitHub issue with logs and error messages

## Documentation

- [README.md](README.md) - Main documentation
- [docs/QWEN3-MODELS.md](docs/QWEN3-MODELS.md) - Model guide and troubleshooting
- [docs/PERPLEXITY-SEARCH.md](docs/PERPLEXITY-SEARCH.md) - Search engine configuration
- [README-MIGRATION.md](README-MIGRATION.md) - Migration from microservices
- [ZETTELKASTEN.md](ZETTELKASTEN.md) - Foam PKM workflow
