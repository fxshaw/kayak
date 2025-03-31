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
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            return response.content
        else:
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
    # Seattle Ferry Terminal webcam (Coleman Dock)
    url = "https://images.wsdot.wa.gov/ferries/sr520/SRCam.jpg"
    return get_webcam_image(url)

def get_bainbridge_ferry_webcam():
    """
    Get the Bainbridge Island Ferry Terminal webcam image
    
    Returns:
        The image bytes if successful, None otherwise
    """
    # This is WSDOT's Bainbridge Island Terminal camera
    url = "https://images.wsdot.wa.gov/nw/010vc00082.jpg"
    return get_webcam_image(url)

def get_eagle_harbor_webcam():
    """
    Get a view of Eagle Harbor on Bainbridge Island
    
    Returns:
        The image bytes if successful, None otherwise
    """
    # Eagle Harbor Marina webcam
    url = "https://images.wsdot.wa.gov/nw/010vc00516.jpg"
    return get_webcam_image(url)

def get_bremerton_ferry_webcam():
    """
    Get the Bremerton Ferry Terminal webcam image
    
    Returns:
        The image bytes if successful, None otherwise
    """
    # Bremerton Terminal webcam
    url = "https://images.wsdot.wa.gov/sw/006vc16001.jpg"
    return get_webcam_image(url)

def get_rich_passage_webcam():
    """
    Get a view of Rich Passage (between Bainbridge and Bremerton)
    
    Returns:
        The image bytes if successful, None otherwise
    """
    # Rich Passage webcam
    url = "https://images.wsdot.wa.gov/sw/006vc17219.jpg"
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
        "Eagle Harbor": {
            "image": get_eagle_harbor_webcam(), 
            "description": "View of Eagle Harbor on Bainbridge Island",
            "updated": current_time
        },
        "Seattle Ferry Terminal": {
            "image": get_seattle_ferry_webcam(),
            "description": "View of the Seattle Ferry Terminal (Coleman Dock)",
            "updated": current_time
        },
        "Bremerton Ferry Terminal": {
            "image": get_bremerton_ferry_webcam(),
            "description": "View of the Bremerton Ferry Terminal",
            "updated": current_time
        },
        "Rich Passage": {
            "image": get_rich_passage_webcam(),
            "description": "View of Rich Passage (between Bainbridge and Bremerton)",
            "updated": current_time
        }
    }
    
    # Filter out any webcams that failed to load
    return {k: v for k, v in webcams.items() if v["image"] is not None}