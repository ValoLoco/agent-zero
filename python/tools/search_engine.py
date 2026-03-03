import os
import asyncio
from python.helpers import dotenv, memory, perplexity_search, duckduckgo_search
from python.helpers.tool import Tool, Response
from python.helpers.print_style import PrintStyle
from python.helpers.errors import handle_error
from python.helpers.searxng import search as searxng

SEARCH_ENGINE_RESULTS = 10


class SearchEngine(Tool):
    async def execute(self, query="", **kwargs):
        # Get search engine preference from environment (searxng or perplexity)
        search_engine = os.getenv("SEARCH_ENGINE", "searxng").lower()
        
        if search_engine == "perplexity":
            perplexity_result = await self.perplexity_search(query)
            await self.agent.handle_intervention(perplexity_result)
            return Response(message=perplexity_result, break_loop=False)
        else:
            # Default to SearXNG
            searxng_result = await self.searxng_search(query)
            await self.agent.handle_intervention(searxng_result)
            return Response(message=searxng_result, break_loop=False)

    async def perplexity_search(self, question):
        try:
            api_key = os.getenv("PERPLEXITY_API_KEY")
            if not api_key:
                return "Perplexity API key not found. Set PERPLEXITY_API_KEY environment variable."
            
            result = perplexity_search.perplexity_search(
                query=question,
                api_key=api_key
            )
            return self.format_result_perplexity(result, "Perplexity")
        except Exception as e:
            handle_error(e)
            return f"Perplexity search failed: {str(e)}"

    async def searxng_search(self, question):
        results = await searxng(question)
        return self.format_result_searxng(results, "Search Engine")

    def format_result_perplexity(self, result, source):
        if isinstance(result, Exception):
            handle_error(result)
            return f"{source} search failed: {str(result)}"
        return f"{source} Results:\n\n{result}"

    def format_result_searxng(self, result, source):
        if isinstance(result, Exception):
            handle_error(result)
            return f"{source} search failed: {str(result)}"

        outputs = []
        for item in result["results"]:
            outputs.append(f"{item['title']}\n{item['url']}\n{item['content']}")

        return "\n\n".join(outputs[:SEARCH_ENGINE_RESULTS]).strip()
