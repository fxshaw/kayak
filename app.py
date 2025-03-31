import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import time
import pytz
from utils import format_time, format_date, get_date_range, get_pacific_time
from api_clients import (
    get_tide_data, 
    get_current_data, 
    get_ferry_schedule, 
    get_weather_data,
    get_sun_times
)
from recommendation_engine import (
    get_launch_recommendations,
    OPTIMAL_COLOR,
    ACCEPTABLE_COLOR,
    NOT_RECOMMENDED_COLOR
)

# Configure page
st.set_page_config(
    page_title="Bainbridge Island Kayak Launch Assistant",
    page_icon="🚣",
    layout="wide"
)

# Title and introduction
st.title("🚣 Bainbridge Island Kayak Launch Assistant")
st.markdown("### Point White Drive NE Launch Conditions")
st.markdown("""
This application provides recommendations for kayak launches from Point White Drive NE on Bainbridge Island.
Recommendations are based on tide levels, current speed, ferry schedules, and wind conditions.
""")

# Sidebar for date selection
with st.sidebar:
    st.header("Settings")
    
    # Date selection
    today = get_pacific_time().date()
    
    # Custom date selector with US format
    st.markdown("**Select date**")
    month = st.selectbox("Month", 
                        options=range(1, 13),
                        format_func=lambda x: f"{x:02d}",
                        index=today.month-1,
                        key="month_select")
    
    day = st.selectbox("Day", 
                      options=range(1, 32),
                      format_func=lambda x: f"{x:02d}",
                      index=today.day-1,
                      key="day_select")
    
    year = st.selectbox("Year", 
                       options=[today.year, today.year + 1],
                       index=0,
                       key="year_select")
    
    # Create date object from selections
    try:
        selected_date = datetime(year, month, day).date()
        # Ensure selected date is not before today
        if selected_date < today:
            selected_date = today
        # Ensure selected date is not more than 7 days in the future
        max_date = today + timedelta(days=7)
        if selected_date > max_date:
            selected_date = max_date
        
        st.markdown(f"**Selected: {format_date(selected_date)}**")
        
        # Add refresh button
        if st.button("Refresh Data for Selected Date", key="refresh_button"):
            st.rerun()
            
    except ValueError:
        # Handle invalid dates like Feb 31
        st.warning("Invalid date selection. Using today's date.")
        selected_date = today
    
    # View options
    view_option = st.radio(
        "View mode",
        ["Daily Forecast", "Weekly Overview"]
    )
    
    # Show information about the recommendations
    st.header("Legend")
    st.markdown(f"""
    - <span style='color:{OPTIMAL_COLOR};'>●</span> **Optimal**: Perfect conditions for launching
    - <span style='color:{ACCEPTABLE_COLOR};'>●</span> **Acceptable**: Safe but not ideal conditions
    - <span style='color:{NOT_RECOMMENDED_COLOR};'>●</span> **Not Recommended**: Avoid launching at these times
    """, unsafe_allow_html=True)
    
    st.header("Location Details")
    st.markdown("""
    **Point White Drive NE, Bainbridge Island**
    
    Considerations:
    - High tide limits beach access
    - Strong currents can make kayaking unsafe
    - Ferry traffic creates waves and hazards
    - Wind conditions affect water safety
    """)
    
    with st.expander("About This App"):
        st.markdown("""
        This app uses data from:
        - NOAA for tide and current information
        - Washington State Ferries API for ferry schedules
        - OpenWeatherMap for wind and weather data
        
        Refresh rate: Data is updated hourly
        """)

# Get data based on selected date/view
dates_to_fetch = get_date_range(selected_date, view_option)

# Main content area
if view_option == "Daily Forecast":
    # Display information for selected date
    st.header(f"Launch Forecast for {format_date(selected_date)}")
    
    # Try to load data with error handling
    with st.spinner("Fetching data..."):
        try:
            # Get data from APIs
            tide_data = get_tide_data(selected_date)
            current_data = get_current_data(selected_date)
            ferry_data = get_ferry_schedule(selected_date)
            weather_data = get_weather_data(selected_date)
            
            # Get sunrise and sunset times
            sun_times = get_sun_times(selected_date)
            sunrise_time = format_time(sun_times['sunrise'])
            sunset_time = format_time(sun_times['sunset'])
            
            # Display sunrise and sunset information
            st.markdown(f"""
            **Daylight Hours:**  
            Sunrise: {sunrise_time} | Sunset: {sunset_time}  
            *Recommendations only include daylight hours with a 30-minute buffer before sunrise and after sunset.*
            """)
            
            # Get recommendations based on all conditions
            recommendations = get_launch_recommendations(
                tide_data, current_data, ferry_data, weather_data
            )
            
            # SIMPLIFIED VIEW: Start with clean display of ideal launch times
            if recommendations:
                # Get the optimal launch windows
                optimal_windows = [r for r in recommendations if r['rating'] == 'optimal']
                acceptable_windows = [r for r in recommendations if r['rating'] == 'acceptable']
                
                # Current conditions
                current_hour = get_pacific_time().hour
                current_conditions = None
                
                for r in recommendations:
                    start_hour = int(r['start_time'].split(':')[0])
                    if start_hour <= current_hour < start_hour + 1:
                        current_conditions = r
                        break
                
                # Show current status first
                if current_conditions:
                    rating_color = {
                        'optimal': OPTIMAL_COLOR,
                        'acceptable': ACCEPTABLE_COLOR,
                        'not_recommended': NOT_RECOMMENDED_COLOR
                    }[current_conditions['rating']]
                    
                    status_text = "OPTIMAL TIME TO LAUNCH! 🚣" if current_conditions['rating'] == 'optimal' else \
                                "ACCEPTABLE TO LAUNCH" if current_conditions['rating'] == 'acceptable' else \
                                "NOT RECOMMENDED FOR LAUNCH"
                    
                    st.markdown(f"""
                    <div style="padding: 20px; border-radius: 10px; background-color: {rating_color}; margin: 20px 0; text-align: center;">
                        <h2 style="margin:0; color: white;">{status_text}</h2>
                        <p style="margin:5px 0 0 0; color: white; font-size: 18px;">
                            Current Time: {get_pacific_time().strftime('%H:%M')}
                        </p>
                    </div>
                    """, unsafe_allow_html=True)
                
                # Display optimal windows prominently
                st.subheader("Today's Optimal Launch Windows")
                if optimal_windows:
                    # Create a more visually prominent display of optimal times
                    cols = st.columns(min(3, len(optimal_windows)))
                    for i, window in enumerate(optimal_windows[:3]):
                        with cols[i]:
                            st.markdown(f"""
                            <div style="padding: 15px; border-radius: 10px; background-color: {OPTIMAL_COLOR}; text-align: center;">
                                <h3 style="margin:0; color: white;">{window['start_time']} - {window['end_time']}</h3>
                            </div>
                            """, unsafe_allow_html=True)
                else:
                    st.info("No optimal launch windows available today.")
                    if acceptable_windows:
                        st.subheader("Best Alternatives")
                        cols = st.columns(min(3, len(acceptable_windows)))
                        for i, window in enumerate(acceptable_windows[:3]):
                            with cols[i]:
                                st.markdown(f"""
                                <div style="padding: 15px; border-radius: 10px; background-color: {ACCEPTABLE_COLOR}; text-align: center;">
                                    <h3 style="margin:0; color: white;">{window['start_time']} - {window['end_time']}</h3>
                                </div>
                                """, unsafe_allow_html=True)
                    else:
                        st.error("No suitable launch windows available today. Consider another day.")
            else:
                st.error("Could not generate recommendations with the available data.")
            
            # Add expander for detailed information
            with st.expander("View Detailed Environmental Conditions"):
                # Create columns for different data displays
                col1, col2 = st.columns(2)
                
                # Current details
                with col1:
                    if current_conditions:
                        st.subheader("Current Conditions")
                        st.markdown(f"""
                        <div style="padding: 15px; border-radius: 5px; background-color: rgba(52, 152, 219, 0.1);">
                            <h4 style="margin:0; color: {rating_color};">Status: {current_conditions['rating'].title()}</h4>
                            <p style="margin:0;">
                                <strong>Tide:</strong> {current_conditions['tide_height']}ft ({current_conditions['tide_status']})<br>
                                <strong>Current:</strong> {current_conditions['current_speed']} mph ({current_conditions['current_direction']})<br>
                                <strong>Wind:</strong> {current_conditions['wind_speed']} mph from {current_conditions['wind_direction']}<br>
                                <strong>Next Ferry:</strong> {current_conditions['ferry_status']}
                            </p>
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.info("Current conditions data not available")
                    
                    # Top recommendations 
                    st.subheader("Top Launch Windows")
                    if optimal_windows:
                        for window in optimal_windows[:3]:  # Show top 3 optimal windows
                            st.markdown(f"""
                            <div style="padding: 10px; border-radius: 5px; background-color: rgba(46, 204, 113, 0.1); margin-bottom: 10px;">
                                <h4 style="margin:0; color: {OPTIMAL_COLOR};">🚣 {window['start_time']} - {window['end_time']}</h4>
                                <p style="margin:0;">Tide: {window['tide_height']}ft | Current: {window['current_speed']} mph<br>
                                Wind: {window['wind_speed']} mph {window['wind_direction']} | Ferry: {window['ferry_status']}</p>
                            </div>
                            """, unsafe_allow_html=True)
                    elif acceptable_windows:
                        for window in acceptable_windows[:3]:
                            st.markdown(f"""
                            <div style="padding: 10px; border-radius: 5px; background-color: rgba(241, 196, 15, 0.1); margin-bottom: 10px;">
                                <h4 style="margin:0; color: {ACCEPTABLE_COLOR};">🚣 {window['start_time']} - {window['end_time']}</h4>
                                <p style="margin:0;">Tide: {window['tide_height']}ft | Current: {window['current_speed']} mph<br>
                                Wind: {window['wind_speed']} mph {window['wind_direction']} | Ferry: {window['ferry_status']}</p>
                            </div>
                            """, unsafe_allow_html=True)
                
                # Visualizations
                with col2:
                    # Create tide chart
                    st.subheader("Tide Forecast")
                    if tide_data is not None and len(tide_data) > 0:
                        fig = px.line(
                            tide_data, 
                            x='time', 
                            y='height', 
                            title="Tide Heights (ft)",
                            labels={"time": "Time", "height": "Height (ft)"}
                        )
                        
                        # Add high tide danger zone
                        high_tide_threshold = 10.0  # Assuming beach disappears around 10ft tide
                        fig.add_shape(
                            type="rect",
                            x0=tide_data['time'].min(),
                            x1=tide_data['time'].max(),
                            y0=high_tide_threshold,
                            y1=max(tide_data['height'].max() + 1, high_tide_threshold + 2),
                            fillcolor="rgba(255, 0, 0, 0.2)",
                            line=dict(width=0),
                            layer="below"
                        )
                        fig.add_annotation(
                            x=tide_data['time'].iloc[len(tide_data)//2],
                            y=high_tide_threshold + 0.5,
                            text="Beach Access Limited",
                            showarrow=False,
                            font=dict(color="red")
                        )
                        
                        # Improve appearance
                        fig.update_layout(
                            height=300,
                            margin=dict(l=20, r=20, t=40, b=20)
                        )
                        st.plotly_chart(fig, use_container_width=True)
                    else:
                        st.error("Tide data not available")
                    
                    # Create current chart
                    st.subheader("Current Forecast")
                    if current_data is not None and len(current_data) > 0:
                        fig = px.line(
                            current_data, 
                            x='time', 
                            y='speed', 
                            title="Current Speed (mph)",
                            labels={"time": "Time", "speed": "Speed (mph)"}
                        )
                        
                        # Add danger zone for strong currents
                        strong_current_threshold = 2.3  # mph (2.0 knots converted to mph)
                        fig.add_shape(
                            type="rect",
                            x0=current_data['time'].min(),
                            x1=current_data['time'].max(),
                            y0=strong_current_threshold,
                            y1=max(current_data['speed'].max() + 0.5, strong_current_threshold + 1),
                            fillcolor="rgba(255, 0, 0, 0.2)",
                            line=dict(width=0),
                            layer="below"
                        )
                        fig.add_annotation(
                            x=current_data['time'].iloc[len(current_data)//2],
                            y=strong_current_threshold + 0.25,
                            text="Strong Current",
                            showarrow=False,
                            font=dict(color="red")
                        )
                        
                        # Improve appearance
                        fig.update_layout(
                            height=300,
                            margin=dict(l=20, r=20, t=40, b=20)
                        )
                        st.plotly_chart(fig, use_container_width=True)
                    else:
                        st.error("Current data not available")
            
            # Display hourly forecast in a table
            st.subheader("All Hours Forecast")
            if recommendations:
                # Create summary hourly table
                hours = []
                for r in recommendations:
                    start_hour = int(r['start_time'].split(':')[0])
                    hours.append({
                        'Hour': f"{start_hour:02d}:00 - {start_hour+1:02d}:00",
                        'Rating': r['rating'].title(),
                        'Tide': f"{r['tide_height']}ft ({r['tide_status']})",
                        'Current': f"{r['current_speed']} mph ({r['current_direction']})",
                        'Wind': f"{r['wind_speed']} mph ({r['wind_direction']})",
                        'Ferry': r['ferry_status']
                    })
                
                # Create DataFrame for the table
                hourly_df = pd.DataFrame(hours)
                
                # Create styled table with colors based on rating
                def color_rating(val):
                    color_map = {
                        'Optimal': f'background-color: {OPTIMAL_COLOR}; color: white',
                        'Acceptable': f'background-color: {ACCEPTABLE_COLOR}; color: white',
                        'Not Recommended': f'background-color: {NOT_RECOMMENDED_COLOR}; color: white'
                    }
                    return color_map.get(val, '')
                
                styled_hourly = hourly_df.style.map(
                    color_rating, subset=['Rating']
                )
                
                st.dataframe(styled_hourly, use_container_width=True)
            else:
                st.error("Hourly forecast data not available")
            
# Ferry schedule section removed as per user request
                
        except Exception as e:
            st.error(f"Error loading data: {str(e)}")
            st.info("Please try refreshing the page or selecting a different date.")

else:  # Weekly Overview
    st.header("Weekly Kayak Launch Overview")
    
    # Add refresh button for weekly view
    if st.button("Refresh Weekly Data", key="refresh_weekly_button"):
        st.rerun()
    
    # Create tabs for different aspects
    tab1, tab2, tab3 = st.tabs(["Launch Quality", "Tide Overview", "Weather Trends"])
    
    # Try to load data for the week
    with st.spinner("Fetching weekly data..."):
        try:
            # Prepare containers for weekly data
            weekly_tide_data = []
            weekly_current_data = []
            weekly_recommendations = []
            
            # Fetch data for each day in the week
            for date in dates_to_fetch:
                # Get data from APIs for this date
                tide_data = get_tide_data(date)
                current_data = get_current_data(date)
                ferry_data = get_ferry_schedule(date)
                weather_data = get_weather_data(date)
                
                # Get sunrise and sunset times for this date
                sun_times = get_sun_times(date)
                
                # Store tide and current data for weekly overview
                if tide_data is not None:
                    tide_data['date'] = date
                    weekly_tide_data.append(tide_data)
                
                if current_data is not None:
                    current_data['date'] = date
                    weekly_current_data.append(current_data)
                
                # Get daily recommendations
                daily_recommendations = get_launch_recommendations(
                    tide_data, current_data, ferry_data, weather_data
                )
                
                # Add date to each recommendation
                for rec in daily_recommendations:
                    rec['date'] = date
                
                weekly_recommendations.extend(daily_recommendations)
            
            # Combine weekly data
            if weekly_tide_data:
                weekly_tide_df = pd.concat(weekly_tide_data)
            else:
                weekly_tide_df = pd.DataFrame()
                
            if weekly_current_data:
                weekly_current_df = pd.concat(weekly_current_data)
            else:
                weekly_current_df = pd.DataFrame()
                
            weekly_rec_df = pd.DataFrame(weekly_recommendations)
            
            # Tab 1: Launch Quality Heatmap
            with tab1:
                if not weekly_rec_df.empty:
                    st.subheader("Launch Quality by Day and Hour")
                    
                    # Note about daylight hours
                    st.markdown("""
                    **Note:** Recommendations only show optimal times during daylight hours 
                    (30 minutes before sunrise to 30 minutes after sunset).
                    """)
                    
                    # Prepare data for heatmap
                    # Convert date to string for display
                    weekly_rec_df['date_str'] = weekly_rec_df['date'].apply(lambda d: format_date(d))
                    
                    # Extract hour from time
                    weekly_rec_df['hour'] = weekly_rec_df['start_time'].apply(
                        lambda t: int(t.split(':')[0])
                    )
                    
                    # Create a pivot table for the heatmap
                    # Map ratings to numerical values: optimal=2, acceptable=1, not_recommended=0
                    rating_map = {
                        'optimal': 2,
                        'acceptable': 1,
                        'not_recommended': 0
                    }
                    weekly_rec_df['rating_value'] = weekly_rec_df['rating'].map(rating_map)
                    
                    # Create pivot table
                    pivot_df = weekly_rec_df.pivot_table(
                        index='hour',
                        columns='date_str',
                        values='rating_value',
                        aggfunc='first'
                    )
                    
                    # Create custom colorscale
                    colors = [NOT_RECOMMENDED_COLOR, ACCEPTABLE_COLOR, OPTIMAL_COLOR]
                    colorscale = [[0, colors[0]], [0.5, colors[1]], [1, colors[2]]]
                    
                    # Create heatmap
                    fig = go.Figure(data=go.Heatmap(
                        z=pivot_df.values,
                        x=pivot_df.columns,
                        y=pivot_df.index,
                        colorscale=colorscale,
                        showscale=False,
                        hoverongaps=False,
                        text=[[
                            f"Hour: {hour}:00<br>Date: {date}<br>Rating: {['Not Recommended', 'Acceptable', 'Optimal'][int(rating)] if not pd.isna(rating) else 'No Data'}"
                            for date, rating in zip(pivot_df.columns, row)
                        ] for hour, row in zip(pivot_df.index, pivot_df.values)],
                        hoverinfo="text"
                    ))
                    
                    # Customize layout
                    fig.update_layout(
                        title="Launch Quality by Day and Hour",
                        xaxis_title="Date",
                        yaxis_title="Hour",
                        height=500
                    )
                    
                    # Update y-axis to show hours in 24-hour format
                    fig.update_yaxes(
                        tickvals=list(range(0, 24)),
                        ticktext=[f"{h:02d}:00" for h in range(0, 24)]
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Legend
                    st.markdown(f"""
                    **Legend:**
                    - <span style='color:{OPTIMAL_COLOR};'>■</span> Optimal
                    - <span style='color:{ACCEPTABLE_COLOR};'>■</span> Acceptable
                    - <span style='color:{NOT_RECOMMENDED_COLOR};'>■</span> Not Recommended
                    """, unsafe_allow_html=True)
                    
                    # Best days summary
                    st.subheader("Best Days This Week")
                    daily_quality = weekly_rec_df.groupby('date').apply(
                        lambda x: (x['rating'] == 'optimal').sum()
                    ).reset_index()
                    daily_quality.columns = ['date', 'optimal_hours']
                    daily_quality = daily_quality.sort_values('optimal_hours', ascending=False)
                    
                    if not daily_quality.empty:
                        # Display top 3 days with most optimal hours
                        for i, row in daily_quality.head(3).iterrows():
                            st.markdown(f"""
                            <div style="padding: 10px; border-radius: 5px; background-color: rgba(46, 204, 113, 0.1); margin-bottom: 10px;">
                                <h4 style="margin:0;">{format_date(row['date'])}: {row['optimal_hours']} optimal hours</h4>
                            </div>
                            """, unsafe_allow_html=True)
                    else:
                        st.info("No optimal launch windows found for the selected week.")
                else:
                    st.error("Weekly recommendation data not available")
            
            # Tab 2: Tide Overview
            with tab2:
                if not weekly_tide_df.empty:
                    st.subheader("Weekly Tide Overview")
                    
                    # Convert datetime to string for readability
                    weekly_tide_df['date_str'] = weekly_tide_df['date'].apply(lambda d: format_date(d))
                    weekly_tide_df['time_str'] = weekly_tide_df['time'].apply(
                        lambda t: t.strftime('%H:%M')
                    )
                    
                    # Create line chart for each day
                    fig = px.line(
                        weekly_tide_df,
                        x='time',
                        y='height',
                        color='date_str',
                        title="Tide Heights by Day (ft)",
                        labels={"time": "Time", "height": "Height (ft)", "date_str": "Date"}
                    )
                    
                    # Add high tide danger zone
                    high_tide_threshold = 10.0  # Assuming beach disappears around 10ft tide
                    fig.add_shape(
                        type="rect",
                        x0=weekly_tide_df['time'].min(),
                        x1=weekly_tide_df['time'].max(),
                        y0=high_tide_threshold,
                        y1=max(weekly_tide_df['height'].max() + 1, high_tide_threshold + 2),
                        fillcolor="rgba(255, 0, 0, 0.2)",
                        line=dict(width=0),
                        layer="below"
                    )
                    fig.add_annotation(
                        x=weekly_tide_df['time'].iloc[len(weekly_tide_df)//2],
                        y=high_tide_threshold + 0.5,
                        text="Beach Access Limited",
                        showarrow=False,
                        font=dict(color="red")
                    )
                    
                    # Improve appearance
                    fig.update_layout(
                        height=500,
                        margin=dict(l=20, r=20, t=40, b=20)
                    )
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Show high and low tide times for each day
                    st.subheader("High & Low Tides")
                    
                    # Group by date and find high/low points
                    tide_extremes = []
                    for date, group in weekly_tide_df.groupby('date'):
                        # Find high tides (local maxima)
                        high_tides = []
                        for i in range(1, len(group) - 1):
                            if group.iloc[i]['height'] > group.iloc[i-1]['height'] and group.iloc[i]['height'] > group.iloc[i+1]['height']:
                                high_tides.append({
                                    'date': date,
                                    'time': group.iloc[i]['time'],
                                    'height': group.iloc[i]['height'],
                                    'type': 'High'
                                })
                        
                        # Find low tides (local minima)
                        low_tides = []
                        for i in range(1, len(group) - 1):
                            if group.iloc[i]['height'] < group.iloc[i-1]['height'] and group.iloc[i]['height'] < group.iloc[i+1]['height']:
                                low_tides.append({
                                    'date': date,
                                    'time': group.iloc[i]['time'],
                                    'height': group.iloc[i]['height'],
                                    'type': 'Low'
                                })
                        
                        tide_extremes.extend(high_tides)
                        tide_extremes.extend(low_tides)
                    
                    # Convert to DataFrame and sort
                    extremes_df = pd.DataFrame(tide_extremes)
                    if not extremes_df.empty:
                        extremes_df['date_str'] = extremes_df['date'].apply(lambda d: format_date(d))
                        extremes_df['time_str'] = extremes_df['time'].apply(lambda t: t.strftime('%H:%M'))
                        extremes_df = extremes_df.sort_values(['date', 'time'])
                        
                        # Display as a table
                        display_df = extremes_df[['date_str', 'time_str', 'type', 'height']]
                        display_df.columns = ['Date', 'Time', 'Tide Type', 'Height (ft)']
                        
                        # Custom styling for high/low tides
                        def highlight_tide(val):
                            if val == 'High':
                                return 'background-color: #ffdddd'
                            elif val == 'Low':
                                return 'background-color: #ddffdd'
                            return ''
                        
                        styled_extremes = display_df.style.map(
                            highlight_tide, subset=['Tide Type']
                        )
                        
                        st.dataframe(styled_extremes, use_container_width=True)
                    else:
                        st.info("Could not determine tide extremes from the available data.")
                else:
                    st.error("Weekly tide data not available")
            
            # Tab 3: Weather Trends
            with tab3:
                if not weekly_rec_df.empty:
                    st.subheader("Weekly Weather Overview")
                    
                    # Extract weather data from recommendations
                    weather_df = weekly_rec_df[['date', 'hour', 'wind_speed', 'wind_direction']]
                    weather_df['date_str'] = weather_df['date'].apply(lambda d: format_date(d))
                    
                    # Create line chart for wind speed
                    fig = px.line(
                        weather_df,
                        x='hour',
                        y='wind_speed',
                        color='date_str',
                        title="Wind Speed by Day (mph)",
                        labels={"hour": "Hour", "wind_speed": "Wind Speed (mph)", "date_str": "Date"}
                    )
                    
                    # Add danger zone for strong winds
                    strong_wind_threshold = 15.0  # mph
                    fig.add_shape(
                        type="rect",
                        x0=weather_df['hour'].min(),
                        x1=weather_df['hour'].max(),
                        y0=strong_wind_threshold,
                        y1=max(weather_df['wind_speed'].max() + 2, strong_wind_threshold + 5),
                        fillcolor="rgba(255, 0, 0, 0.2)",
                        line=dict(width=0),
                        layer="below"
                    )
                    fig.add_annotation(
                        x=weather_df['hour'].iloc[len(weather_df)//2],
                        y=strong_wind_threshold + 2,
                        text="Strong Winds",
                        showarrow=False,
                        font=dict(color="red")
                    )
                    
                    # Update x-axis to show hours in 24-hour format
                    fig.update_xaxes(
                        tickvals=list(range(0, 24)),
                        ticktext=[f"{h:02d}:00" for h in range(0, 24)]
                    )
                    
                    # Improve appearance
                    fig.update_layout(
                        height=400,
                        margin=dict(l=20, r=20, t=40, b=20)
                    )
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Wind direction summary
                    st.subheader("Wind Direction Summary")
                    
                    # Get the predominant wind direction for each day
                    wind_summary = []
                    for date, group in weather_df.groupby('date'):
                        direction_counts = group['wind_direction'].value_counts()
                        predominant_direction = direction_counts.index[0]
                        avg_speed = group['wind_speed'].mean()
                        max_speed = group['wind_speed'].max()
                        
                        wind_summary.append({
                            'date': date,
                            'date_str': format_date(date),
                            'predominant_direction': predominant_direction,
                            'avg_speed': avg_speed,
                            'max_speed': max_speed
                        })
                    
                    wind_summary_df = pd.DataFrame(wind_summary)
                    
                    # Display as a table
                    if not wind_summary_df.empty:
                        display_df = wind_summary_df[['date_str', 'predominant_direction', 'avg_speed', 'max_speed']]
                        display_df.columns = ['Date', 'Predominant Direction', 'Avg Speed (mph)', 'Max Speed (mph)']
                        
                        # Custom styling for wind speed
                        def color_wind_speed(val):
                            if val > 15:
                                return 'color: red'
                            elif val > 10:
                                return 'color: orange'
                            return ''
                        
                        styled_wind = display_df.style.map(
                            color_wind_speed, subset=['Max Speed (mph)']
                        ).map(
                            color_wind_speed, subset=['Avg Speed (mph)']
                        )
                        
                        st.dataframe(styled_wind, use_container_width=True)
                    else:
                        st.info("Could not determine wind patterns from the available data.")
                else:
                    st.error("Weekly weather data not available")
        
        except Exception as e:
            st.error(f"Error loading weekly data: {str(e)}")
            st.info("Please try refreshing the page or selecting a different date range.")

# Add footer
st.markdown("---")
st.caption("Kayak Launch Assistant • Data refreshed: " + get_pacific_time().strftime("%m/%d/%Y %H:%M"))
