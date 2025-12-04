"""
MCP Client for Docker MCP Gateway

Communicates with the MCP Gateway to access tools like web search
for enhanced travel recommendations.
"""

import os
import json
import logging
from typing import Optional

import httpx
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from mcp.client.sse import sse_client

logger = logging.getLogger(__name__)


class MCPClient:
    """Client for interacting with Docker MCP Gateway."""

    def __init__(self):
        self.gateway_url = os.getenv(
            "MCP_GATEWAY_ENDPOINT",
            "http://mcp-gateway:8811/sse"
        )
        self.session: Optional[ClientSession] = None
        self._client_context = None

        logger.info(f"MCP Client initialized - Gateway: {self.gateway_url}")

    async def _ensure_connected(self):
        """Ensure MCP client session is established."""
        if self.session is not None:
            return

        try:
            logger.info(f"Connecting to MCP Gateway at {self.gateway_url}")

            # Use SSE client for HTTP transport
            self._client_context = sse_client(self.gateway_url)
            read, write = await self._client_context.__aenter__()

            self.session = ClientSession(read, write)
            await self.session.__aenter__()

            # Initialize the session
            await self.session.initialize()

            logger.info("MCP session established successfully")

        except Exception as e:
            logger.error(f"Failed to connect to MCP Gateway: {e}", exc_info=True)
            self.session = None
            raise

    async def close(self):
        """Close the MCP session."""
        if self.session:
            try:
                await self.session.__aexit__(None, None, None)
            except Exception as e:
                logger.warning(f"Error closing session: {e}")
            self.session = None

        if self._client_context:
            try:
                await self._client_context.__aexit__(None, None, None)
            except Exception as e:
                logger.warning(f"Error closing client context: {e}")
            self._client_context = None

    async def search(self, query: str) -> str:
        """
        Search for information using DuckDuckGo via MCP Gateway.

        Args:
            query: Search query string

        Returns:
            Formatted search results
        """
        try:
            await self._ensure_connected()

            if not self.session:
                logger.warning("No MCP session available")
                return ""

            # Call the search tool
            logger.info(f"Calling search tool with query: {query}")
            result = await self.session.call_tool(
                "search",
                arguments={"query": query, "max_results": 5}
            )

            logger.info(f"Search tool returned: {type(result)}")

            # Extract and format results
            if hasattr(result, 'content') and result.content:
                formatted = self._format_search_results(result.content)
                logger.info(f"Formatted {len(formatted)} chars of search results")
                return formatted

            return ""

        except Exception as e:
            logger.error(f"Search failed: {e}", exc_info=True)
            return ""

    async def fetch_url(self, url: str) -> str:
        """
        Fetch content from a URL via MCP Gateway.

        Args:
            url: URL to fetch

        Returns:
            Page content
        """
        try:
            await self._ensure_connected()

            if not self.session:
                logger.warning("No MCP session available")
                return ""

            result = await self.session.call_tool(
                "fetch",
                arguments={"url": url}
            )

            if hasattr(result, 'content') and result.content:
                return self._extract_text_content(result.content)

            return ""

        except Exception as e:
            logger.error(f"Fetch failed: {e}")
            return ""

    def _extract_text_content(self, content) -> str:
        """Extract text from MCP content."""
        if isinstance(content, list):
            texts = []
            for item in content:
                if hasattr(item, 'text'):
                    texts.append(item.text)
                elif isinstance(item, dict) and 'text' in item:
                    texts.append(item['text'])
            return "\n".join(texts)
        elif hasattr(content, 'text'):
            return content.text
        elif isinstance(content, str):
            return content
        return str(content)

    def _format_search_results(self, content) -> str:
        """Format search results for the LLM context."""
        try:
            text = self._extract_text_content(content)

            # Try to parse as JSON if it looks like JSON
            if text.strip().startswith('[') or text.strip().startswith('{'):
                try:
                    data = json.loads(text)

                    if isinstance(data, list):
                        formatted = []
                        for item in data[:5]:  # Limit to 5 results
                            if isinstance(item, dict):
                                title = item.get("title", "")
                                snippet = item.get("snippet", item.get("description", ""))
                                formatted.append(f"- **{title}**: {snippet}")
                        return "\n".join(formatted)
                except json.JSONDecodeError:
                    pass

            # Return text as-is if not JSON
            return text[:2000] if len(text) > 2000 else text

        except Exception as e:
            logger.error(f"Error formatting results: {e}")
            return str(content)[:2000]

    async def list_available_tools(self) -> list[dict]:
        """List available tools from the MCP Gateway."""
        try:
            await self._ensure_connected()

            if not self.session:
                return []

            tools = await self.session.list_tools()
            return [{"name": tool.name, "description": tool.description} for tool in tools.tools]

        except Exception as e:
            logger.error(f"Failed to list tools: {e}")
            return []
