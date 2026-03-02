from __future__ import annotations

from pathlib import Path
from typing import List
import subprocess
import json

from python.helpers.tool import Tool, Response
from python.helpers import projects, files, file_tree
from python.helpers import skills as skills_helper, runtime


DATA_NAME_LOADED_SKILLS = "loaded_skills"
SKILLS_SH_URL = "https://skills.sh"


class SkillsTool(Tool):
    """
    Manage and use SKILL.md-based Skills (Anthropic open standard).
    
    Fallback workflow:
    1. Search local skills directory
    2. If not found, search skills.sh marketplace using browser_agent
    3. If still not found, auto-create skill using skill-creator pattern

    Methods (tool_args.method):
      - list
      - search (query) - searches local + skills.sh
      - load (skill_name)
      - create (skill_name, description) - auto-create missing skill
      - install_from_marketplace (skill_name) - download from skills.sh
    """

    async def execute(self, **kwargs) -> Response:
        method = (
            (kwargs.get("method") or self.args.get("method") or self.method or "")
            .strip()
            .lower()
        )

        try:
            if method == "list":
                return Response(message=self._list(), break_loop=False)
            
            if method == "search":
                query = str(kwargs.get("query") or "").strip()
                return Response(message=await self._search_with_fallback(query), break_loop=False)
            
            if method == "load":
                skill_name = str(kwargs.get("skill_name") or "").strip()
                return Response(message=await self._load_with_fallback(skill_name), break_loop=False)
            
            if method == "create":
                skill_name = str(kwargs.get("skill_name") or "").strip()
                description = str(kwargs.get("description") or "").strip()
                return Response(message=self._create_skill(skill_name, description), break_loop=False)
            
            if method == "install_from_marketplace":
                skill_name = str(kwargs.get("skill_name") or "").strip()
                return Response(message=await self._install_from_marketplace(skill_name), break_loop=False)

            return Response(
                message="Error: missing/invalid 'method'. Supported: list, search, load, create, install_from_marketplace.",
                break_loop=False,
            )
        except Exception as e:
            return Response(message=f"Error in skills_tool: {e}", break_loop=False)

    def _list(self) -> str:
        """List all locally available skills"""
        skills = skills_helper.list_skills(
            agent=self.agent,
            include_content=False,
        )
        if not skills:
            return f"No local skills found. Search skills.sh marketplace: skills_tool method=search query='your_topic'"

        skills_sorted = sorted(skills, key=lambda s: s.name.lower())

        lines: List[str] = []
        lines.append(f"Available local skills ({len(skills_sorted)}):")
        for s in skills_sorted:
            tags = f" tags={','.join(s.tags)}" if s.tags else ""
            ver = f" v{s.version}" if s.version else ""
            desc = (s.description or "").strip()
            if len(desc) > 200:
                desc = desc[:200].rstrip() + "…"
            lines.append(f"- {s.name}{ver}{tags}: {desc}")
        lines.append("")
        lines.append("Tip: Use method=search to find skills in skills.sh marketplace.")
        return "\n".join(lines)

    async def _search_with_fallback(self, query: str) -> str:
        """Search local skills, then skills.sh marketplace if not found"""
        if not query:
            return "Error: 'query' is required for method=search."

        # Step 1: Search local skills
        local_results = self._search_local(query)
        
        if local_results:
            return local_results
        
        # Step 2: No local matches, search skills.sh marketplace
        marketplace_msg = f"\nNo local skills found for '{query}'. Searching skills.sh marketplace...\n\n"
        marketplace_results = await self._search_marketplace(query)
        
        if "No skills found" in marketplace_results:
            # Step 3: No marketplace matches either, suggest creation
            return marketplace_msg + marketplace_results + f"\n\nSuggestion: Create custom skill with:\nskills_tool method=create skill_name='{query.replace(' ', '-')}' description='Description here'"
        
        return marketplace_msg + marketplace_results

    def _search_local(self, query: str) -> str:
        """Search only local skills directory"""
        skills = skills_helper.list_skills(
            agent=self.agent,
            include_content=True,
        )
        
        if not skills:
            return ""
        
        # Filter by name, description, or tags
        query_lower = query.lower()
        matches = [
            s for s in skills
            if query_lower in s.name.lower()
            or query_lower in (s.description or "").lower()
            or any(query_lower in tag.lower() for tag in (s.tags or []))
        ]
        
        if not matches:
            return ""
        
        lines: List[str] = []
        lines.append(f"Local skills matching '{query}' ({len(matches)}):")
        for s in matches:
            desc = (s.description or "").strip()
            if len(desc) > 200:
                desc = desc[:200].rstrip() + "…"
            lines.append(f"- {s.name}: {desc}")
        lines.append("")
        lines.append(f"Load with: skills_tool method=load skill_name='<name>'")
        return "\n".join(lines)

    async def _search_marketplace(self, query: str) -> str:
        """Search skills.sh marketplace using browser agent"""
        try:
            # Use browser_agent to search skills.sh
            search_url = f"{SKILLS_SH_URL}?q={query.replace(' ', '+')}"
            
            # Delegate to browser_agent tool for actual search
            browser_result = await self.agent.call_tool(
                "browser_agent",
                task=f"Search skills.sh for '{query}' skills. Extract: skill name, install count, description, GitHub URL. Return top 5 results.",
                url=search_url
            )
            
            if browser_result and "error" not in browser_result.lower():
                return f"Skills.sh marketplace results:\n{browser_result}\n\nInstall with: skills_tool method=install_from_marketplace skill_name='owner/repo/skill'"
            else:
                return f"No skills found on skills.sh for '{query}'."
                
        except Exception as e:
            return f"Could not search skills.sh marketplace: {e}"

    async def _load_with_fallback(self, skill_name: str) -> str:
        """Load skill with automatic marketplace fallback"""
        skill_name = skill_name.strip()
        if skill_name.startswith("**") and skill_name.endswith("**"):
            skill_name = skill_name[2:-2]

        if not skill_name:
            return "Error: 'skill_name' is required for method=load."

        # Try local first
        skill = skills_helper.find_skill(
            skill_name,
            include_content=False,
            agent=self.agent,
        )
        
        if skill:
            # Load from local
            if not self.agent.data.get(DATA_NAME_LOADED_SKILLS):
                self.agent.data[DATA_NAME_LOADED_SKILLS] = []
            loaded = self.agent.data[DATA_NAME_LOADED_SKILLS]
            if skill.name in loaded:
                loaded.remove(skill.name)
            loaded.append(skill.name)
            self.agent.data[DATA_NAME_LOADED_SKILLS] = loaded[-max_loaded_skills():]
            return f"Loaded skill '{skill.name}' into EXTRAS."
        
        # Not found locally, offer to search marketplace
        return f"Error: skill '{skill_name}' not found locally.\n\nSearch marketplace: skills_tool method=search query='{skill_name}'\nOr create: skills_tool method=create skill_name='{skill_name}' description='...'"

    async def _install_from_marketplace(self, skill_name: str) -> str:
        """Download and install skill from skills.sh marketplace"""
        if not skill_name:
            return "Error: 'skill_name' is required. Format: 'owner/repo/skill' or 'owner/repo'"
        
        try:
            # Parse skill_name (format: owner/repo or owner/repo/skill)
            parts = skill_name.strip().split('/')
            if len(parts) < 2:
                return f"Error: Invalid format. Use 'owner/repo' or 'owner/repo/skill'"
            
            owner = parts[0]
            repo = parts[1]
            skill = parts[2] if len(parts) > 2 else None
            
            # Construct GitHub URL
            if skill:
                github_url = f"https://raw.githubusercontent.com/{owner}/{repo}/main/skills/{skill}/SKILL.md"
            else:
                github_url = f"https://raw.githubusercontent.com/{owner}/{repo}/main/SKILL.md"
            
            # Use browser_agent to fetch SKILL.md
            fetch_result = await self.agent.call_tool(
                "browser_agent",
                task=f"Download SKILL.md from {github_url}. Return complete file content.",
                url=github_url
            )
            
            if fetch_result and "---" in fetch_result:
                # Save to local skills directory
                skill_dir = Path(f"/a0/usr/skills/{skill or repo}")
                skill_dir.mkdir(parents=True, exist_ok=True)
                
                skill_file = skill_dir / "SKILL.md"
                skill_file.write_text(fetch_result)
                
                return f"✅ Installed skill '{skill or repo}' from marketplace.\n\nLoad with: skills_tool method=load skill_name='{skill or repo}'"
            else:
                return f"Error: Could not fetch SKILL.md from {github_url}. Skill may not exist."
                
        except Exception as e:
            return f"Error installing from marketplace: {e}"

    def _create_skill(self, skill_name: str, description: str) -> str:
        """Auto-create a new skill based on user requirements"""
        if not skill_name or not description:
            return "Error: Both 'skill_name' and 'description' are required for method=create."
        
        # Sanitize skill name
        skill_name = skill_name.lower().replace(' ', '-').replace('_', '-')
        
        # Create skill directory
        skill_dir = Path(f"/a0/usr/skills/{skill_name}")
        skill_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate SKILL.md template
        skill_content = f"""---
name: "{skill_name}"
description: "{description}"
version: "1.0.0"
author: "Agent Zero"
tags: ["custom", "auto-generated"]
trigger_patterns:
  - "{skill_name.replace('-', ' ')}"
---

# {skill_name.replace('-', ' ').title()}

## When to use this skill
{description}

## Instructions

### Step 1: Analyze the task
Understand what needs to be accomplished.

### Step 2: Execute
Perform the required actions.

### Step 3: Verify
Confirm the task was completed successfully.

## Examples

### Example 1: Basic usage
Describe a typical use case here.

## Best practices
1. Follow the instructions step-by-step
2. Verify results before finishing
3. Document any issues encountered

## References
- Add relevant documentation links here
"""
        
        # Write SKILL.md
        skill_file = skill_dir / "SKILL.md"
        skill_file.write_text(skill_content)
        
        return f"✅ Created new skill '{skill_name}' at {skill_dir}/SKILL.md\n\nNext steps:\n1. Edit the skill file to add detailed instructions\n2. Load with: skills_tool method=load skill_name='{skill_name}'\n3. Test and refine based on usage"


def max_loaded_skills() -> int:
    return 5
