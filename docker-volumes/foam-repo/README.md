# OneBot PKM Vault

Integrated Zettelkasten + PARA knowledge base for Agent Zero.

## Structure

- **journals/** - Daily notes (capture everything)
- **zettelkasten/** - Atomic permanent notes (one idea per note)
  - inbox/ - Fleeting notes (quick captures)
  - literature/ - Source-based notes
  - permanent/ - Main Zettel (linked ideas)
- **PARA/** - Action-oriented organization
  - Projects/ - Time-bound goals
  - Areas/ - Ongoing responsibilities
  - Resources/ - Reference topics
  - Archives/ - Completed/inactive

## Workflow

1. Daily capture → `journals/YYYY-MM-DD.md`
2. Process fleeting → `zettelkasten/inbox/`
3. Develop permanent → `zettelkasten/permanent/`
4. Link to PARA → Projects reference Zettel
5. Agent RAG → Searches all folders

## VS Code

Open in VS Code with Foam extension:
```bash
code docker-volumes/foam-repo
```

Or use vscode.dev:
```
https://vscode.dev/github/ValoLoco/agent-zero/docker-volumes/foam-repo
```
