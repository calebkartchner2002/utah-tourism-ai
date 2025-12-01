"""
MCP Client for Docker MCP Gateway

Communicates with the MCP Gateway to access tools like web search
for enhanced travel recommendations.
"""

import os
import json
import logging
from typing import Optional, Any

import httpx
from httpx_sse import aconnect_sse

logger = logging.getLogger(__name__)


class MCPClient:
    """Client for interacting with Docker MCP Gateway."""
    
    def __init__(self):
        self.gateway_url = os.getenv(
            "MCP_GATEWAY_ENDPOINT",
            "http://mcp-gateway:8811/sse"
        )
        self.http_client = httpx.AsyncClient(timeout=30.0)
        
        logger.info(f"MCP Client initialized - Gateway: {self.gateway_url}")
    
    async def close(self):
        """Close the HTTP client."""
        await self.http_client.aclose()
    
    async def search(self, query: str) -> str:
        """
        Search for information using DuckDuckGo via MCP Gateway.
        
        Args:
            query: Search query string
            
        Returns:
            Formatted search results
        """
        try:
            # Call the DuckDuckGo search tool via MCP Gateway
            result = await self._call_tool(
                tool_name="duckduckgo_search",
                arguments={"query": query, "max_results": 5}
            )
            
            if result:
                return self._format_search_results(result)
            return ""
            
        except Exception as e:
            logger.error(f"Search failed: {e}")
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
            result = await self._call_tool(
                tool_name="fetch",
                arguments={"url": url}
            )
            return result if result else ""
        except Exception as e:
            logger.error(f"Fetch failed: {e}")
            return ""
    
    async def _call_tool(
        self,
        tool_name: str,
        arguments: dict[str, Any]
    ) -> Optional[str]:
        """
        Call an MCP tool via the gateway.
        
        Args:
            tool_name: Name of the MCP tool
            arguments: Tool arguments
            
        Returns:
            Tool response or None
        """
        # Parse gateway URL for base endpoint
        base_url = self.gateway_url.replace("/sse", "")
        
        # MCP Gateway tool call endpoint
        tool_endpoint = f"{base_url}/tools/{tool_name}/call"
        
        try:
            response = await self.http_client.post(
                tool_endpoint,
                json={"arguments": arguments},
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                # Extract content from MCP response
                if "content" in data:
                    contents = data["content"]
                    if isinstance(contents, list):
                        return "\n".join(
                            c.get("text", "") 
                            for c in contents 
                            if c.get("type") == "text"
                        )
                    return str(contents)
                return str(data)
            else:
                logger.warning(
                    f"Tool call failed: {response.status_code} - {response.text}"
                )
                return None
                
        except httpx.HTTPError as e:
            logger.error(f"HTTP error calling tool {tool_name}: {e}")
            return None
        except Exception as e:
            logger.error(f"Error calling tool {tool_name}: {e}")
            return None
    
    async def _call_tool_sse(
        self,
        tool_name: str,
        arguments: dict[str, Any]
    ) -> Optional[str]:
        """
        Call an MCP tool via SSE (Server-Sent Events).
        
        Alternative method using SSE transport.
        """
        try:
            request_body = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "tools/call",
                "params": {
                    "name": tool_name,
                    "arguments": arguments
                }
            }
            
            async with aconnect_sse(
                self.http_client,
                "POST",
                self.gateway_url,
                json=request_body
            ) as event_source:
                async for event in event_source.aiter_sse():
                    if event.data:
                        try:
                            data = json.loads(event.data)
                            if "result" in data:
                                return self._extract_result(data["result"])
                        except json.JSONDecodeError:
                            continue
                            
            return None
            
        except Exception as e:
            logger.error(f"SSE tool call failed: {e}")
            return None
    
    def _extract_result(self, result: Any) -> str:
        """Extract text content from MCP result."""
        if isinstance(result, dict):
            if "content" in result:
                contents = result["content"]
                if isinstance(contents, list):
                    return "\n".join(
                        c.get("text", "") 
                        for c in contents 
                        if isinstance(c, dict) and c.get("type") == "text"
                    )
            return json.dumps(result, indent=2)
        return str(result)
    
    def _format_search_results(self, results: str) -> str:
        """Format search results for the LLM context."""
        try:
            # Try to parse as JSON
            data = json.loads(results) if isinstance(results, str) else results
            
            if isinstance(data, list):
                formatted = []
                for item in data[:5]:  # Limit to 5 results
                    if isinstance(item, dict):
                        title = item.get("title", "")
                        snippet = item.get("snippet", item.get("description", ""))
                        url = item.get("url", item.get("link", ""))
                        formatted.append(f"- **{title}**: {snippet}")
                return "\n".join(formatted)
            
            return results
            
        except (json.JSONDecodeError, TypeError):
            # Return as-is if not JSON
            return results[:2000] if len(results) > 2000 else results
    
    async def list_available_tools(self) -> list[dict]:
        """List available tools from the MCP Gateway."""
        base_url = self.gateway_url.replace("/sse", "")
        
        try:
            response = await self.http_client.get(f"{base_url}/tools")
            if response.status_code == 200:
                data = response.json()
                return data.get("tools", [])
            return []
        except Exception as e:
            logger.error(f"Failed to list tools: {e}")
            return []
