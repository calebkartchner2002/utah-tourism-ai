"""
Utah Tourism AI - Main Application

AI-powered tourism recommendation system for Utah using Docker Model Runner
and MCP Gateway for intelligent travel suggestions.
"""

import os
import json
import logging
from typing import Optional
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from .llm_client import LLMClient
from .mcp_client import MCPClient
from .utah_data import UTAH_DESTINATIONS, get_destinations_context, get_weather_locations

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Initialize clients
    app.state.llm_client = LLMClient()
    app.state.mcp_client = MCPClient()
    
    logger.info("Utah Tourism AI initialized")
    logger.info(f"LLM API URL: {os.getenv('LLM_API_URL', 'not set')}")
    logger.info(f"MCP Gateway: {os.getenv('MCP_GATEWAY_ENDPOINT', 'not set')}")
    
    yield
    
    # Cleanup
    await app.state.llm_client.close()
    await app.state.mcp_client.close()
    logger.info("Utah Tourism AI shutdown complete")


app = FastAPI(
    title="Utah Tourism AI",
    description="Get personalized travel recommendations for Utah powered by local AI",
    version="1.0.0",
    lifespan=lifespan
)

# Mount static files and templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Render the main page."""
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "destinations": UTAH_DESTINATIONS
        }
    )


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "utah-tourism-ai"}


@app.get("/api/tools")
async def list_tools(request: Request):
    """List available MCP tools for debugging."""
    mcp_client: MCPClient = request.app.state.mcp_client
    try:
        tools = await mcp_client.list_available_tools()
        return {"tools": tools}
    except Exception as e:
        return {"error": str(e), "tools": []}


@app.post("/recommend", response_class=HTMLResponse)
async def get_recommendation(
    request: Request,
    interests: str = Form(...),
    duration: str = Form(default="3-5 days"),
    season: str = Form(default="any"),
    activity_level: str = Form(default="moderate"),
    include_search: bool = Form(default=True)
):
    """
    Generate personalized Utah travel recommendations.
    
    Uses the local LLM via Docker Model Runner and optionally
    enhances with real-time data via MCP Gateway tools.
    """
    llm_client: LLMClient = request.app.state.llm_client
    mcp_client: MCPClient = request.app.state.mcp_client
    
    try:
        # Build context from Utah destination data
        utah_context = get_destinations_context()

        # Fetch current weather for relevant locations
        weather_info = ""
        try:
            weather_locations = get_weather_locations(interests, season)
            logger.info(f"Fetching weather for: {weather_locations}")

            weather_results = []
            for location in weather_locations:
                weather_data = await mcp_client.get_weather(location)
                if weather_data:
                    weather_results.append(f"**{location}**: {weather_data}")

            if weather_results:
                weather_info = "\n".join(weather_results)
                logger.info(f"Weather fetched for {len(weather_results)} locations")
        except Exception as e:
            logger.warning(f"Weather fetch failed (continuing without): {e}")
            weather_info = ""

        # Optionally search for current information
        search_results = ""
        if include_search:
            try:
                search_query = f"Utah tourism {interests} {season} travel tips"
                search_results = await mcp_client.search(search_query)
                logger.info(f"Search completed for: {search_query}")
            except Exception as e:
                logger.warning(f"Search failed (continuing without): {e}")
                search_results = ""

        # Combine weather and search results
        additional_context = ""
        if weather_info:
            additional_context += f"\n**Current Weather Conditions:**\n{weather_info}\n"
        if search_results:
            additional_context += f"\n**Travel Tips from Web:**\n{search_results}"

        # Close MCP session before LLM generation to avoid timeout
        await mcp_client.close()

        # Generate recommendation using LLM
        recommendation = await llm_client.generate_recommendation(
            interests=interests,
            duration=duration,
            season=season,
            activity_level=activity_level,
            utah_context=utah_context,
            search_results=additional_context
        )
        
        return templates.TemplateResponse(
            "recommendation.html",
            {
                "request": request,
                "recommendation": recommendation,
                "interests": interests,
                "duration": duration,
                "season": season,
                "activity_level": activity_level,
                "used_search": bool(search_results)
            }
        )
        
    except Exception as e:
        logger.error(f"Error generating recommendation: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate recommendation: {str(e)}"
        )


@app.get("/api/destinations")
async def list_destinations():
    """API endpoint to list all Utah destinations."""
    return {"destinations": UTAH_DESTINATIONS}


@app.post("/api/recommend")
async def api_recommend(
    request: Request,
    interests: str = Form(...),
    duration: str = Form(default="3-5 days"),
    season: str = Form(default="any"),
    activity_level: str = Form(default="moderate"),
    include_search: bool = Form(default=True)
):
    """JSON API endpoint for recommendations."""
    llm_client: LLMClient = request.app.state.llm_client
    mcp_client: MCPClient = request.app.state.mcp_client

    try:
        utah_context = get_destinations_context()

        # Fetch weather
        weather_info = ""
        try:
            weather_locations = get_weather_locations(interests, season)
            weather_results = []
            for location in weather_locations:
                weather_data = await mcp_client.get_weather(location)
                if weather_data:
                    weather_results.append(f"**{location}**: {weather_data}")
            if weather_results:
                weather_info = "\n".join(weather_results)
        except Exception:
            pass

        search_results = ""
        if include_search:
            try:
                search_query = f"Utah tourism {interests} {season}"
                search_results = await mcp_client.search(search_query)
            except Exception:
                pass

        # Combine weather and search
        additional_context = ""
        if weather_info:
            additional_context += f"\n**Current Weather:**\n{weather_info}\n"
        if search_results:
            additional_context += f"\n**Travel Tips:**\n{search_results}"

        # Close MCP session before LLM generation to avoid timeout
        await mcp_client.close()

        recommendation = await llm_client.generate_recommendation(
            interests=interests,
            duration=duration,
            season=season,
            activity_level=activity_level,
            utah_context=utah_context,
            search_results=additional_context
        )
        
        return {
            "recommendation": recommendation,
            "parameters": {
                "interests": interests,
                "duration": duration,
                "season": season,
                "activity_level": activity_level
            },
            "enhanced_with_search": bool(search_results)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
