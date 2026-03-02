# Spacebot-Inspired Agent Hierarchy Implementation Plan

**Feature Branch**: `feature/agent-hierarchy`  
**Status**: 📋 PLANNING  
**Priority**: HIGH  
**Estimated Effort**: 10 hours MVP (24 hours full)  
**Target Release**: v1.1-onebot-os

---

## Executive Summary

Add Spacebot-inspired visual agent hierarchy to Agent Zero, enabling users to see and monitor agent coordination in real-time. Implementation follows MVP-first strategy: ship core visualization (10h) before investing in advanced features.

**Inspiration Source**: [Spacebot by Spacedrive](https://github.com/spacedriveapp/spacebot) (FSL-1.1-ALv2 license)  
**Approach**: Study patterns, reimplement in Python/JS (not Rust), credit Spacebot  
**Legal Compliance**: ✅ No direct code copying, architecture patterns only

---

## What We're Building

### Phase 1: Study & Design (2 hours)
**Deliverable**: Architecture documentation  
**Status**: TODO

**Tasks**:
- [ ] Clone Spacebot repository
- [ ] Study process architecture (`src/process/`)
- [ ] Study memory system (`src/memory/`)
- [ ] Study UI components (`interface/src/`)
- [ ] Document patterns to adapt
- [ ] Create data structure designs

**Outputs**:
- `docs/research/spacebot-patterns.md` - Architecture notes
- `docs/research/agent-hierarchy-schema.json` - Data structures
- `docs/research/agent-api-spec.md` - API endpoints

**Commands**:
```bash
git clone https://github.com/spacedriveapp/spacebot.git /tmp/spacebot
cd /tmp/spacebot
# Study these files:
cat src/process/*.rs
cat src/memory/*.rs
cat interface/src/components/*.tsx
```

---

### Phase 2: Agent Tree Visualization (8 hours)
**Deliverable**: Real-time agent hierarchy UI  
**Status**: TODO

Broken into 3 mini-PRs for incremental delivery:

#### Mini PR #7a: Basic Agent List (2 hours)

**Tasks**:
- [ ] Create agent list component
- [ ] Add WebSocket event: `agent_spawned`
- [ ] Add WebSocket event: `agent_completed`
- [ ] Create backend endpoint: `GET /api/agents`
- [ ] Display active agents in sidebar
- [ ] Show agent profile badges

**Files to Create**:
```
webui/components/agent-list.js
python/api/endpoints/agents.py
```

**Files to Modify**:
```
webui/index.html (add agent list container)
webui/index.js (WebSocket event handlers)
python/api/websocket.py (add events)
```

**Code Pattern** (agent-list.js):
```javascript
class AgentList {
  constructor(container) {
    this.container = container;
    this.agents = new Map();
  }
  
  addAgent(agent) {
    this.agents.set(agent.id, agent);
    this.render();
  }
  
  render() {
    this.container.innerHTML = Array.from(this.agents.values())
      .map(a => `
        <div class="agent-item">
          <span class="badge">${a.profile}</span>
          <span class="status ${a.status}">${a.status}</span>
        </div>
      `).join('');
  }
}
```

**Testing**:
```bash
# Test with subordinate agent
curl -X POST http://localhost:8000/api/chat \\
  -d '{"message": "Use call_subordinate to analyze data"}'
# Verify agent appears in UI list
```

---

#### Mini PR #7b: Tree Visualization (3 hours)

**Tasks**:
- [ ] Install vis-network: `npm install vis-network`
- [ ] Create agent-tree.js component
- [ ] Add hierarchical layout
- [ ] Show parent-child relationships
- [ ] Add click to view agent details
- [ ] Style nodes with agent profiles

**Files to Create**:
```
webui/components/agent-tree.js
webui/css/agent-tree.css
```

**Files to Modify**:
```
webui/index.html (add tree container)
webui/index.js (initialize tree)
package.json (add vis-network)
```

**Code Pattern** (agent-tree.js):
```javascript
import { Network } from 'vis-network/standalone';

class AgentTreeViewer {
  constructor(container) {
    this.container = container;
    this.nodes = new vis.DataSet();
    this.edges = new vis.DataSet();
    
    const options = {
      layout: { 
        hierarchical: { 
          direction: 'UD',
          sortMethod: 'directed'
        } 
      },
      nodes: {
        shape: 'box',
        color: { background: '#6366f1', border: '#4f46e5' },
        font: { color: '#ffffff' }
      },
      edges: { 
        arrows: 'to',
        color: '#94a3b8'
      }
    };
    
    this.network = new Network(
      this.container,
      { nodes: this.nodes, edges: this.edges },
      options
    );
  }
  
  addAgent(id, name, profile, parent = null) {
    this.nodes.add({ 
      id, 
      label: name, 
      title: profile,
      color: this.getProfileColor(profile)
    });
    
    if (parent) {
      this.edges.add({ from: parent, to: id });
    }
  }
  
  getProfileColor(profile) {
    const colors = {
      'agent0': '#6366f1',
      'hacker': '#ef4444',
      'researcher': '#10b981',
      'browser_agent': '#f59e0b',
      'code_agent': '#8b5cf6'
    };
    return { background: colors[profile] || '#6366f1' };
  }
  
  updateStatus(id, status) {
    const color = status === 'executing' ? '#10b981' : '#6366f1';
    this.nodes.update({ id, color: { background: color } });
  }
}
```

**Testing**:
```bash
# Test tree layout
# Create subordinate agents, verify tree structure appears
# Click nodes, verify details panel opens
```

---

#### Mini PR #7c: Real-time Updates (3 hours)

**Tasks**:
- [ ] Create agent_monitor.py backend
- [ ] Add agent lifecycle tracking
- [ ] Add WebSocket event: `agent_status_changed`
- [ ] Update tree on agent status changes
- [ ] Add context size indicators
- [ ] Add performance metrics display

**Files to Create**:
```
python/api/agent_monitor.py
```

**Files to Modify**:
```
python/agent.py (add lifecycle hooks)
python/api/websocket.py (add status events)
webui/components/agent-tree.js (handle updates)
```

**Code Pattern** (agent_monitor.py):
```python
from datetime import datetime
from typing import Dict, Optional

class AgentMonitor:
    def __init__(self):
        self.active_agents: Dict[str, dict] = {}
    
    async def track_agent(self, agent_id: str, agent_info: dict):
        """Track agent lifecycle"""
        self.active_agents[agent_id] = {
            "id": agent_id,
            "name": agent_info.get("name", "Agent"),
            "profile": agent_info.get("profile", "agent0"),
            "status": "active",
            "created_at": datetime.now().isoformat(),
            "parent_id": agent_info.get("parent_id"),
            "context_size": agent_info.get("context_size", 0)
        }
        await self.broadcast_update()
    
    async def update_status(self, agent_id: str, status: str):
        """Update agent status"""
        if agent_id in self.active_agents:
            self.active_agents[agent_id]["status"] = status
            await self.broadcast_update()
    
    async def broadcast_update(self):
        """Send hierarchy to frontend via WebSocket"""
        from python.api.websocket import websocket_manager
        await websocket_manager.broadcast({
            "type": "agent_hierarchy",
            "data": list(self.active_agents.values())
        })
    
    def get_hierarchy(self) -> dict:
        """Get current agent hierarchy"""
        return {
            "agents": list(self.active_agents.values()),
            "total": len(self.active_agents)
        }

# Global instance
agent_monitor = AgentMonitor()
```

**Integration** (python/agent.py):
```python
# Add to Agent class __init__
from python.api.agent_monitor import agent_monitor

async def __init__(self, ...):
    # ... existing code ...
    await agent_monitor.track_agent(self.id, {
        "name": self.name,
        "profile": self.config.get("profile", "agent0"),
        "parent_id": self.parent_id if hasattr(self, 'parent_id') else None,
        "context_size": len(self.context)
    })

async def set_status(self, status: str):
    await agent_monitor.update_status(self.id, status)
```

**Testing**:
```bash
# Test real-time updates
# Start agent, verify tree updates
# Agent completes task, verify status changes
# Monitor WebSocket events in browser DevTools
```

---

### Phase 3: Concurrent Agent Pool (6 hours)
**Deliverable**: Multi-user concurrent execution  
**Status**: TODO (AFTER Phase 2)

**Decision Point**: Evaluate Phase 2 user feedback before implementing

**Tasks**:
- [ ] Design agent pool architecture
- [ ] Create agent_pool.py
- [ ] Add ThreadPoolExecutor integration
- [ ] Add per-user agent isolation
- [ ] Add resource limits (max 5 concurrent)
- [ ] Add graceful shutdown
- [ ] Update UI to show pool status
- [ ] Test multi-user scenarios

**Files to Create**:
```
python/helpers/agent_pool.py
```

**Files to Modify**:
```
python/helpers/settings.py (add pool config)
python/agent.py (integrate with pool)
webui/components/agent-monitor.js (show pool status)
```

**Code Pattern** (agent_pool.py):
```python
from concurrent.futures import ThreadPoolExecutor
from typing import Dict, Optional
import asyncio

class AgentPool:
    def __init__(self, max_agents: int = 5):
        self.pool = ThreadPoolExecutor(max_workers=max_agents)
        self.active_agents: Dict[str, any] = {}
        self.max_agents = max_agents
    
    async def spawn_agent(self, task: str, user_id: str) -> str:
        """Spawn agent in pool"""
        if len(self.active_agents) >= self.max_agents:
            raise Exception(f"Agent pool full ({self.max_agents} active)")
        
        from python.agent import Agent
        agent = Agent(user_id=user_id)
        agent_id = agent.id
        
        future = self.pool.submit(agent.run, task)
        self.active_agents[user_id] = {
            "agent": agent,
            "future": future,
            "agent_id": agent_id
        }
        
        return agent_id
    
    async def shutdown(self):
        """Graceful shutdown"""
        self.pool.shutdown(wait=True)

# Global instance
agent_pool = AgentPool(max_agents=5)
```

**Configuration** (.env):
```bash
# Agent Pool Settings
MAX_CONCURRENT_AGENTS=5
AGENT_TIMEOUT_SECONDS=300
ENABLE_AGENT_POOL=true
```

---

### Phase 4: Typed Memory System (6 hours)
**Deliverable**: 8 memory types with FAISS + Foam integration  
**Status**: TODO (AFTER Phase 2)

**🔥 KEY INTEGRATION**: Unifies existing FAISS vector memory + Foam PKM

**Decision Point**: Evaluate Phase 2 user feedback before implementing

#### Architecture: Unified Memory Layer

```
┌─────────────────────────────────────────────────┐
│           Agent Zero Memory Layer               │
├─────────────────────────────────────────────────┤
│                                                 │
│  ┌──────────────────────────────────────────┐  │
│  │      Typed Memory (Phase 4 - NEW)       │  │
│  │  8 memory types + graph relationships   │  │
│  │  Integration layer for both systems     │  │
│  └──────────────┬──────────────┬────────────┘  │
│                 │              │                │
│                 ▼              ▼                │
│  ┌──────────────────┐  ┌─────────────────┐    │
│  │  Vector Memory   │  │   Foam Vault    │    │
│  │  (FAISS - EXISTS)│  │  (Zettelkasten) │    │
│  │                  │  │   (EXISTS)      │    │
│  │  • Fast search   │  │  • Structured   │    │
│  │  • Embeddings    │  │  • Markdown     │    │
│  │  • metadata      │  │  • Links        │    │
│  └──────────────────┘  └─────────────────┘    │
│                                                 │
└─────────────────────────────────────────────────┘
```

#### How It Works

**1. Store Operation** (writes to both systems):
```python
# Agent learns a fact
await typed_memory.store(
    content="Python uses dynamic typing",
    memory_type=MemoryType.FACT,
    persist_to_foam=True  # Also creates Foam zettel
)

# Result:
# ✓ FAISS vector DB entry with type="fact" metadata
# ✓ Foam note: foam/zettelkasten/permanent/fact-python-uses-dynamic-typing.md
```

**2. Recall Operation** (queries FAISS by type):
```python
# Agent recalls facts about Python
facts = await typed_memory.recall_by_type(
    query="Python typing",
    memory_type=MemoryType.FACT
)

# Returns only documents with type="fact" from FAISS
# Fast semantic search with type filtering
```

**3. Foam Integration** (structured persistence):
```python
# Important memories → Foam permanent notes
if memory_type in [MemoryType.FACT, MemoryType.SKILL, MemoryType.SUCCESS]:
    # Auto-create Zettelkasten note with:
    # - Markdown formatting
    # - Graph connections [[links]]
    # - PARA organization
    # - Human-readable knowledge base
```

#### Tasks

- [ ] Define 8 memory types enum
- [ ] Create typed_memory.py (integration layer)
- [ ] Extend memory.py with type field (FAISS metadata)
- [ ] Extend foam_zettel.py with auto-create from typed memory
- [ ] Add graph relationship support
- [ ] Update memory_tool.py for typed queries
- [ ] Add memory type filter in UI
- [ ] Test memory recall by type
- [ ] Test Foam auto-creation

**Files to Create**:
```
python/helpers/typed_memory.py (integration layer)
```

**Files to Modify**:
```
python/helpers/memory.py (add type metadata support)
python/tools/memory_tool.py (typed queries)
python/tools/foam_zettel.py (auto-create from typed memory)
webui/components/agent-tree.js (show memory types)
```

#### Code Pattern (typed_memory.py):
```python
from enum import Enum
from typing import List, Optional
from python.helpers.memory import Memory
from python.tools.foam_zettel import FoamZettelTool

class MemoryType(Enum):
    FACT = "fact"               # Verified information
    OPINION = "opinion"         # Subjective views
    PREFERENCE = "preference"   # User preferences
    TASK = "task"              # Completed tasks
    SKILL = "skill"            # Learned skills
    CONTEXT = "context"        # Conversation context
    ERROR = "error"            # Mistakes to avoid
    SUCCESS = "success"        # Successful patterns

class TypedMemory:
    """
    Unified typed memory layer integrating:
    - FAISS vector DB (fast semantic search)
    - Foam PKM (structured Zettelkasten notes)
    """
    
    def __init__(self, agent):
        self.agent = agent
        self.vector_memory = None  # Lazy load via Memory.get(agent)
        self.foam = FoamZettelTool()
    
    async def _get_vector_memory(self):
        if not self.vector_memory:
            self.vector_memory = await Memory.get(self.agent)
        return self.vector_memory
    
    async def store(
        self, 
        content: str, 
        memory_type: MemoryType,
        persist_to_foam: bool = True,
        foam_links: List[str] = []
    ):
        """
        Store typed memory in both FAISS and Foam
        
        Args:
            content: Memory content
            memory_type: One of 8 memory types
            persist_to_foam: Create Foam zettel (default True for important types)
            foam_links: Wiki links for Foam note
        
        Returns:
            vector_id: FAISS document ID
        """
        
        # 1. Store in FAISS vector memory with type metadata
        mem = await self._get_vector_memory()
        metadata = {
            "type": memory_type.value,
            "area": Memory.Area.MAIN.value,
            "timestamp": Memory.get_timestamp()
        }
        vector_id = await mem.insert_text(content, metadata)
        
        # 2. Optionally create Foam zettel (structured permanent note)
        important_types = [MemoryType.FACT, MemoryType.SKILL, MemoryType.SUCCESS]
        
        if persist_to_foam and memory_type in important_types:
            title = f"{memory_type.value.title()}: {content[:50]}"
            await self.foam.execute(
                action="create_zettel",
                title=title,
                content=content,
                tags=[memory_type.value, "agent-memory", "auto-created"],
                links=foam_links
            )
        
        return vector_id
    
    async def recall_by_type(
        self, 
        query: str, 
        memory_type: Optional[MemoryType] = None,
        limit: int = 5,
        threshold: float = 0.7
    ):
        """
        Recall memories from FAISS filtered by type
        
        Args:
            query: Search query
            memory_type: Filter by specific type (None = all types)
            limit: Max results
            threshold: Similarity threshold
        
        Returns:
            List of Document objects with scores
        """
        mem = await self._get_vector_memory()
        
        # Build filter condition
        filter_condition = ""
        if memory_type:
            filter_condition = f"type == '{memory_type.value}'"
        
        results = await mem.search_similarity_threshold(
            query=query,
            limit=limit,
            threshold=threshold,
            filter=filter_condition
        )
        
        return results
    
    async def get_facts(self, query: str, limit: int = 5):
        """Quick helper: recall facts"""
        return await self.recall_by_type(query, MemoryType.FACT, limit)
    
    async def get_skills(self, query: str, limit: int = 5):
        """Quick helper: recall skills"""
        return await self.recall_by_type(query, MemoryType.SKILL, limit)
    
    async def get_successes(self, query: str, limit: int = 5):
        """Quick helper: recall successful patterns"""
        return await self.recall_by_type(query, MemoryType.SUCCESS, limit)
    
    async def get_errors(self, query: str, limit: int = 5):
        """Quick helper: recall errors to avoid"""
        return await self.recall_by_type(query, MemoryType.ERROR, limit)
```

#### Memory.py Enhancement (backwards compatible):
```python
# python/helpers/memory.py (MODIFY)

class Memory:
    # ... existing code ...
    
    async def insert_text(self, text, metadata: dict = {}):
        """
        Enhanced to support typed memory (backwards compatible)
        Existing memories without 'type' continue working
        """
        # Add type support (defaults to 'generic' for existing code)
        if 'type' not in metadata:
            metadata['type'] = 'generic'
        
        doc = Document(text, metadata=metadata)
        ids = await self.insert_documents([doc])
        return ids[0]
    
    async def search_by_type(
        self, 
        query: str, 
        memory_type: str, 
        limit: int = 5,
        threshold: float = 0.7
    ):
        """
        NEW: Search memories filtered by type
        Uses existing search_similarity_threshold with type filter
        """
        filter_condition = f"type == '{memory_type}'"
        return await self.search_similarity_threshold(
            query=query,
            limit=limit,
            threshold=threshold,
            filter=filter_condition
        )
```

#### Foam Integration Enhancement:
```python
# python/tools/foam_zettel.py (MODIFY)

class FoamZettelTool(Tool):
    # ... existing code ...
    
    async def create_from_typed_memory(
        self,
        memory_type: str,
        content: str,
        links: List[str] = []
    ):
        """
        NEW: Create Foam zettel from typed memory
        Called by TypedMemory.store()
        """
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        rand_id = random.randint(1000, 9999)
        note_id = f"{timestamp}-{rand_id}"
        
        title = f"{memory_type.title()}: {content[:50]}"
        filename = f"{memory_type}-{title.lower().replace(' ', '-')[:30]}.md"
        filepath = os.path.join(
            "/app/foam",
            "zettelkasten/permanent",
            filename
        )
        
        note_content = f"""---
id: {note_id}
type: permanent
memory_type: {memory_type}
tags: [agent-memory, {memory_type}, auto-created]
created: {datetime.now().isoformat()}
---

# {title}

{content}

## Memory Metadata

- **Type**: {memory_type}
- **Auto-created**: Yes
- **Source**: Agent Zero Typed Memory

## Connections

{chr(10).join([f'- [[{link}]]' for link in links])}
"""
        
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, 'w') as f:
            f.write(note_content)
        
        return filepath
```

#### Memory Tool Enhancement:
```python
# python/tools/memory_tool.py (MODIFY)

class MemoryTool(Tool):
    # ... existing code ...
    
    async def execute(self, **kwargs):
        memory_type = kwargs.get('type')  # Optional type filter
        query = kwargs.get('query')
        
        if memory_type:
            # NEW: Use typed memory for filtered search
            from python.helpers.typed_memory import TypedMemory, MemoryType
            typed_mem = TypedMemory(self.agent)
            results = await typed_mem.recall_by_type(
                query=query,
                memory_type=MemoryType(memory_type)
            )
        else:
            # Existing: Generic memory search
            memory = await Memory.get(self.agent)
            results = await memory.search_similarity_threshold(
                query=query,
                limit=5,
                threshold=0.7
            )
        
        return Response(
            message=Memory.format_docs_plain(results),
            break_loop=False
        )
```

#### Example Usage:
```python
# Agent stores a fact (goes to FAISS + Foam)
from python.helpers.typed_memory import TypedMemory, MemoryType

typed_mem = TypedMemory(agent)

await typed_mem.store(
    content="FastAPI uses Pydantic for request validation",
    memory_type=MemoryType.FACT,
    persist_to_foam=True,
    foam_links=["FastAPI", "Pydantic", "Python"]
)

# Later, agent recalls facts about FastAPI
facts = await typed_mem.get_facts("FastAPI validation")

# Result:
# - Fast FAISS vector search (type="fact")
# - Human-readable Foam note created
# - Graph connections via [[FastAPI]] [[Pydantic]]
```

#### Benefits:

**For FAISS Vector Memory**:
- ✅ Adds type metadata (backwards compatible)
- ✅ Enables filtered search by type
- ✅ Fast semantic search remains unchanged
- ✅ Existing memories continue working

**For Foam PKM**:
- ✅ Important memories auto-create zettels
- ✅ Structured permanent notes
- ✅ Human-readable knowledge base
- ✅ Graph visualization in Foam UI

**Combined System**:
- ✅ Best of both worlds
- ✅ Machine-readable (FAISS) + Human-readable (Foam)
- ✅ Fast recall + Deep organization
- ✅ Vector search + Zettelkasten methodology

**Testing**:
```bash
# Test typed memory storage
python -c "
from python.helpers.typed_memory import TypedMemory, MemoryType
typed_mem = TypedMemory(agent)
await typed_mem.store('Test fact', MemoryType.FACT)
"

# Verify FAISS entry
# Check foam/zettelkasten/permanent/ for new note

# Test typed recall
facts = await typed_mem.get_facts('test')
print(len(facts))  # Should find the fact

# Test Foam note exists
ls -la foam/zettelkasten/permanent/ | grep fact
```

---

### Phase 5: Polish & Documentation (2 hours)
**Deliverable**: User guides, credits, demo  
**Status**: TODO (AFTER Phase 2-4)

**Tasks**:
- [ ] Create agent-hierarchy.md guide
- [ ] Create typed-memory-foam-integration.md guide
- [ ] Update README with new features
- [ ] Record demo video/screenshots
- [ ] Add Spacebot credit to CREDITS.md
- [ ] Create troubleshooting guide

**Files to Create**:
```
docs/guides/agent-hierarchy.md
docs/guides/concurrent-agents.md
docs/guides/typed-memory-foam-integration.md (NEW)
CREDITS.md
```

**Files to Modify**:
```
README.md (add feature showcase)
docs/guides/ZETTELKASTEN.md (add typed memory section)
```

---

## Technical Architecture

### WebSocket Events

**New Events**:
```javascript
// agent_spawned
{
  type: "agent_spawned",
  data: {
    agent_id: "uuid",
    name: "Agent 0",
    profile: "agent0",
    parent_id: null,
    timestamp: "2026-03-02T19:00:00Z"
  }
}

// agent_status_changed
{
  type: "agent_status_changed",
  data: {
    agent_id: "uuid",
    status: "executing", // idle, thinking, executing, completed, error
    context_size: 1234,
    memory_usage: {
      vector_docs: 156,
      foam_notes: 42,
      typed_memories: {
        fact: 28,
        skill: 14,
        success: 8
      }
    }
  }
}

// agent_completed
{
  type: "agent_completed",
  data: {
    agent_id: "uuid",
    result: "success",
    duration_ms: 5432,
    memories_created: 3
  }
}

// agent_hierarchy (broadcast)
{
  type: "agent_hierarchy",
  data: {
    agents: [...],
    total: 3
  }
}

// memory_stored (NEW - Phase 4)
{
  type: "memory_stored",
  data: {
    agent_id: "uuid",
    memory_type: "fact",
    vector_id: "abc123",
    foam_note: "foam/zettelkasten/permanent/fact-example.md"
  }
}
```

### API Endpoints

**New Endpoints**:
```
GET  /api/agents              - List active agents
GET  /api/agents/:id          - Get agent details
GET  /api/agents/hierarchy    - Get agent tree
POST /api/agents/:id/kill     - Kill agent (admin only)

# Phase 4: Memory endpoints
GET  /api/memory/types        - List memory types with counts
GET  /api/memory/search       - Search typed memories
POST /api/memory/store        - Store typed memory
GET  /api/memory/foam-sync    - Sync FAISS <-> Foam
```

### Data Structures

**Agent Node**:
```typescript
interface AgentNode {
  id: string;
  name: string;
  profile: string;
  status: 'idle' | 'thinking' | 'executing' | 'completed' | 'error';
  parent_id: string | null;
  created_at: string;
  context_size: number;
  memory_stats?: {
    vector_docs: number;
    foam_notes: number;
    typed_counts: Record<string, number>;
  };
  metrics?: {
    tasks_completed: number;
    avg_response_time_ms: number;
    memory_usage_mb: number;
  };
}
```

**Agent Hierarchy**:
```typescript
interface AgentHierarchy {
  agents: AgentNode[];
  edges: Array<{
    from: string;
    to: string;
  }>;
  total: number;
}
```

**Typed Memory Document** (Phase 4):
```typescript
interface TypedMemoryDoc {
  id: string;
  content: string;
  type: 'fact' | 'opinion' | 'preference' | 'task' | 'skill' | 'context' | 'error' | 'success';
  timestamp: string;
  vector_score?: number;
  foam_note?: string;  // Path to Foam zettel if created
  relations?: string[]; // Graph edges
}
```

---

## Feature Flags

**Configuration** (.env):
```bash
# Phase 2: Agent Tree UI
ENABLE_AGENT_TREE=true

# Phase 3: Concurrent Pool
ENABLE_AGENT_POOL=false

# Phase 4: Typed Memory + Foam Integration
ENABLE_TYPED_MEMORY=false
TYPED_MEMORY_AUTO_FOAM=true  # Auto-create Foam notes for important types
TYPED_MEMORY_FOAM_TYPES=fact,skill,success  # Which types create Foam notes
```

**Usage** (python/helpers/settings.py):
```python
ENABLE_AGENT_TREE = os.getenv('ENABLE_AGENT_TREE', 'true').lower() == 'true'
ENABLE_AGENT_POOL = os.getenv('ENABLE_AGENT_POOL', 'false').lower() == 'true'
ENABLE_TYPED_MEMORY = os.getenv('ENABLE_TYPED_MEMORY', 'false').lower() == 'true'
TYPED_MEMORY_AUTO_FOAM = os.getenv('TYPED_MEMORY_AUTO_FOAM', 'true').lower() == 'true'
TYPED_MEMORY_FOAM_TYPES = os.getenv('TYPED_MEMORY_FOAM_TYPES', 'fact,skill,success').split(',')
```

---

## Timeline & Milestones

### Week 1 (4 hours)
- **Milestone**: Study complete + Agent list visible
- **Tasks**: Phase 1 (2h) + Mini PR #7a (2h)
- **Deliverable**: Basic agent list in UI
- **Success**: Users can see active agents

### Week 2 (3 hours)
- **Milestone**: Tree visualization working
- **Tasks**: Mini PR #7b (3h)
- **Deliverable**: vis-network tree display
- **Success**: Users can see agent hierarchy

### Week 3 (3 hours)
- **Milestone**: Real-time updates complete
- **Tasks**: Mini PR #7c (3h)
- **Deliverable**: WebSocket-driven updates
- **Success**: Tree updates as agents spawn/complete

### Week 4 (DECISION POINT)
- **Options**:
  - A: Ship Phase 2, gather feedback, pause ✅ RECOMMENDED
  - B: Continue with Phase 3 (concurrent pool)
  - C: Continue with Phase 4 (typed memory + Foam)
  - D: Do both Phase 3 & 4 in parallel
- **Recommendation**: **Option A** - Validate MVP before investing more

### Week 5-6 (Optional - If continuing)
- **Phase 3**: Concurrent pool (6h)
- **Phase 4**: Typed memory + Foam integration (6h)
- **Phase 5**: Polish & docs (2h)

---

## Quality Gates

### Phase 1 Checklist
- [ ] Spacebot repository studied
- [ ] Architecture patterns documented
- [ ] Data structures designed
- [ ] API endpoints specified
- [ ] Legal compliance verified (no code copying)

### Phase 2 Checklist
- [ ] vis-network installed and working
- [ ] Agent tree displays correctly
- [ ] WebSocket events trigger updates
- [ ] UI matches Agent Zero style
- [ ] Works with existing subordinate agents
- [ ] No performance degradation (<100ms UI lag)
- [ ] Documentation updated

### Phase 3 Checklist
- [ ] Agent pool creates/destroys agents correctly
- [ ] Resource limits enforced (max 5 concurrent)
- [ ] Graceful shutdown works
- [ ] Multi-user scenarios tested
- [ ] No memory leaks
- [ ] Thread safety verified
- [ ] Performance benchmarked

### Phase 4 Checklist
- [ ] 8 memory types implemented
- [ ] FAISS integration backwards compatible
- [ ] Foam auto-creation working
- [ ] Typed queries work correctly
- [ ] Graph relationships stored
- [ ] UI shows memory types
- [ ] Recall performance acceptable (<200ms)
- [ ] FAISS ↔ Foam sync tested
- [ ] No duplicate memories

---

## Success Metrics

| Metric | Target | Measure |
|--------|--------|---------||
| User adoption | 80% enable agent tree | Feature flag analytics |
| Performance | <100ms UI lag | Browser profiling |
| Stability | Zero crashes | Error tracking |
| Code quality | Clean, maintainable | Code review |
| Memory accuracy | 95% correct type | Manual validation |
| Foam sync | 100% of important types | Automated test |

---

## Risk Mitigation

### Legal Risk (LOW)
- **Mitigation**: Study patterns only, reimplement from scratch
- **Action**: Document inspiration, not derivation
- **Verification**: No Rust code copied, only concepts

### Performance Risk (MEDIUM)
- **Mitigation**: Feature flags, agent pool limits
- **Action**: Add max 5 concurrent agents, throttle updates
- **Rollback**: Disable flags if performance degrades

### Compatibility Risk (LOW)
- **Mitigation**: All features are additive, backwards compatible
- **Action**: No breaking changes to existing API
- **Testing**: Verify existing features work unchanged
- **Phase 4**: Existing FAISS memories work without types

### Memory Duplication Risk (MEDIUM - Phase 4)
- **Mitigation**: Smart Foam creation (only important types)
- **Action**: Configure which types create Foam notes
- **Testing**: Verify no duplicate zettels created

---

## Rollback Plan

**If Phase 2 fails**:
```bash
# Disable agent tree
ENABLE_AGENT_TREE=false
# Users continue with existing UI
```

**If Phase 3 fails**:
```bash
# Disable agent pool
ENABLE_AGENT_POOL=false
# Sequential execution continues
```

**If Phase 4 fails**:
```bash
# Disable typed memory
ENABLE_TYPED_MEMORY=false
# Existing FAISS memory continues (type='generic')
# Existing Foam notes unaffected
```

---

## Integration: FAISS + Foam Workflow

### Write Path (Agent stores memory)
```
Agent creates memory
       ↓
TypedMemory.store()
       ↓
   ┌───┴───┐
   ↓       ↓
FAISS    Foam
(fast)   (structured)
   ↓       ↓
vector   zettel
+ type   + links
```

### Read Path (Agent recalls memory)
```
Agent queries memory
       ↓
TypedMemory.recall_by_type()
       ↓
    FAISS search
    (filtered by type)
       ↓
    Results
    (with Foam links if exist)
```

### Example: Agent learns from error
```python
# Agent encounters CORS error and fixes it
await typed_memory.store(
    content="""
    CORS Error Fix:
    Problem: Browser blocked API request
    Solution: Add CORS headers in middleware
    Code: app.add_middleware(CORSMiddleware, allow_origins=["*"])
    """,
    memory_type=MemoryType.SUCCESS,
    persist_to_foam=True,
    foam_links=["CORS", "FastAPI", "Middleware", "Debugging"]
)

# Result:
# 1. FAISS: Fast vector entry (searchable)
# 2. Foam: foam/zettelkasten/permanent/success-cors-error-fix.md
#    With links to: [[CORS]] [[FastAPI]] [[Middleware]] [[Debugging]]

# Later, agent faces similar issue:
solutions = await typed_memory.get_successes("CORS browser error")
# → Instantly retrieves past solution from FAISS
# → User can review structured Foam note for context
```

---

## Credits & Legal

**Inspiration**: [Spacebot by Spacedrive](https://github.com/spacedriveapp/spacebot)  
**License**: FSL-1.1-ALv2 (Functional Source License)  
**Compliance**: Architecture patterns studied, no code copied  
**Implementation**: Original Python/JS codebase for Agent Zero

**To Add** (CREDITS.md):
```markdown
## Spacebot

Agent hierarchy visualization inspired by [Spacebot](https://github.com/spacedriveapp/spacebot) 
by the Spacedrive team. We studied their innovative multi-agent architecture and adapted the 
concepts to Agent Zero's Python/JS stack. No Rust code was copied; only patterns were reimplemented.

Memory system architecture inspired by Spacebot's typed memory approach, adapted to integrate
with our existing FAISS vector database and Foam Zettelkasten PKM system.

License: FSL-1.1-ALv2 (Functional Source License)
```

---

## Development Commands

### Setup
```bash
# Install dependencies
npm install vis-network

# Enable feature flags
echo "ENABLE_AGENT_TREE=true" >> .env
echo "ENABLE_TYPED_MEMORY=false" >> .env
echo "TYPED_MEMORY_AUTO_FOAM=true" >> .env
```

### Development
```bash
# Run Agent Zero
docker compose up

# Watch logs
docker compose logs -f agent-zero

# Test WebSocket events
# Open browser DevTools → Network → WS
```

### Testing
```bash
# Test agent spawning
curl -X POST http://localhost:8000/api/chat \\
  -d '{"message": "Use call_subordinate to research quantum computing"}'

# Test hierarchy endpoint
curl http://localhost:8000/api/agents/hierarchy

# Test typed memory (Phase 4)
curl -X POST http://localhost:8000/api/memory/store \\
  -d '{"content": "Test fact", "type": "fact", "persist_to_foam": true}'

# Check Foam notes created
ls -la foam/zettelkasten/permanent/ | grep agent-memory
```

---

## Carbon Fiber Principle Applied

✅ **Maximum Strength**: Full agent hierarchy + typed memory + Foam integration  
✅ **Minimum Weight**: 10h MVP, clean implementation, no bloat  
✅ **No Unnecessary Complexity**: Start simple (Phase 2), add only when validated  
✅ **AI-First**: Code clear for both humans and AI  
✅ **Integration Over Reinvention**: Use existing FAISS + Foam, don't rebuild

**Every line earns its place. YAGNI principle enforced. Build what users need.**

---

## Next Steps

1. **Review this plan** - Confirm approach
2. **Create feature branch**:
   ```bash
   git checkout -b feature/agent-hierarchy
   ```

3. **Start Phase 1** (2 hours):
   ```bash
   git clone https://github.com/spacedriveapp/spacebot.git /tmp/spacebot
   # Study and document patterns
   ```

4. **Create Mini PR #7a** (2 hours):
   ```bash
   # Implement basic agent list
   git checkout -b feature/agent-list
   # ... code ...
   git commit -m "Add basic agent list UI"
   ```

5. **Ship MVP** (Week 3):
   - Merge all Mini PRs
   - Deploy to production
   - Gather user feedback

6. **Decision Point** (Week 4):
   - Evaluate user adoption (target: 80%)
   - Decide on Phase 3/4 investment
   - If proceeding with Phase 4: Test FAISS + Foam integration thoroughly

---

**Status**: ✅ DMAIC Complete - Ready for Implementation  
**Approval**: ✅ APPROVED  
**Location**: `docs/roadmap/spacebot-inspired-hierarchy.md`

---

## FAQ

### Q: Will Phase 4 break existing memories?
**A**: No. Existing FAISS memories continue working with `type='generic'`. Typed memory is purely additive.

### Q: Will Phase 4 create duplicate notes?
**A**: No. Foam auto-creation is configurable via `TYPED_MEMORY_FOAM_TYPES`. Only important types (fact, skill, success) create zettels by default.

### Q: Can I disable Foam auto-creation?
**A**: Yes. Set `TYPED_MEMORY_AUTO_FOAM=false` to keep typed memory in FAISS only.

### Q: How do I query typed memories?
**A**: Use memory tool with type parameter: `{"query": "Python", "type": "fact"}` or use TypedMemory API directly.

### Q: Will this slow down memory recall?
**A**: No. Type filtering uses FAISS metadata (already fast). Target: <200ms recall time.

### Q: Can I manually create Foam notes for existing memories?
**A**: Yes. A sync tool will be provided to backfill Foam notes from typed FAISS memories.
