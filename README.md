# Bainbridge Island Kayak Launch Assistant

A Streamlit-powered application that provides kayak launch recommendations for Bainbridge Island, specifically for launches from Point White Drive NE. The app considers multiple environmental factors to suggest optimal launch times.

## Features

- **Tide Analysis**: Monitors tide levels and warns when the beach might be inaccessible due to high tide
- **Current Speed Tracking**: Displays current speeds and directions to avoid dangerous paddling conditions
- **Wind Conditions**: Incorporates wind data to assess safety for kayaking
- **Ferry Traffic**: Accounts for ferry schedules to avoid vessel traffic
- **Optimal Launch Windows**: Identifies and highlights the best times to launch throughout the day
- **Weekly Forecast**: Provides an overview of conditions for the upcoming week
- **Marine Weather Information**: Real-time marine forecasts, tide information, and weather observations

## Data Sources

- NOAA Tides and Currents API for tide and current data
- Washington State Ferries API for ferry schedules
- OpenWeatherMap for weather data
- NOAA Marine Weather forecasts

## Technical Details

- Built with Streamlit for interactive data visualization
- Uses pandas for data manipulation
- Plotly for interactive charts and graphs
- Trafilatura for web scraping marine information

## Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/bainbridge-kayak-assistant.git
cd bainbridge-kayak-assistant

# Install dependencies
pip install streamlit pandas plotly pytz requests trafilatura

# Run the application
streamlit run app.py
```

## Dependencies

- streamlit >= 1.25.0
- pandas >= 1.5.0
- plotly >= 5.14.0
- pytz >= 2023.3
- requests >= 2.28.0
- trafilatura >= 1.6.0

## Usage

1. Select a date using the sidebar controls
2. Choose between Daily Forecast or Weekly Overview
3. View optimal launch times highlighted in green
4. Check detailed environmental conditions in the expandable sections
5. Use the Marine Information section to see current marine forecasts

## License

MIT

## Author

Created for kayakers on Bainbridge Island