import pandas as pd
from datetime import datetime, timedelta

def format_time(dt_obj):
    """Format datetime object to 24-hour military time string (HH:MM)"""
    if isinstance(dt_obj, datetime):
        return dt_obj.strftime("%H:%M")
    return dt_obj

def format_date(date_obj):
    """Format date object to string (Day, Month Date)"""
    if isinstance(date_obj, datetime):
        date_obj = date_obj.date()
    return date_obj.strftime("%a, %b %d")

def get_date_range(selected_date, view_option):
    """
    Get a list of dates to fetch data for based on selected date and view option
    
    Args:
        selected_date: The main selected date
        view_option: 'Daily Forecast' or 'Weekly Overview'
        
    Returns:
        List of date objects
    """
    if view_option == "Daily Forecast":
        return [selected_date]
    else:
        # For weekly overview, get 7 days starting from selected date
        dates = [selected_date + timedelta(days=i) for i in range(7)]
        return dates

def is_high_tide(height):
    """Determine if tide height is considered high tide"""
    # Adjust thresholds based on local knowledge
    return height > 8.0

def is_strong_current(speed):
    """Determine if current is too strong for safe kayaking"""
    # Adjust thresholds based on local knowledge
    return speed > 2.3  # mph (2.0 knots converted to mph)

def is_high_wind(speed):
    """Determine if wind is too strong for safe kayaking"""
    # Adjust thresholds based on local knowledge
    return speed > 15.0

def get_wind_direction_text(degrees):
    """Convert wind direction degrees to cardinal direction text"""
    directions = [
        "N", "NNE", "NE", "ENE", "E", "ESE", "SE", "SSE",
        "S", "SSW", "SW", "WSW", "W", "WNW", "NW", "NNW"
    ]
    index = round(degrees / 22.5) % 16
    return directions[index]

def knots_to_mph(knots):
    """Convert speed from knots to miles per hour"""
    return knots * 1.15078

def get_tide_status(height, previous_height=None):
    """Determine if tide is rising, falling, or at extremes"""
    if previous_height is None:
        return "steady"
    
    if height > previous_height:
        return "rising"
    elif height < previous_height:
        return "falling"
    else:
        return "steady"

def get_optimal_tide_range():
    """Get the optimal tide height range for kayaking at Point White"""
    # These are example values and should be adjusted based on local conditions
    min_height = 4.0  # Low enough for beach access but not too low
    max_height = 8.0  # High enough for water depth but beach still accessible
    return (min_height, max_height)

def get_optimal_current_range():
    """Get the optimal current speed range for kayaking at Point White"""
    # These are example values and should be adjusted based on local conditions
    min_speed = 0.0  # Minimal current is generally better for beginners
    max_speed = 1.73  # Not too strong to paddle against (1.5 knots converted to mph)
    return (min_speed, max_speed)

def get_optimal_wind_range():
    """Get the optimal wind speed range for kayaking at Point White"""
    # These are example values and should be adjusted based on local conditions
    min_speed = 0.0  # Minimal wind is generally better
    max_speed = 10.0  # Not too strong to create challenging waves
    return (min_speed, max_speed)

def ferry_time_proximity(time, ferry_schedule):
    """
    Determine proximity to next ferry
    
    Args:
        time: Time to check
        ferry_schedule: List of ferry departure times
        
    Returns:
        Tuple: (minutes_to_ferry, direction)
    """
    if not ferry_schedule:
        return None, None
    
    # Convert string time to datetime if needed
    if not isinstance(time, datetime):
        hours, minutes = map(int, time.split(':'))
        time = datetime.now().replace(hour=hours, minute=minutes, second=0, microsecond=0)
    
    # Find the next ferry
    next_ferry = None
    min_diff = float('inf')
    direction = None
    
    for ferry in ferry_schedule:
        ferry_time = ferry['departure_time']
        ferry_dir = ferry['direction']
        
        # Calculate time difference in minutes
        diff = (ferry_time - time).total_seconds() / 60
        
        # Only consider upcoming ferries
        if 0 <= diff < min_diff:
            min_diff = diff
            next_ferry = ferry_time
            direction = ferry_dir
    
    if next_ferry:
        return min_diff, direction
    else:
        # If no upcoming ferry found, check for the earliest ferry tomorrow
        tomorrow_ferries = [f for f in ferry_schedule if f['departure_time'].day > time.day]
        if tomorrow_ferries:
            earliest = min(tomorrow_ferries, key=lambda x: x['departure_time'])
            diff = (earliest['departure_time'] - time).total_seconds() / 60
            return diff, earliest['direction']
        
        return None, None
