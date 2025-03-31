import requests
import pandas as pd
from datetime import datetime, timedelta
import os
import json
import time
import math
from utils import get_wind_direction_text

# API keys and base URLs
# Note: These would typically be in environment variables
NOAA_API_BASE_URL = "https://api.tidesandcurrents.noaa.gov/api/prod/datagetter"
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY", "your_openweather_api_key")
OPENWEATHER_API_BASE_URL = "https://api.openweathermap.org/data/2.5/forecast"
WSF_API_BASE_URL = "https://www.wsdot.wa.gov/ferries/api/schedule/rest"

# Station IDs for Point White Drive NE area
# These are example stations - real implementation would use the closest accurate stations
TIDE_STATION_ID = "9447130"  # Seattle station
CURRENT_STATION_ID = "PCT1641_17"  # Rich Passage current station

# Coordinates for Point White Drive NE on Bainbridge Island
POINT_WHITE_LAT = 47.5980
POINT_WHITE_LON = -122.5307

def get_tide_data(date):
    """
    Get tide data from NOAA CO-OPS API for a specific date
    
    Args:
        date: The date to get tide data for
        
    Returns:
        DataFrame with tide data (time and height columns)
    """
    # Format date strings for API request
    begin_date = date.strftime("%Y%m%d")
    end_date = (date + timedelta(days=1)).strftime("%Y%m%d")
    
    # Build API request URL
    params = {
        "begin_date": begin_date,
        "end_date": begin_date,
        "station": TIDE_STATION_ID,
        "product": "predictions",
        "datum": "MLLW",
        "time_zone": "lst_ldt",
        "interval": "h",
        "units": "english",
        "format": "json"
    }
    
    try:
        # Make API request with exponential backoff for retries
        max_retries = 3
        retry_delay = 1
        
        for attempt in range(max_retries):
            try:
                response = requests.get(NOAA_API_BASE_URL, params=params)
                response.raise_for_status()
                
                # Parse response
                data = response.json()
                
                if "predictions" in data:
                    # Process tide predictions
                    predictions = data["predictions"]
                    
                    times = []
                    heights = []
                    
                    for pred in predictions:
                        # Parse date and time
                        dt = datetime.strptime(pred["t"], "%Y-%m-%d %H:%M")
                        times.append(dt)
                        heights.append(float(pred["v"]))
                    
                    # Create DataFrame
                    df = pd.DataFrame({
                        "time": times,
                        "height": heights
                    })
                    
                    return df
                else:
                    # Handle case where no predictions are returned
                    print(f"No tide predictions found in response: {data}")
                    return None
                
            except requests.RequestException as e:
                if attempt < max_retries - 1:
                    # Wait with exponential backoff before retrying
                    time.sleep(retry_delay)
                    retry_delay *= 2
                else:
                    # Last attempt failed
                    print(f"Failed to fetch tide data after {max_retries} attempts: {str(e)}")
                    return None
                    
    except Exception as e:
        print(f"Error getting tide data: {str(e)}")
        return None

def get_current_data(date):
    """
    Get current data from NOAA CO-OPS API for a specific date
    
    Args:
        date: The date to get current data for
        
    Returns:
        DataFrame with current data (time, speed, and direction columns)
    """
    # Format date strings for API request
    begin_date = date.strftime("%Y%m%d")
    end_date = (date + timedelta(days=1)).strftime("%Y%m%d")
    
    # Build API request URL
    params = {
        "begin_date": begin_date,
        "end_date": begin_date,
        "station": CURRENT_STATION_ID,
        "product": "currents_predictions",
        "time_zone": "lst_ldt",
        "interval": "h",
        "units": "english",
        "format": "json"
    }
    
    try:
        # Make API request with exponential backoff for retries
        max_retries = 3
        retry_delay = 1
        
        for attempt in range(max_retries):
            try:
                response = requests.get(NOAA_API_BASE_URL, params=params)
                response.raise_for_status()
                
                # Parse response
                data = response.json()
                
                if "current_predictions" in data:
                    # Process current predictions
                    predictions = data["current_predictions"]["cp"]
                    
                    times = []
                    speeds = []
                    directions = []
                    
                    for pred in predictions:
                        # Parse date and time
                        dt = datetime.strptime(pred["Time"], "%Y-%m-%d %H:%M")
                        times.append(dt)
                        speeds.append(float(pred["Velocity_Major"]))
                        directions.append(float(pred["Bin"]) if "Bin" in pred else 0)  # Direction might not be in all records
                    
                    # Create DataFrame
                    df = pd.DataFrame({
                        "time": times,
                        "speed": speeds,
                        "direction": directions
                    })
                    
                    return df
                else:
                    # Handle case where no predictions are returned
                    print(f"No current predictions found in response: {data}")
                    
                    # Fallback: Generate synthetic current data for demo purposes
                    # In a real app, this would be more sophisticated or use a backup data source
                    times = []
                    speeds = []
                    directions = []
                    
                    # Generate hourly data for the day
                    for hour in range(24):
                        time_point = datetime.combine(date, datetime.min.time()) + timedelta(hours=hour)
                        times.append(time_point)
                        
                        # Simulate tidal current pattern with two peaks per day
                        # This is a very simplified model
                        hour_frac = hour / 24.0 * 2 * math.pi  # Convert hour to radians
                        speed = abs(1.5 * math.sin(hour_frac)) + 0.2  # Speed between 0.2 and 1.7 knots
                        
                        # Direction alternates with tide
                        if math.sin(hour_frac) > 0:
                            direction = 90  # Ebb tide (flowing east)
                        else:
                            direction = 270  # Flood tide (flowing west)
                        
                        speeds.append(speed)
                        directions.append(direction)
                    
                    # Create DataFrame
                    df = pd.DataFrame({
                        "time": times,
                        "speed": speeds,
                        "direction": directions
                    })
                    
                    return df
                
            except requests.RequestException as e:
                if attempt < max_retries - 1:
                    # Wait with exponential backoff before retrying
                    time.sleep(retry_delay)
                    retry_delay *= 2
                else:
                    # Last attempt failed
                    print(f"Failed to fetch current data after {max_retries} attempts: {str(e)}")
                    return None
                    
    except Exception as e:
        print(f"Error getting current data: {str(e)}")
        return None

def get_ferry_schedule(date):
    """
    Get Washington State Ferries schedule for Bainbridge-Seattle route
    
    Args:
        date: The date to get ferry schedule for
        
    Returns:
        List of dictionaries with ferry schedule information
    """
    # Format date for API request
    date_str = date.strftime("%Y-%m-%d")
    
    try:
        # In a real implementation, this would use the WSF API
        # For this example, we'll create a simplified ferry schedule
        
        # Define Seattle-Bainbridge ferry schedule (simplified)
        # In a real app, this would come from the API
        seattle_departures = [
            "05:20", "06:10", "07:05", "07:55", "08:45", 
            "09:35", "10:25", "11:15", "12:05", "12:55", 
            "13:45", "14:35", "15:30", "16:15", "17:05", 
            "17:55", "18:45", "19:35", "20:30", "21:15", 
            "22:05", "23:00"
        ]
        
        bainbridge_departures = [
            "04:45", "05:40", "06:30", "07:15", "08:10", 
            "09:00", "09:50", "10:40", "11:30", "12:20", 
            "13:10", "14:00", "14:50", "15:40", "16:30", 
            "17:20", "18:10", "19:00", "19:45", "20:40", 
            "21:25", "22:15"
        ]
        
        # Create schedule data
        schedule = []
        
        # Add Seattle to Bainbridge departures
        for time_str in seattle_departures:
            hours, minutes = map(int, time_str.split(":"))
            departure_time = datetime.combine(date, datetime.min.time())
            departure_time = departure_time.replace(hour=hours, minute=minutes)
            
            schedule.append({
                "departure_time": departure_time,
                "arrival_time": departure_time + timedelta(minutes=35),  # Approx 35 min crossing
                "direction": "Seattle to Bainbridge",
                "vessel": "Ferry"
            })
        
        # Add Bainbridge to Seattle departures
        for time_str in bainbridge_departures:
            hours, minutes = map(int, time_str.split(":"))
            departure_time = datetime.combine(date, datetime.min.time())
            departure_time = departure_time.replace(hour=hours, minute=minutes)
            
            schedule.append({
                "departure_time": departure_time,
                "arrival_time": departure_time + timedelta(minutes=35),  # Approx 35 min crossing
                "direction": "Bainbridge to Seattle",
                "vessel": "Ferry"
            })
        
        return schedule
        
    except Exception as e:
        print(f"Error getting ferry schedule: {str(e)}")
        return []

def get_weather_data(date):
    """
    Get weather forecast data from OpenWeatherMap API
    
    Args:
        date: The date to get weather forecast for
        
    Returns:
        DataFrame with hourly weather data
    """
    # Calculate unix timestamps for start/end of day
    start_timestamp = int(datetime.combine(date, datetime.min.time()).timestamp())
    end_timestamp = int(datetime.combine(date, datetime.max.time()).timestamp())
    
    # Build API request URL
    params = {
        "lat": POINT_WHITE_LAT,
        "lon": POINT_WHITE_LON,
        "appid": OPENWEATHER_API_KEY,
        "units": "imperial"  # Use imperial for mph, fahrenheit
    }
    
    try:
        # Make API request with exponential backoff for retries
        max_retries = 3
        retry_delay = 1
        
        for attempt in range(max_retries):
            try:
                # If we're using the demo key, return simulated data instead
                if OPENWEATHER_API_KEY == "your_openweather_api_key":
                    return generate_simulated_weather_data(date)
                    
                response = requests.get(OPENWEATHER_API_BASE_URL, params=params)
                response.raise_for_status()
                
                # Parse response
                data = response.json()
                
                if "list" in data:
                    # Process forecast data
                    forecast_list = data["list"]
                    
                    times = []
                    temps = []
                    wind_speeds = []
                    wind_directions = []
                    conditions = []
                    
                    for forecast in forecast_list:
                        dt = datetime.fromtimestamp(forecast["dt"])
                        
                        # Only include forecasts for the requested date
                        if dt.date() == date:
                            times.append(dt)
                            temps.append(forecast["main"]["temp"])
                            wind_speeds.append(forecast["wind"]["speed"])
                            wind_dirs = get_wind_direction_text(forecast["wind"]["deg"])
                            wind_directions.append(wind_dirs)
                            conditions.append(forecast["weather"][0]["main"])
                    
                    # Create DataFrame
                    df = pd.DataFrame({
                        "time": times,
                        "temperature": temps,
                        "wind_speed": wind_speeds,
                        "wind_direction": wind_directions,
                        "condition": conditions
                    })
                    
                    # If no data was found for the requested date (may happen for dates far in the future)
                    if df.empty:
                        return generate_simulated_weather_data(date)
                    
                    return df
                else:
                    # Handle case where no forecast data is returned
                    print(f"No forecast data found in response: {data}")
                    return generate_simulated_weather_data(date)
                
            except requests.RequestException as e:
                if attempt < max_retries - 1:
                    # Wait with exponential backoff before retrying
                    time.sleep(retry_delay)
                    retry_delay *= 2
                else:
                    # Last attempt failed
                    print(f"Failed to fetch weather data after {max_retries} attempts: {str(e)}")
                    return generate_simulated_weather_data(date)
                    
    except Exception as e:
        print(f"Error getting weather data: {str(e)}")
        return generate_simulated_weather_data(date)

def generate_simulated_weather_data(date):
    """
    Generate simulated weather data when API access is not available
    
    Args:
        date: The date to generate weather data for
        
    Returns:
        DataFrame with simulated hourly weather data
    """
    # Create synthetic weather data for demo purposes
    times = []
    temps = []
    wind_speeds = []
    wind_directions = []
    conditions = []
    
    # Base weather patterns - adjust based on season
    month = date.month
    is_summer = 5 <= month <= 9
    
    # Base temperature varies by season
    base_temp = 70 if is_summer else 45
    
    # Base wind pattern - typically calmer in morning, stronger in afternoon
    base_wind = 8 if is_summer else 12
    
    # Generate hourly data for the day
    for hour in range(24):
        time_point = datetime.combine(date, datetime.min.time()) + timedelta(hours=hour)
        times.append(time_point)
        
        # Temperature varies by time of day
        hour_factor = abs(hour - 14) / 14.0  # 0 at 2pm (warmest), 1 at 2am (coldest)
        temp_variation = 15 if is_summer else 10
        temp = base_temp - hour_factor * temp_variation + (hash(str(date)) % 5)  # Add some day-to-day variation
        temps.append(temp)
        
        # Wind tends to be higher in the afternoon
        afternoon_factor = 1.0 - abs(hour - 14) / 14.0  # 1 at 2pm, 0 at 2am
        wind_variation = 8 if is_summer else 10
        wind = base_wind + afternoon_factor * wind_variation * (0.5 + (hash(str(date) + str(hour)) % 100) / 100.0)
        wind_speeds.append(wind)
        
        # Wind direction shifts throughout the day
        wind_dir_base = (hash(str(date)) % 4) * 90  # Base direction changes by day
        wind_dir_shift = hour * 15 % 360  # Direction shifts throughout day
        wind_direction = (wind_dir_base + wind_dir_shift) % 360
        wind_directions.append(get_wind_direction_text(wind_direction))
        
        # Weather conditions
        if wind > 15:
            condition = "Windy"
        elif hour_factor < 0.3 and (hash(str(date) + str(hour)) % 100) < 70:
            condition = "Clear"
        else:
            condition = "Cloudy" if (hash(str(date) + str(hour)) % 100) < 70 else "Rainy"
        
        conditions.append(condition)
    
    # Create DataFrame
    df = pd.DataFrame({
        "time": times,
        "temperature": temps,
        "wind_speed": wind_speeds,
        "wind_direction": wind_directions,
        "condition": conditions
    })
    
    return df
