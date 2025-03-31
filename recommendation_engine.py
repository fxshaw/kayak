import pandas as pd
from datetime import datetime, timedelta
import math
from utils import (
    is_high_tide,
    is_strong_current,
    is_high_wind,
    get_optimal_tide_range,
    get_optimal_current_range,
    get_optimal_wind_range,
    ferry_time_proximity,
    get_tide_status
)

# Define colors for ratings
OPTIMAL_COLOR = "#2ecc71"  # Green
ACCEPTABLE_COLOR = "#f1c40f"  # Yellow/Orange
NOT_RECOMMENDED_COLOR = "#e74c3c"  # Red

def get_launch_recommendations(tide_data, current_data, ferry_data, weather_data):
    """
    Generate kayak launch recommendations by combining all data sources
    
    Args:
        tide_data: DataFrame of tide predictions
        current_data: DataFrame of current predictions
        ferry_data: List of ferry schedule data
        weather_data: DataFrame of weather predictions
        
    Returns:
        List of hourly recommendations with ratings
    """
    # Check for missing data
    if tide_data is None or current_data is None or not ferry_data or weather_data is None:
        print("Warning: Missing data for recommendations")
        return []
    
    # Get ranges for optimal conditions
    optimal_tide_range = get_optimal_tide_range()
    optimal_current_range = get_optimal_current_range()
    optimal_wind_range = get_optimal_wind_range()
    
    # Initialize recommendations
    recommendations = []
    
    # Process hourly data
    for hour in range(24):
        # Create time point for this hour
        hour_time = tide_data['time'].iloc[0].replace(hour=hour, minute=0, second=0)
        
        # Get tide data for this hour
        tide_hour_data = tide_data[tide_data['time'].dt.hour == hour]
        if tide_hour_data.empty:
            continue
        
        tide_height = tide_hour_data['height'].iloc[0]
        previous_hour = (hour - 1) % 24
        previous_tide_data = tide_data[tide_data['time'].dt.hour == previous_hour]
        previous_height = previous_tide_data['height'].iloc[0] if not previous_tide_data.empty else None
        tide_status = get_tide_status(tide_height, previous_height)
        
        # Get current data for this hour
        current_hour_data = current_data[current_data['time'].dt.hour == hour]
        if current_hour_data.empty:
            continue
        
        current_speed = current_hour_data['speed'].iloc[0]
        if 'direction' in current_hour_data:
            current_direction = current_hour_data['direction'].iloc[0]
            current_direction_text = 'flooding' if 0 <= current_direction <= 180 else 'ebbing'
        else:
            current_direction_text = 'unknown'
        
        # Get weather data for this hour
        weather_hour_data = weather_data[weather_data['time'].dt.hour == hour]
        if weather_hour_data.empty:
            # Find the closest weather data point
            closest_hour = min(weather_data['time'], key=lambda x: abs((x - hour_time).total_seconds()))
            weather_hour_data = weather_data[weather_data['time'] == closest_hour]
            if weather_hour_data.empty:
                continue
        
        wind_speed = weather_hour_data['wind_speed'].iloc[0]
        wind_direction = weather_hour_data['wind_direction'].iloc[0]
        
        # Get ferry information
        min_to_ferry, ferry_direction = ferry_time_proximity(f"{hour}:00", ferry_data)
        if min_to_ferry is not None:
            if min_to_ferry < 15:
                ferry_status = f"Caution: {ferry_direction} ferry in {int(min_to_ferry)} minutes"
            elif min_to_ferry < 30:
                ferry_status = f"{ferry_direction} ferry in {int(min_to_ferry)} minutes"
            else:
                ferry_status = "No ferries soon"
        else:
            ferry_status = "No ferry data"
        
        # Calculate rating based on all factors
        
        # Tide factor (0-1, 1 is best)
        if optimal_tide_range[0] <= tide_height <= optimal_tide_range[1]:
            tide_factor = 1.0
        else:
            # How far outside optimal range
            if tide_height < optimal_tide_range[0]:
                tide_factor = 1.0 - min(1.0, (optimal_tide_range[0] - tide_height) / 4.0)
            else:  # tide_height > optimal_tide_range[1]
                tide_factor = 1.0 - min(1.0, (tide_height - optimal_tide_range[1]) / 4.0)
        
        # Beach disappears at high tide
        if tide_height > 10.0:
            tide_factor = 0.0  # No beach access
        
        # Current factor (0-1, 1 is best)
        if optimal_current_range[0] <= current_speed <= optimal_current_range[1]:
            current_factor = 1.0
        else:
            # How far outside optimal range
            if current_speed < optimal_current_range[0]:
                current_factor = 1.0  # Slow current is fine
            else:  # current_speed > optimal_current_range[1]
                current_factor = 1.0 - min(1.0, (current_speed - optimal_current_range[1]) / 2.0)
        
        # Wind factor (0-1, 1 is best)
        if optimal_wind_range[0] <= wind_speed <= optimal_wind_range[1]:
            wind_factor = 1.0
        else:
            # How far outside optimal range
            if wind_speed < optimal_wind_range[0]:
                wind_factor = 1.0  # Light wind is fine
            else:  # wind_speed > optimal_wind_range[1]
                wind_factor = 1.0 - min(1.0, (wind_speed - optimal_wind_range[1]) / 10.0)
        
        # Ferry factor (0-1, 1 is best)
        if min_to_ferry is not None and min_to_ferry < 15:
            ferry_factor = 0.5  # Caution near ferry times
        else:
            ferry_factor = 1.0
        
        # Combine factors with weights
        weighted_score = (
            tide_factor * 0.35 +    # Tide is very important for beach access
            current_factor * 0.3 +  # Current is important for safety
            wind_factor * 0.25 +    # Wind affects wave conditions
            ferry_factor * 0.1      # Ferry proximity is a concern but can be managed
        )
        
        # Assign rating based on combined score
        if weighted_score >= 0.8:
            rating = "optimal"
        elif weighted_score >= 0.6:
            rating = "acceptable"
        else:
            rating = "not_recommended"
        
        # Create recommendation entry
        recommendation = {
            'hour': hour,
            'start_time': f"{hour:02d}:00",
            'end_time': f"{(hour+1) % 24:02d}:00",
            'tide_height': f"{tide_height:.1f}",
            'tide_status': tide_status,
            'current_speed': f"{current_speed:.1f}",
            'current_direction': current_direction_text,
            'wind_speed': f"{wind_speed:.1f}",
            'wind_direction': wind_direction,
            'ferry_status': ferry_status,
            'score': weighted_score,
            'rating': rating
        }
        
        recommendations.append(recommendation)
    
    return recommendations
