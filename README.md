# Agent Zero - OneBot OS Template

Agent Zero AI framework with integrated n8n workflow automation and Foam PKM (Zettelkasten + PARA).

## Features

- **Agent Zero**: Autonomous AI agents with memory, tools, and self-evolution
- **n8n**: Visual workflow automation (400+ integrations)
- **Foam PKM**: Zettelkasten + PARA knowledge management
- **Ollama**: Local LLM inference (Gemma2, Llama3.2, etc.)
- **Docker**: Complete stack in one command

## Quick Start

### 1. Clone & Setup

```bash
git clone https://github.com/ValoLoco/agent-zero.git
cd agent-zero
```

### 2. Start Stack

```bash
docker compose up -d
```

### 3. Install Ollama Models

```bash
docker exec ollama ollama pull gemma2:9b
docker exec ollama ollama pull nomic-embed-text
```

### 4. Access Services

- **Agent Zero UI**: http://localhost:8000
- **n8n**: http://localhost:5678
- **Foam Vault**: Open `docker-volumes/foam-repo` in VS Code with Foam extension

## Architecture

```
Agent Zero (8000)
├── Ollama (11434) - Local LLM
├── n8n (5678) - Workflow automation
│   └── Postgres (5432) - n8n database
└── Foam Vault - PKM
    ├── Zettelkasten (atomic notes)
    ├── PARA (projects/areas)
    └── Daily notes (journals)
```

## Zettelkasten Workflow

1. **Capture**: Daily notes in `journals/`
2. **Process**: Fleeting notes in `zettelkasten/inbox/`
3. **Develop**: Permanent atomic notes in `zettelkasten/permanent/`
4. **Organize**: Link to PARA projects
5. **Retrieve**: Agents use RAG across all notes

See [ZETTELKASTEN.md](ZETTELKASTEN.md) for detailed workflow.

## Agent Tools

### n8n Tool
Create and execute workflows programmatically:
```python
n8n_tool.execute(action="create_workflow", workflow={...})
```

### Foam Zettel Tool
Create atomic notes with linking:
```python
foam_zettel.execute(
    action="create_zettel",
    title="Agent Memory Patterns",
    content="Vector embeddings enable semantic search",
    links=["agent-zero-architecture"]
)
```

## Development

- **Local**: `docker compose up` for full stack
- **Production**: Deploy to Railway/Render with docker-compose
- **SaaS**: Fork as template, customize branding/UI

## Template Usage

This is a clean template for building Agent Zero-based applications:

1. Fork this repo
2. Customize branding in `webui/`
3. Add custom tools in `python/tools/`
4. Deploy to cloud (Vercel frontend + Railway backend)
5. Multi-tenant via GitHub orgs or Supabase

## Environment Variables

```bash
# .env (optional)
OLLAMA_URL=http://ollama:11434
N8N_URL=http://n8n:5678
N8N_API_KEY=your_api_key  # For agent n8n integration
```

## VS Code Setup

Install Foam extension:
```bash
code --install-extension foam.foam-vscode
code docker-volumes/foam-repo
```

## License

MIT
