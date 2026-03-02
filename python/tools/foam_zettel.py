import os
import random
from datetime import datetime
from python.helpers.tool import Tool, Response

class FoamZettelTool(Tool):
    """
    Create and manage Zettelkasten notes in Foam vault.
    Agents can create atomic notes with proper linking.
    """

    async def execute(self, **kwargs):
        action = kwargs.get("action")
        foam_path = "/app/foam"
        
        if action == "create_zettel":
            title = kwargs.get("title")
            content = kwargs.get("content")
            tags = kwargs.get("tags", [])
            links = kwargs.get("links", [])
            
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            rand_id = random.randint(1000, 9999)
            note_id = f"{timestamp}-{rand_id}"
            
            filename = f"{title.lower().replace(' ', '-')}.md"
            filepath = os.path.join(foam_path, "zettelkasten/permanent", filename)
            
            note_content = f"""---
id: {note_id}
type: permanent
tags: {tags}
created: {datetime.now().isoformat()}
---

# {title}

{content}

## Connections

{chr(10).join([f'- [[{link}]]' for link in links])}
"""
            
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            with open(filepath, 'w') as f:
                f.write(note_content)
            
            return Response(
                message=f"Created Zettel: {filename}",
                break_loop=False
            )
        
        elif action == "search_notes":
            query = kwargs.get("query")
            import subprocess
            result = subprocess.run(
                ["grep", "-r", "-i", query, foam_path],
                capture_output=True,
                text=True
            )
            return Response(
                message=f"Search results:\n{result.stdout}",
                break_loop=False
            )
        
        elif action == "create_daily":
            date = datetime.now().strftime("%Y-%m-%d")
            filepath = os.path.join(foam_path, "journals", f"{date}.md")
            
            if os.path.exists(filepath):
                return Response(message=f"Daily note already exists: {date}", break_loop=False)
            
            content = f"""---
type: daily-note
date: {date}
---

# {date}

## Tasks

- [ ] 

## Captures

## Zettelkasten

## PARA Updates
"""
            
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            with open(filepath, 'w') as f:
                f.write(content)
            
            return Response(
                message=f"Created daily note: {date}",
                break_loop=False
            )
