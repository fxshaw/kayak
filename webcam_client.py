import requests
from datetime import datetime
import pytz
import streamlit as st

# Cache webcam images to avoid hitting rate limits
@st.cache_data(ttl=600)  # Cache for 10 minutes
def get_webcam_image(url):
    """
    Get a webcam image from a URL
    
    Args:
        url: The URL of the webcam image
        
    Returns:
        The image bytes if successful, None otherwise
    """
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        print(f"Response status for {url}: {response.status_code}")
        if response.status_code == 200:
            return response.content
        else:
            print(f"Failed to get image from {url}, status code: {response.status_code}")
            return None
    except Exception as e:
        print(f"Error getting webcam image: {e}")
        return None

def get_seattle_ferry_webcam():
    """
    Get the Seattle-Bainbridge Ferry Terminal webcam image
    
    Returns:
        The image bytes if successful, None otherwise
    """
    # Seattle ferry terminal view - updated URL from WSDOT traffic cameras
    url = "https://images.wsdot.wa.gov/nw/099vc16008.jpg"
    return get_webcam_image(url)

def get_bainbridge_ferry_webcam():
    """
    Get the Bainbridge Island Ferry Terminal webcam image
    
    Returns:
        The image bytes if successful, None otherwise
    """
    # Bainbridge Island ferry terminal camera
    url = "https://images.wsdot.wa.gov/nw/305vc00969.jpg"
    return get_webcam_image(url)

def get_elliot_bay_webcam():
    """
    Get a view of Elliott Bay
    
    Returns:
        The image bytes if successful, None otherwise
    """
    # Elliott Bay view
    url = "https://cdn.tegna-media.com/king/weather/seattleskyline.jpg"
    return get_webcam_image(url)

def get_bremerton_ferry_webcam():
    """
    Get the Bremerton Ferry Terminal webcam image
    
    Returns:
        The image bytes if successful, None otherwise
    """
    # Bremerton Terminal webcam
    url = "https://images.wsdot.wa.gov/sw/304vc00000.jpg"
    return get_webcam_image(url)

def get_tacoma_narrows_webcam():
    """
    Get a view of the Tacoma Narrows Bridge
    
    Returns:
        The image bytes if successful, None otherwise
    """
    # Tacoma Narrows Bridge webcam (for water conditions in the South Sound)
    url = "https://images.wsdot.wa.gov/sw/016vc00438.jpg"
    return get_webcam_image(url)

def get_puget_sound_web_cam():
    """
    Get a view of Puget Sound weather conditions (Space Needle cam)
    
    Returns:
        The image bytes if successful, None otherwise
    """
    # Space Needle webcam showing Puget Sound weather
    url = "https://spaceneedle.com/wp-content/uploads/2023/06/spaceneedle_west.jpg"
    return get_webcam_image(url)

def get_point_white_area_webcams():
    """
    Get all available webcams near Point White area
    
    Returns:
        Dictionary of webcam images with their descriptions
    """
    pacific_tz = pytz.timezone('US/Pacific')
    current_time = datetime.now(pacific_tz).strftime('%H:%M')
    
    webcams = {
        "Bainbridge Ferry Terminal": {
            "image": get_bainbridge_ferry_webcam(),
            "description": "View of the Bainbridge Island Ferry Terminal",
            "updated": current_time
        },
        "Seattle Waterfront": {
            "image": get_seattle_ferry_webcam(),
            "description": "View of the Seattle Waterfront near Ferry Terminal",
            "updated": current_time
        },
        "Elliott Bay": {
            "image": get_elliot_bay_webcam(), 
            "description": "View of Elliott Bay from Seattle",
            "updated": current_time
        },
        "Bremerton Ferry Terminal": {
            "image": get_bremerton_ferry_webcam(),
            "description": "View of the Bremerton Ferry Terminal",
            "updated": current_time
        },
        "Puget Sound Weather": {
            "image": get_puget_sound_web_cam(),
            "description": "View of Puget Sound weather conditions",
            "updated": current_time
        },
        "Tacoma Narrows": {
            "image": get_tacoma_narrows_webcam(),
            "description": "View of Tacoma Narrows Bridge and water conditions",
            "updated": current_time
        }
    }
    
    # Filter out any webcams that failed to load
    return {k: v for k, v in webcams.items() if v["image"] is not None}