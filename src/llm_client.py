"""
LLM Client for Docker Model Runner

Communicates with the local LLM via OpenAI-compatible API provided by
Docker Model Runner.
"""

import os
import logging

from openai import AsyncOpenAI

logger = logging.getLogger(__name__)


class LLMClient:
    """Client for interacting with the local LLM via Docker Model Runner."""
    
    def __init__(self):
        # Docker Model Runner provides OpenAI-compatible API
        self.base_url = os.getenv("OPENAI_BASE_URL", os.getenv("LLM_API_URL", ""))
        self.model_name = os.getenv("OPENAI_MODEL_NAME", os.getenv("LLM_MODEL_NAME", "ai/llama3.2"))
        self.api_key = os.getenv("OPENAI_API_KEY", "local-model-runner")
        
        # Initialize OpenAI client pointing to Docker Model Runner
        self.client = AsyncOpenAI(
            base_url=self.base_url,
            api_key=self.api_key,
            timeout=120.0,  # LLM responses can take time
        )
        
        logger.info(f"LLM Client initialized - URL: {self.base_url}, Model: {self.model_name}")
    
    async def close(self):
        """Close the client."""
        await self.client.close()
    
    async def generate_recommendation(
        self,
        interests: str,
        duration: str,
        season: str,
        activity_level: str,
        utah_context: str,
        search_results: str = ""
    ) -> str:
        """
        Generate a personalized Utah travel recommendation.
        
        Args:
            interests: User's travel interests (hiking, photography, etc.)
            duration: Trip duration
            season: Preferred travel season
            activity_level: Physical activity preference
            utah_context: Pre-loaded Utah destination information
            search_results: Optional real-time search results
            
        Returns:
            Formatted travel recommendation
        """
        
        # Build the system prompt
        system_prompt = """You are an expert Utah travel guide with deep knowledge of:
- Utah's "Mighty Five" national parks (Zion, Bryce Canyon, Arches, Canyonlands, Capitol Reef)
- State parks and monuments
- Scenic byways and road trips
- Outdoor activities (hiking, skiing, mountain biking, rock climbing)
- Cultural attractions and local cuisine
- Best times to visit different areas
- Practical travel tips

Your recommendations should be:
1. Personalized to the user's interests and activity level
2. Realistic given the trip duration
3. Seasonally appropriate
4. Include specific locations, trails, or attractions
5. Provide practical tips (best times, what to bring, etc.)

Format your response with clear sections using markdown:
- **Recommended Destinations**
- **Suggested Itinerary**
- **Pro Tips**
- **What to Pack**
- **Current Weather** (if weather data is provided - place this at the end)"""

        # Build the user prompt
        user_message = f"""Please create a personalized Utah travel recommendation based on:

**Traveler Preferences:**
- Interests: {interests}
- Trip Duration: {duration}
- Preferred Season: {season}
- Activity Level: {activity_level}

**Utah Destination Information:**
{utah_context}
"""
        
        # Add search results if available
        if search_results:
            user_message += f"""
**Current Travel Information:**
{search_results}
"""

        user_message += """
Please provide a detailed, personalized travel recommendation that matches these preferences.

IMPORTANT: If weather information is provided above, you MUST include it in a dedicated **Current Weather** section at the END of your response (after What to Pack).

Format the weather in a clean, human-readable way:
- Convert temperatures from Celsius to Fahrenheit (formula: F = C × 9/5 + 32)
- Convert Unix timestamps to readable times (e.g., "sunrise at 7:15 AM")
- Use natural language (e.g., "Currently 25°F with clear skies" instead of "Now: -3.89 metric")
- Only include relevant details: conditions, temperature, feels like, and wind if significant"""

        try:
            # Call the LLM via Docker Model Runner's OpenAI-compatible API
            response = await self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message}
                ],
                temperature=0.7,
                max_tokens=2000,
            )
            
            recommendation = response.choices[0].message.content
            logger.info(f"Generated recommendation ({len(recommendation)} chars)")
            return recommendation
            
        except Exception as e:
            logger.error(f"LLM generation failed: {e}")
            # Return a helpful fallback response
            return self._get_fallback_recommendation(interests, duration, season)
    
    def _get_fallback_recommendation(
        self,
        interests: str,
        duration: str,
        season: str
    ) -> str:
        """Provide a fallback recommendation if LLM is unavailable."""
        return f"""## Utah Travel Recommendation

*Note: AI-generated recommendation temporarily unavailable. Here's a general guide:*

### Based on Your Interests: {interests}

**The Mighty Five National Parks** are Utah's crown jewels:

1. **Zion National Park** - Stunning red cliffs, famous Angels Landing hike
2. **Bryce Canyon** - Otherworldly hoodoo formations
3. **Arches National Park** - Over 2,000 natural stone arches
4. **Canyonlands** - Vast wilderness, incredible viewpoints
5. **Capitol Reef** - Less crowded, scenic drives

### For a {duration} Trip in {season}:

Consider focusing on 2-3 parks to avoid rushing. The parks in southern Utah 
(Zion, Bryce, Capitol Reef) can be combined, while Arches and Canyonlands 
are near Moab.

### Pro Tips:
- Book accommodations early, especially for popular parks
- Start hikes early to avoid crowds and heat
- Carry plenty of water - Utah is desert country
- Check road conditions in winter months

Visit utah.com for current conditions and detailed planning resources.
"""
    
    async def chat(self, message: str, history: list = None) -> str:
        """
        Simple chat interface for follow-up questions.
        
        Args:
            message: User message
            history: Optional conversation history
            
        Returns:
            Assistant response
        """
        messages = [
            {
                "role": "system",
                "content": "You are a helpful Utah travel assistant. Answer questions about Utah tourism, attractions, and travel planning."
            }
        ]
        
        if history:
            messages.extend(history)
        
        messages.append({"role": "user", "content": message})
        
        try:
            response = await self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                temperature=0.7,
                max_tokens=1000,
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"Chat failed: {e}")
            return "I apologize, but I'm having trouble responding right now. Please try again."
