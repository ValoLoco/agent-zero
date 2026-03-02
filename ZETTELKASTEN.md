# Zettelkasten + PARA Workflow Guide

## Philosophy

**Zettelkasten**: Bottom-up knowledge building through atomic, linked notes.  
**PARA**: Top-down organization by actionability (Projects, Areas, Resources, Archives).

Together, they create a complete knowledge + action system.

## Daily Workflow

### Morning (5 min)
1. Open daily note: `journals/2026-03-02.md`
2. Review tasks from yesterday
3. Capture today's intentions

### Throughout Day
- Quick captures in today's daily note
- Voice memos → transcribe to daily note
- Meeting notes inline
- Ideas in "Captures" section

### Evening (10 min)
1. Process captures:
   - Tasks → PARA Projects
   - Ideas → Zettelkasten inbox
   - References → PARA Resources
2. Create 1-2 permanent Zettel from inbox
3. Link new Zettel to existing notes

## Creating Permanent Notes

### Quality Criteria
- **Atomic**: One idea per note
- **Own words**: Rewrite in your language
- **Standalone**: Readable without context
- **Linked**: Connects to other notes

### Template Usage
1. `Cmd/Ctrl + Shift + P` → "Foam: Create Note from Template"
2. Select "zettel.md"
3. Fill in:
   - Title (descriptive, unique)
   - Content (one idea, your words)
   - Connections (3-5 related notes)
   - Source (where idea came from)

### Example

```markdown
---
id: 20260302151234-4829
type: permanent
tags: [agent-architecture, memory]
created: 2026-03-02T15:12:34
---

# Agent Memory Requires Vector Embeddings

Agents need semantic recall, not keyword search. Vector embeddings (e.g., nomic-embed-text) convert text to numerical representations, enabling similarity search across knowledge base.

## Context

Traditional keyword search fails with synonyms and conceptual queries. Vector search finds "car" when querying "automobile" by measuring semantic distance in embedding space.

## Connections

- [[agent-zero-architecture]]
- [[ollama-embedding-models]]
- [[rag-retrieval-strategies]]

## Source

Agent Zero codebase analysis + Ollama docs
```

## PARA Structure

### Projects (Active, Time-Bound)
- `PARA/Projects/Q1-OneBot-SaaS.md`
- `PARA/Projects/Client-KASAPT-Website.md`

Link to relevant Zettel:
```markdown
# Q1 OneBot SaaS

## Architecture Notes
- [[agent-zero-architecture]]
- [[n8n-workflow-patterns]]
```

### Areas (Ongoing Standards)
- `PARA/Areas/Trading-Psychology.md`
- `PARA/Areas/BUENATURA-Operations.md`

### Resources (Reference Topics)
- `PARA/Resources/Bitcoin-Research/`
- `PARA/Resources/AI-Agent-Frameworks/`

### Archives (Completed/Inactive)
- Move completed projects here
- Keep for reference, low priority

## Agent Integration

Agents read/write all folders:

```python
# Agent tool usage
foam_zettel.create_zettel(
    title="n8n Workflow Patterns",
    content="Common patterns: trigger → process → action",
    links=["agent-zero-architecture", "automation-best-practices"]
)
```

Agents use RAG across:
- All Zettelkasten notes
- PARA projects/resources
- Daily notes (recent context)

## Graph View

`Cmd/Ctrl + Shift + P` → "Foam: Show Graph"

Visualize:
- Hubs (highly connected notes)
- Orphans (unlinked notes - process these)
- Clusters (topic areas)

## Tips

- Start with 10 permanent notes, build from there
- Link liberally (3-5 per note minimum)
- Review orphans weekly
- Agents help: "Summarize this article into Zettel"
- Use daily notes as inbox, process daily

## Further Reading

- Niklas Luhmann's Zettelkasten method
- Tiago Forte's PARA system
- Foam documentation
