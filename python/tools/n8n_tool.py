import os
import requests
from python.helpers.tool import Tool, Response

class N8nTool(Tool):
    """
    Create and manage n8n workflows programmatically.
    Agents can build automation workflows on-demand.
    """

    async def execute(self, **kwargs):
        action = kwargs.get("action")
        n8n_url = os.getenv("N8N_URL", "http://n8n:5678")
        api_key = os.getenv("N8N_API_KEY", "")
        
        headers = {"X-N8N-API-KEY": api_key} if api_key else {}
        
        if action == "create_workflow":
            workflow_json = kwargs.get("workflow")
            response = requests.post(
                f"{n8n_url}/api/v1/workflows",
                json=workflow_json,
                headers=headers
            )
            return Response(
                message=f"Workflow created: {response.json().get('id')}",
                break_loop=False
            )
        
        elif action == "list_workflows":
            response = requests.get(
                f"{n8n_url}/api/v1/workflows",
                headers=headers
            )
            workflows = response.json().get("data", [])
            return Response(
                message=f"Found {len(workflows)} workflows",
                break_loop=False
            )
        
        elif action == "execute_workflow":
            workflow_id = kwargs.get("workflow_id")
            response = requests.post(
                f"{n8n_url}/api/v1/workflows/{workflow_id}/execute",
                headers=headers
            )
            return Response(
                message=f"Workflow executed: {response.json()}",
                break_loop=False
            )
