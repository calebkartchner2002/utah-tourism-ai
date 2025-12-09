"""
Utah Tourism AI - Main Application

AI-powered tourism recommendation system for Utah using Docker Model Runner
and MCP Gateway for intelligent travel suggestions.
"""

import os
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from .llm_client import LLMClient
from .mcp_client import MCPClient
from .utah_data import UTAH_DESTINATIONS, get_destinations_summary, get_weather_locations
from .database import DatabaseManager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Initialize clients
    app.state.llm_client = LLMClient()
    app.state.mcp_client = MCPClient()
    app.state.db = DatabaseManager()

    # Initialize database tables
    await app.state.db.init_db()

    logger.info("Utah Tourism AI initialized")
    logger.info(f"LLM API URL: {os.getenv('LLM_API_URL', 'not set')}")
    logger.info(f"MCP Gateway: {os.getenv('MCP_GATEWAY_ENDPOINT', 'not set')}")
    logger.info(f"Database: Connected")

    yield

    # Cleanup
    await app.state.llm_client.close()
    await app.state.mcp_client.close()
    await app.state.db.close()
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


async def _generate_recommendation_internal(
    request: Request,
    interests: str,
    duration: str,
    season: str,
    activity_level: str
) -> tuple[str, bool]:
    """
    Internal function to generate recommendations.
    Returns tuple of (recommendation_text, used_search).
    """
    llm_client: LLMClient = request.app.state.llm_client
    mcp_client: MCPClient = request.app.state.mcp_client

    # Use minimal static context - let web search provide fresh, dynamic info
    utah_context = get_destinations_summary()

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

    # Always search for fresh, dynamic information
    search_results = ""
    try:
        search_query = f"best {interests} in Utah {season} {duration} itinerary recommendations 2025"
        search_results = await mcp_client.search(search_query)
        logger.info(f"Search completed for: {search_query}")
    except Exception as e:
        logger.warning(f"Search failed (continuing without): {e}")

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

    # Save recommendation to database
    db: DatabaseManager = request.app.state.db
    saved_rec = await db.save_recommendation(
        interests=interests,
        duration=duration,
        season=season,
        activity_level=activity_level,
        recommendation_text=recommendation,
        used_search=bool(search_results)
    )
    logger.info(f"Saved recommendation to database with ID: {saved_rec.id}")

    return recommendation, bool(search_results)


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
    try:
        recommendation, used_search = await _generate_recommendation_internal(
            request, interests, duration, season, activity_level
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
                "used_search": used_search
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


@app.get("/history", response_class=HTMLResponse)
async def view_history(request: Request):
    """View all saved recommendations."""
    db: DatabaseManager = request.app.state.db
    try:
        recommendations = await db.get_all_recommendations(limit=50)
        return templates.TemplateResponse(
            "history.html",
            {
                "request": request,
                "recommendations": recommendations
            }
        )
    except Exception as e:
        logger.error(f"Error fetching recommendations: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch recommendations: {str(e)}"
        )


@app.get("/api/recommendations")
async def get_recommendations(request: Request, limit: int = 50):
    """Get all saved recommendations as JSON."""
    db: DatabaseManager = request.app.state.db
    try:
        recommendations = await db.get_all_recommendations(limit=limit)
        return {
            "recommendations": [
                {
                    "id": rec.id,
                    "interests": rec.interests,
                    "duration": rec.duration,
                    "season": rec.season,
                    "activity_level": rec.activity_level,
                    "recommendation_text": rec.recommendation_text,
                    "used_search": rec.used_search,
                    "created_at": rec.created_at.isoformat()
                }
                for rec in recommendations
            ],
            "count": len(recommendations)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/recommendations/{recommendation_id}")
async def get_recommendation_detail(request: Request, recommendation_id: int):
    """Get a specific recommendation by ID."""
    db: DatabaseManager = request.app.state.db
    try:
        rec = await db.get_recommendation_by_id(recommendation_id)
        if not rec:
            raise HTTPException(status_code=404, detail="Recommendation not found")

        return {
            "id": rec.id,
            "interests": rec.interests,
            "duration": rec.duration,
            "season": rec.season,
            "activity_level": rec.activity_level,
            "recommendation_text": rec.recommendation_text,
            "used_search": rec.used_search,
            "created_at": rec.created_at.isoformat()
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


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
    try:
        recommendation, used_search = await _generate_recommendation_internal(
            request, interests, duration, season, activity_level
        )

        return {
            "recommendation": recommendation,
            "parameters": {
                "interests": interests,
                "duration": duration,
                "season": season,
                "activity_level": activity_level
            },
            "enhanced_with_search": used_search
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
