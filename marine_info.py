import trafilatura
import streamlit as st
from datetime import datetime
import pytz

@st.cache_data(ttl=3600)  # Cache for 1 hour
def get_marine_weather_text(location="puget_sound"):
    """
    Get marine weather information from NOAA marine forecasts.
    Uses web scraping to get the latest text-based forecasts.
    
    Args:
        location: The location to get forecast for (e.g., 'puget_sound')
        
    Returns:
        Dictionary with marine forecast sections
    """
    try:
        # Get the current time in Pacific timezone
        pacific_tz = pytz.timezone('US/Pacific')
        current_time = datetime.now(pacific_tz).strftime('%H:%M %Z')
        
        # NOAA Marine Forecasts URL for Puget Sound
        url = "https://marine.weather.gov/MapClick.php?zoneid=PZZ131"
        
        # Fetch and extract text from the URL
        downloaded = trafilatura.fetch_url(url)
        if not downloaded:
            print(f"Failed to download content from {url}")
            return {
                "status": "error",
                "error": "Failed to download marine forecast",
                "updated": current_time
            }
        
        text = trafilatura.extract(downloaded)
        if not text:
            print(f"Failed to extract text from {url}")
            return {
                "status": "error",
                "error": "Failed to extract marine forecast text",
                "updated": current_time
            }
        
        # Process the text to extract relevant sections
        sections = {}
        current_section = "overview"
        sections[current_section] = []
        
        for line in text.split('\n'):
            line = line.strip()
            if not line:
                continue
                
            # Check for major section headers
            if "SMALL CRAFT ADVISORY" in line:
                current_section = "small_craft_advisory"
                sections[current_section] = [line]
            elif "TONIGHT" in line:
                current_section = "tonight"
                sections[current_section] = [line]
            elif "TOMORROW" in line or "TODAY" in line:
                current_section = "tomorrow"
                sections[current_section] = [line]
            elif "COASTAL WATERS FORECAST" in line:
                current_section = "coastal_waters_forecast"
                sections[current_section] = [line]
            elif "PZZ" in line:
                current_section = "zone_info"
                sections[current_section] = [line]
            elif "FT" in line and ("WIND" in line or "WAVES" in line or "SEAS" in line):
                current_section = "conditions"
                sections[current_section] = [line]
            else:
                # Add line to current section
                if current_section in sections:
                    sections[current_section].append(line)
        
        # Format the results
        result = {
            "status": "success",
            "updated": current_time,
            "sections": {}
        }
        
        # Extract key information
        for section, lines in sections.items():
            result["sections"][section] = "\n".join(lines)
        
        # Extract important warnings
        warnings = []
        if "small_craft_advisory" in sections:
            warnings.append(sections["small_craft_advisory"][0])
        
        result["warnings"] = warnings if warnings else ["No current marine warnings for this area"]
        
        return result
        
    except Exception as e:
        print(f"Error getting marine forecast: {e}")
        return {
            "status": "error",
            "error": str(e),
            "updated": datetime.now(pacific_tz).strftime('%H:%M %Z')
        }

@st.cache_data(ttl=3600)  # Cache for 1 hour
def get_tide_information():
    """
    Get tide information from NOAA tides and currents website.
    Uses web scraping to get the latest tide predictions and observations.
    
    Returns:
        Dictionary with tide information
    """
    try:
        # Get the current time in Pacific timezone
        pacific_tz = pytz.timezone('US/Pacific')
        current_time = datetime.now(pacific_tz).strftime('%H:%M %Z')
        
        # NOAA Tides and Currents for Seattle
        url = "https://tidesandcurrents.noaa.gov/noaatidepredictions.html?id=9447130"
        
        # Fetch and extract text from the URL
        downloaded = trafilatura.fetch_url(url)
        if not downloaded:
            print(f"Failed to download content from {url}")
            return {
                "status": "error",
                "error": "Failed to download tide information",
                "updated": current_time
            }
        
        text = trafilatura.extract(downloaded)
        if not text:
            print(f"Failed to extract text from {url}")
            return {
                "status": "error",
                "error": "Failed to extract tide information text",
                "updated": current_time
            }
        
        # Process the text to extract tide information
        tide_info = {
            "status": "success",
            "updated": current_time,
            "station": "Seattle, Puget Sound",
            "data": text
        }
        
        return tide_info
        
    except Exception as e:
        print(f"Error getting tide information: {e}")
        return {
            "status": "error",
            "error": str(e),
            "updated": datetime.now(pacific_tz).strftime('%H:%M %Z')
        }

@st.cache_data(ttl=3600)  # Cache for 1 hour
def get_marine_observations():
    """
    Get marine observations from NOAA buoy data.
    Uses web scraping to get the latest observations.
    
    Returns:
        Dictionary with marine observations
    """
    try:
        # Get the current time in Pacific timezone
        pacific_tz = pytz.timezone('US/Pacific')
        current_time = datetime.now(pacific_tz).strftime('%H:%M %Z')
        
        # NOAA Buoy Data for Puget Sound
        url = "https://www.ndbc.noaa.gov/station_page.php?station=sisw1"
        
        # Fetch and extract text from the URL
        downloaded = trafilatura.fetch_url(url)
        if not downloaded:
            print(f"Failed to download content from {url}")
            return {
                "status": "error",
                "error": "Failed to download marine observations",
                "updated": current_time
            }
        
        text = trafilatura.extract(downloaded)
        if not text:
            print(f"Failed to extract text from {url}")
            return {
                "status": "error",
                "error": "Failed to extract marine observations text",
                "updated": current_time
            }
        
        # Process the text to extract relevant information
        lines = text.split('\n')
        observations = {}
        
        for i, line in enumerate(lines):
            if "Wind Direction" in line and i+1 < len(lines):
                observations["wind_direction"] = lines[i+1].strip()
            elif "Wind Speed" in line and i+1 < len(lines):
                observations["wind_speed"] = lines[i+1].strip()
            elif "Wind Gust" in line and i+1 < len(lines):
                observations["wind_gust"] = lines[i+1].strip()
            elif "Wave Height" in line and i+1 < len(lines):
                observations["wave_height"] = lines[i+1].strip()
            elif "Atmospheric Pressure" in line and i+1 < len(lines):
                observations["pressure"] = lines[i+1].strip()
            elif "Air Temperature" in line and i+1 < len(lines):
                observations["air_temp"] = lines[i+1].strip()
            elif "Water Temperature" in line and i+1 < len(lines):
                observations["water_temp"] = lines[i+1].strip()
        
        return {
            "status": "success",
            "updated": current_time,
            "station": "Smith Island, Puget Sound",
            "observations": observations
        }
        
    except Exception as e:
        print(f"Error getting marine observations: {e}")
        return {
            "status": "error",
            "error": str(e),
            "updated": datetime.now(pacific_tz).strftime('%H:%M %Z')
        }