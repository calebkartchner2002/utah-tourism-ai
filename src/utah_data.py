"""
Utah Tourism Data

Comprehensive information about Utah destinations to provide context
for the LLM recommendations.
"""

UTAH_DESTINATIONS = {
    "national_parks": {
        "zion": {
            "name": "Zion National Park",
            "location": "Springdale, Southern Utah",
            "highlights": [
                "Angels Landing - Iconic chain-assisted climb with stunning views",
                "The Narrows - Hiking through the Virgin River canyon",
                "Observation Point - 8-mile round trip with panoramic views",
                "Emerald Pools - Family-friendly waterfall hikes",
                "Canyon Overlook Trail - Short hike with big rewards"
            ],
            "best_season": "Spring (March-May) and Fall (September-November)",
            "activity_level": "Moderate to Strenuous",
            "tips": [
                "Shuttle system required in peak season",
                "Angels Landing requires permits - book in advance",
                "The Narrows requires special gear - rent in Springdale",
                "Start hikes early to avoid crowds and heat"
            ]
        },
        "bryce_canyon": {
            "name": "Bryce Canyon National Park",
            "location": "Bryce Canyon City, Southern Utah",
            "highlights": [
                "Sunrise/Sunset Point - Spectacular hoodoo views",
                "Navajo Loop Trail - Descend among the hoodoos",
                "Queens Garden Trail - Gentle introduction to the canyon",
                "Rim Trail - Easy walk connecting viewpoints",
                "Stargazing - One of the darkest skies in North America"
            ],
            "best_season": "May-September (snow possible in winter)",
            "activity_level": "Easy to Moderate",
            "tips": [
                "Elevation 8,000+ feet - acclimate before strenuous hikes",
                "Combine with Zion for a complete southern Utah trip",
                "Winter brings beautiful snow-covered hoodoos",
                "Night sky programs offered by rangers"
            ]
        },
        "arches": {
            "name": "Arches National Park",
            "location": "Moab, Eastern Utah",
            "highlights": [
                "Delicate Arch - Utah's iconic symbol, best at sunset",
                "Landscape Arch - One of the world's longest natural arches",
                "Devils Garden - Multiple arches on one trail",
                "The Windows Section - Easy access to impressive arches",
                "Fiery Furnace - Ranger-guided exploration required"
            ],
            "best_season": "Spring and Fall (summer extremely hot)",
            "activity_level": "Easy to Moderate",
            "tips": [
                "Timed entry reservation required April-October",
                "Delicate Arch hike has no shade - bring water",
                "Sunset at Delicate Arch is magical but crowded",
                "Combine with Canyonlands, only 30 minutes away"
            ]
        },
        "canyonlands": {
            "name": "Canyonlands National Park",
            "location": "Moab, Eastern Utah",
            "highlights": [
                "Island in the Sky - Most accessible district with grand views",
                "Mesa Arch - Famous sunrise photography spot",
                "Grand View Point - See for 100 miles",
                "The Needles - Colorful spires and backcountry hiking",
                "White Rim Road - Epic 4x4 adventure"
            ],
            "best_season": "Spring and Fall",
            "activity_level": "Easy to Very Strenuous",
            "tips": [
                "Three separate districts - Island in the Sky most popular",
                "Backcountry permits required for overnight camping",
                "4x4 required for many remote areas",
                "Much less crowded than Arches"
            ]
        },
        "capitol_reef": {
            "name": "Capitol Reef National Park",
            "location": "Torrey, South-Central Utah",
            "highlights": [
                "Scenic Drive - 8-mile paved road through the park",
                "Hickman Bridge - Natural bridge hike",
                "Capitol Gorge - Petroglyphs and pioneer history",
                "Fruita Historic District - Pick your own fruit in season",
                "Cathedral Valley - Remote 4x4 area"
            ],
            "best_season": "Year-round (hot summers)",
            "activity_level": "Easy to Moderate",
            "tips": [
                "Least crowded of the Mighty Five",
                "Free fruit picking in Fruita orchards (in season)",
                "Scenic Byway 12 connects to Bryce Canyon",
                "Great for a quieter national park experience"
            ]
        }
    },
    "state_parks": {
        "dead_horse_point": {
            "name": "Dead Horse Point State Park",
            "location": "Near Moab",
            "highlights": ["Spectacular Colorado River views", "Less crowded than nearby Arches"],
            "best_season": "Year-round",
            "activity_level": "Easy"
        },
        "goblin_valley": {
            "name": "Goblin Valley State Park",
            "location": "Hanksville area",
            "highlights": ["Unique mushroom-shaped rock formations", "Explore freely among the goblins"],
            "best_season": "Spring and Fall",
            "activity_level": "Easy"
        },
        "snow_canyon": {
            "name": "Snow Canyon State Park",
            "location": "Near St. George",
            "highlights": ["Red and white sandstone", "Lava tubes and caves"],
            "best_season": "Year-round (mild winters)",
            "activity_level": "Easy to Moderate"
        },
        "kodachrome_basin": {
            "name": "Kodachrome Basin State Park",
            "location": "Near Bryce Canyon",
            "highlights": ["Colorful sedimentary pipes", "Less crowded alternative to Bryce"],
            "best_season": "Spring and Fall",
            "activity_level": "Easy to Moderate"
        }
    },
    "monuments": {
        "grand_staircase": {
            "name": "Grand Staircase-Escalante National Monument",
            "location": "Southern Utah",
            "highlights": [
                "Slot canyons (Zebra, Spooky, Peek-a-boo)",
                "Calf Creek Falls",
                "Devils Garden",
                "Vast wilderness backcountry"
            ],
            "best_season": "Spring and Fall",
            "activity_level": "Moderate to Strenuous"
        },
        "bears_ears": {
            "name": "Bears Ears National Monument",
            "location": "Southeastern Utah",
            "highlights": ["Ancient cliff dwellings", "Native American cultural sites", "Remote wilderness"],
            "best_season": "Spring and Fall",
            "activity_level": "Moderate"
        },
        "natural_bridges": {
            "name": "Natural Bridges National Monument",
            "location": "Southeastern Utah",
            "highlights": ["Three natural bridges", "Dark sky preserve", "Less crowded"],
            "best_season": "Year-round",
            "activity_level": "Easy to Moderate"
        }
    },
    "cities_towns": {
        "moab": {
            "name": "Moab",
            "highlights": ["Gateway to Arches and Canyonlands", "Mountain biking mecca", "Colorado River activities"],
            "activities": ["Mountain biking", "River rafting", "Off-roading", "Rock climbing"]
        },
        "salt_lake_city": {
            "name": "Salt Lake City",
            "highlights": ["Temple Square", "Great Salt Lake", "Ski resorts nearby", "Vibrant food scene"],
            "activities": ["Skiing", "City exploration", "Hiking in the Wasatch"]
        },
        "park_city": {
            "name": "Park City",
            "highlights": ["World-class skiing", "Historic Main Street", "Sundance Film Festival"],
            "activities": ["Skiing", "Mountain biking", "Golf", "Festivals"]
        },
        "st_george": {
            "name": "St. George",
            "highlights": ["Gateway to Zion", "Warm winters", "Golf destination"],
            "activities": ["Golf", "Hiking", "Mountain biking"]
        },
        "springdale": {
            "name": "Springdale",
            "highlights": ["Gateway town to Zion", "Charming shops and restaurants"],
            "activities": ["Dining", "Shopping", "Zion access"]
        }
    },
    "scenic_byways": {
        "highway_12": {
            "name": "Scenic Byway 12",
            "description": "124 miles connecting Bryce Canyon to Capitol Reef",
            "highlights": ["Voted one of America's most scenic drives", "Boulder Mountain views", "Escalante access"]
        },
        "highway_128": {
            "name": "Highway 128 (Colorado River Scenic Byway)",
            "description": "44 miles along the Colorado River from Moab to I-70",
            "highlights": ["River views", "Fisher Towers", "Castle Valley"]
        },
        "mirror_lake": {
            "name": "Mirror Lake Scenic Byway",
            "description": "High Uinta Mountains route",
            "highlights": ["Alpine lakes", "Mountain scenery", "Summer only"]
        }
    },
    "skiing": {
        "park_city": {
            "name": "Park City Mountain Resort",
            "highlights": ["Largest ski resort in US", "Connected to Canyons Village"],
            "best_season": "December-April"
        },
        "deer_valley": {
            "name": "Deer Valley Resort",
            "highlights": ["Ski-only (no snowboards)", "Luxury experience", "Limited tickets"],
            "best_season": "December-April"
        },
        "snowbird": {
            "name": "Snowbird",
            "highlights": ["Deep powder", "Challenging terrain", "Long season"],
            "best_season": "November-May"
        },
        "alta": {
            "name": "Alta Ski Area",
            "highlights": ["Ski-only resort", "Incredible snow", "Classic ski experience"],
            "best_season": "November-April"
        },
        "brighton": {
            "name": "Brighton Resort",
            "highlights": ["Night skiing", "Family-friendly", "Affordable"],
            "best_season": "November-April"
        }
    }
}


def get_weather_locations(interests: str, season: str) -> list[str]:
    """
    Determine which Utah cities to fetch weather for based on interests and season.

    Args:
        interests: User's travel interests
        season: Preferred season

    Returns:
        List of city names for weather lookup (max 3 unique locations)
    """
    interests_lower = interests.lower()
    season_lower = season.lower()
    locations = []

    # Skiing/winter sports locations
    if any(word in interests_lower for word in ["ski", "snow", "winter sports"]) or season_lower == "winter":
        locations.extend(["Park City, Utah", "Salt Lake City, Utah"])

    # Moab area (Arches, Canyonlands)
    if any(word in interests_lower for word in ["arches", "canyonlands", "moab", "mountain bike", "4x4", "off-road"]):
        locations.append("Moab, Utah")

    # Zion area
    if any(word in interests_lower for word in ["zion", "angel", "narrows", "springdale"]):
        locations.append("Springdale, Utah")

    # Bryce Canyon area
    if any(word in interests_lower for word in ["bryce", "hoodoo"]):
        locations.append("Bryce Canyon City, Utah")

    # General southern Utah parks/hiking
    if any(word in interests_lower for word in ["hiking", "photography", "nature", "canyon", "national park", "desert"]):
        if "Moab, Utah" not in locations:
            locations.append("Moab, Utah")
        if "Springdale, Utah" not in locations:
            locations.append("Springdale, Utah")

    # St. George area (warm weather destination)
    if any(word in interests_lower for word in ["golf", "warm", "st. george", "st george", "snow canyon"]):
        locations.append("St. George, Utah")

    # Default to Salt Lake City if no specific match
    if not locations:
        locations.append("Salt Lake City, Utah")

    # Return unique locations (max 3)
    return list(dict.fromkeys(locations))[:3]


def get_destinations_summary() -> str:
    """
    Generate a lightweight summary of Utah destinations.
    Provides just enough context without overwhelming the LLM.
    Web search will provide detailed, up-to-date information.
    
    Returns:
        Brief formatted string with Utah highlights
    """
    return """Utah's "Mighty Five" National Parks: Zion, Bryce Canyon, Arches, Canyonlands, Capitol Reef
Major Ski Resorts: Park City Mountain, Deer Valley, Alta, Snowbird, Brighton
Popular Activities: Hiking, skiing, mountain biking, rock climbing, photography
Major Cities: Salt Lake City (gateway), Park City (ski town), Moab (adventure hub)"""
