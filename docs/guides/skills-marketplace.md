# Skills Marketplace Integration

## Overview

Agent Zero now integrates with [skills.sh](https://skills.sh), the largest directory of AI agent skills following the Anthropic SKILL.md open standard. When agents need a capability they don't have locally, they automatically search the marketplace, download the skill, and use it.

## Three-Tier Fallback System

### Tier 1: Local Skills (Instant)
Agent searches `/a0/usr/skills/` directory first

### Tier 2: Skills.sh Marketplace (Automated)
If not found locally, agent uses `browser_agent` to search skills.sh marketplace

### Tier 3: Auto-Creation (Adaptive)
If skill doesn't exist anywhere, agent auto-generates a custom skill based on requirements

---

## Usage Examples

### Search for Skills

```python
# Agent command
skills_tool(
    method="search",
    query="pdf processing"
)
```

**Agent workflow:**
1. Searches local skills first
2. If not found, searches skills.sh marketplace
3. Returns top 5 matches with install counts
4. Offers to install from marketplace

### Load a Skill

```python
# Load local skill
skills_tool(
    method="load",
    skill_name="python-optimizer"
)

# If not found locally, agent suggests:
# - Search marketplace
# - Create custom skill
```

### Install from Marketplace

```python
# Install from skills.sh
skills_tool(
    method="install_from_marketplace",
    skill_name="anthropics/skills/pdf"
)
```

**Format**: `owner/repo/skill` or `owner/repo`

**Agent actions:**
1. Constructs GitHub raw URL
2. Downloads SKILL.md using browser_agent
3. Saves to `/a0/usr/skills/{skill_name}/`
4. Makes immediately available for loading

### Create Custom Skill

```python
# Auto-generate skill template
skills_tool(
    method="create",
    skill_name="forex-analysis",
    description="Analyze forex trading pairs using technical indicators"
)
```

**Agent actions:**
1. Creates `/a0/usr/skills/forex-analysis/SKILL.md`
2. Generates template with frontmatter
3. Adds basic instructions structure
4. Ready to customize and load

---

## Skills.sh Marketplace

### What is skills.sh?

[skills.sh](https://skills.sh) is a public registry of AI agent skills following the Anthropic SKILL.md open standard. Compatible with:
- Claude Code
- Cursor IDE
- OpenAI Codex CLI
- GitHub Copilot
- Agent Zero

### Popular Skills Available

| Skill | Installs | Description |
|-------|----------|-------------|
| `anthropics/skills/pdf` | 923 | PDF processing and extraction |
| `anthropics/skills/frontend-design` | 3.9K | Frontend design patterns |
| `anthropics/skills/skill-creator` | 2.5K | Create and optimize skills |
| `anthropics/skills/docx` | 735 | Word document processing |
| `anthropics/skills/xlsx` | 773 | Excel spreadsheet processing |
| `anthropics/skills/webapp-testing` | 662 | Web app testing frameworks |
| `anthropics/skills/mcp-builder` | 618 | MCP server builder |

### Browsing the Marketplace

**Website**: [https://skills.sh](https://skills.sh)  
**Leaderboard**: [https://skills.sh/leaderboard](https://skills.sh/leaderboard)  
**Anthropic Official**: [https://skills.sh/anthropics/skills](https://skills.sh/anthropics/skills)

---

## Complete Workflow Example

### Scenario: Agent Needs PDF Processing

**User**: "Extract text from this PDF document"

**Agent Internal Process**:

```python
# Step 1: Check if pdf skill exists locally
skills_tool(method="search", query="pdf")
# Result: No local skills found

# Step 2: Search marketplace automatically
# Uses browser_agent to search skills.sh
# Finds: anthropics/skills/pdf (923 installs)

# Step 3: Offer to install
"Found 'anthropics/skills/pdf' with 923 installs. Install?"

# Step 4: User confirms, agent installs
skills_tool(
    method="install_from_marketplace",
    skill_name="anthropics/skills/pdf"
)
# Downloaded to /a0/usr/skills/pdf/SKILL.md

# Step 5: Load skill
skills_tool(method="load", skill_name="pdf")
# Skill instructions now in agent context

# Step 6: Execute task
code_execution_tool(code="import pypdf; ...")
```

---

## Skill Installation Formats

### Format 1: owner/repo/skill
```python
skill_name="anthropics/skills/pdf"
# Downloads from: https://github.com/anthropics/skills/tree/main/skills/pdf
```

### Format 2: owner/repo
```python
skill_name="mycompany/custom-tools"
# Downloads from: https://github.com/mycompany/custom-tools/SKILL.md
```

### GitHub URL Construction

**With skill path**:  
`https://raw.githubusercontent.com/{owner}/{repo}/main/skills/{skill}/SKILL.md`

**Repository root**:  
`https://raw.githubusercontent.com/{owner}/{repo}/main/SKILL.md`

---

## Auto-Creation Template

When no skill exists, agent generates:

```markdown
---
name: "your-skill-name"
description: "What this skill does"
version: "1.0.0"
author: "Agent Zero"
tags: ["custom", "auto-generated"]
trigger_patterns:
  - "keyword"
---

# Your Skill Name

## When to use this skill
Your description here.

## Instructions

### Step 1: Analyze the task
Understand requirements.

### Step 2: Execute
Perform actions.

### Step 3: Verify
Confirm completion.

## Examples

### Example 1: Basic usage
Describe typical use case.

## Best practices
1. Follow instructions step-by-step
2. Verify results
3. Document issues

## References
- Add links here
```

**Agent then**:
1. Saves template to `/a0/usr/skills/{name}/SKILL.md`
2. Suggests editing for specific needs
3. Loads skill for immediate use

---

## Configuration

### Environment Variables

```bash
# .env
SKILLS_DIR=/a0/usr/skills  # Default skills directory
SKILLS_SH_URL=https://skills.sh  # Marketplace URL
```

### Limits

```python
# Maximum skills loaded simultaneously
MAX_LOADED_SKILLS=5

# Configurable in skills_tool.py:
def max_loaded_skills() -> int:
    return 5  # Change as needed
```

---

## Best Practices

### For Users

1. **Prefer marketplace skills** - They're battle-tested
2. **Check install counts** - Higher = more reliable
3. **Customize after install** - Adapt to your needs
4. **Share custom skills** - Contribute back to marketplace

### For Agents

1. **Search before creating** - Don't reinvent the wheel
2. **Install high-count skills** - Better quality
3. **Cache marketplace results** - Faster subsequent searches
4. **Validate downloaded skills** - Check YAML frontmatter

---

## Troubleshooting

### Skill Not Found

**Problem**: `Error: skill not found locally`

**Solution**:
```python
# Search marketplace
skills_tool(method="search", query="skill_name")

# Or create custom
skills_tool(
    method="create",
    skill_name="skill-name",
    description="What it does"
)
```

### Marketplace Search Fails

**Problem**: `Could not search skills.sh marketplace`

**Solution**:
1. Check internet connection
2. Verify browser_agent is working
3. Try direct URL: https://skills.sh
4. Fallback to manual skill creation

### Installation Fails

**Problem**: `Could not fetch SKILL.md from GitHub`

**Solution**:
1. Verify skill exists on GitHub
2. Check URL format: `owner/repo/skill`
3. Try without skill path: `owner/repo`
4. Check GitHub API rate limits

---

## Integration with Other Tools

### n8n Workflows

Create skill for n8n automation:

```python
skills_tool(
    method="create",
    skill_name="n8n-automation",
    description="Create and manage n8n workflows using n8n_tool"
)
```

### Foam PKM

Create skill for Zettelkasten notes:

```python
skills_tool(
    method="create",
    skill_name="foam-zettelkasten",
    description="Manage atomic notes in Foam vault using foam_zettel"
)
```

### Code Execution

Skills can reference tools:

```markdown
## Instructions

### Step 1: Write code
Use code_execution_tool to run Python:

```python
import pandas as pd
# Your code here
```
```

---

## API Reference

### skills_tool Methods

#### list
List all locally available skills

```python
skills_tool(method="list")
```

#### search
Search local skills + marketplace with fallback

```python
skills_tool(method="search", query="keyword")
```

#### load
Load skill into agent context (max 5 simultaneous)

```python
skills_tool(method="load", skill_name="skill-name")
```

#### install_from_marketplace
Download skill from skills.sh via GitHub

```python
skills_tool(
    method="install_from_marketplace",
    skill_name="owner/repo/skill"
)
```

#### create
Auto-generate custom skill template

```python
skills_tool(
    method="create",
    skill_name="my-skill",
    description="What it does"
)
```

---

## Contributing Skills

### Publish to Marketplace

1. **Create GitHub repo** with skills directory
2. **Add SKILL.md files** following standard
3. **Submit to skills.sh** via their CLI or web form
4. **Share with community**

### SKILL.md Standard

Follow Anthropic's open standard:
- YAML frontmatter (name, description, tags, triggers)
- Markdown body (instructions, examples, best practices)
- Compatible with 20+ AI coding agents

### Example Repository Structure

```
my-skills-repo/
├── README.md
├── skills/
│   ├── skill-one/
│   │   ├── SKILL.md
│   │   └── scripts/
│   ├── skill-two/
│   │   └── SKILL.md
│   └── skill-three/
│       ├── SKILL.md
│       └── templates/
└── .github/
    └── workflows/
```

---

## Resources

### Official Links
- [skills.sh Marketplace](https://skills.sh)
- [Anthropic Skills Repository](https://github.com/anthropics/skills)
- [SKILL.md Standard](https://www.mintlify.com/blog/skill-md)
- [Complete Guide to Building Skills](https://resources.anthropic.com/hubfs/The-Complete-Guide-to-Building-Skill-for-Claude.pdf)

### Community
- [Claude Developers Discord](https://discord.gg/claude-devs)
- [GitHub Issues](https://github.com/anthropics/skills/issues)
- [Cursor Docs: Agent Skills](https://cursor.com/docs/context/skills)

### Tools
- [Vercel Skills CLI](https://www.npmjs.com/package/@vercel/skills-cli)
- [LobeHub Market CLI](https://www.npmjs.com/package/@lobehub/market-cli)
- [Playbooks Skills](https://playbooks.com/skills)

---

## What's Next

### Planned Enhancements

1. **Skill caching** - Local marketplace index for offline search
2. **Version management** - Update skills when new versions available
3. **Skill analytics** - Track which skills are most useful
4. **Batch installation** - Install multiple skills at once
5. **Skill recommendations** - AI suggests relevant skills for tasks

### Contributing

Want to improve the skills integration? See [CONTRIBUTING.md](../../CONTRIBUTING.md)

---

**Carbon Fiber Principle**: Maximum capability discovery, minimum manual intervention.
