import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import folium
from streamlit_folium import folium_static
from streamlit_folium import st_folium
from huggingface_hub import hf_hub_download
import os

import os
st.sidebar.write("Current directory:", os.getcwd())
st.sidebar.write("Files:", os.listdir())
if os.path.exists("pages"):
    st.sidebar.write("Pages folder contents:", os.listdir("pages"))
else:
    st.sidebar.error("❌ Pages folder not found!")

# Page configuration
st.set_page_config(
    page_title="Traffic Analysis",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("Bangkok Traffic Analysis Dashboard")
st.sidebar.success("Select a page above.")

# ==================================================
# HUGGING FACE CONFIG
# ==================================================
HF_REPO = "Ayemm/BKK_Bus_Data"

# ==================================================
# REMOTE DATA LOADER
# ==================================================
@st.cache_data(show_spinner=False)
def load_csv_from_hf(
    repo_id: str,
    filename: str,
    required_cols=None,
    parse_dates=None
) -> pd.DataFrame | None:
    try:
        local_path = hf_hub_download(
            repo_id=repo_id,
            filename=filename,
            repo_type="dataset"
        )

        df = pd.read_csv(local_path, parse_dates=parse_dates)

        if required_cols:
            missing = [c for c in required_cols if c not in df.columns]
            if missing:
                st.error(f"Missing columns {missing} in {filename}")
                return None

        st.success(f"✅ Loaded {len(df):,} rows from HF: {filename}")
        return df

    except Exception as e:
        st.error(f"❌ HF load failed ({filename}): {e}")
        return None


# ==================================================
# LOCAL FALLBACK LOADERS
# ==================================================
@st.cache_data(show_spinner=False)
def load_local_csv(path, parse_dates=None):
    if os.path.exists(path):
        try:
            df = pd.read_csv(path, parse_dates=parse_dates)
            st.success(f"✅ Loaded {len(df):,} rows from {path}")
            return df
        except Exception as e:
            st.error(f"❌ Error loading {path}: {e}")
    return None


# ==================================================
# MAIN DATA LOADER (FIXED)
# ==================================================
def load_data():

    traffic_df = load_csv_from_hf(
        HF_REPO,
        "traffic.csv",
        required_cols=["lat", "lon", "speed", "timestamp"],
        parse_dates=["timestamp"]
    )
    if traffic_df is None:
        traffic_df = load_local_csv("data/traffic.csv", parse_dates=["timestamp"])

    congestion_df = load_csv_from_hf(
        HF_REPO,
        "congestion_zones.csv",
        required_cols=["center_lat", "center_lon", "severity", "avg_speed"]
    )
    if congestion_df is None:
        congestion_df = load_local_csv("data/congestion.csv")

    bus_routes_df = load_csv_from_hf(HF_REPO, "cleaned_bus_routes_file.csv")
    if bus_routes_df is None:
        bus_routes_df = load_local_csv("data/bangkok_bus_routes.csv")

    bus_stops_df = load_csv_from_hf(HF_REPO, "cleaned_bus_stops_file.csv")
    if bus_stops_df is None:
        bus_stops_df = load_local_csv("data/cleaned_bus_stops_file.csv")

    route_summary_df = load_csv_from_hf(HF_REPO, "predicted_route_times_summary.csv")
    if route_summary_df is None:
        route_summary_df = load_local_csv("data/predicted_route_times_summary.csv")

    return (
        traffic_df,
        congestion_df,
        bus_routes_df,
        bus_stops_df,
        route_summary_df,
    )

# ==================================================
# LOAD DATA
# ==================================================
with st.spinner("Loading data..."):
    traffic_df, congestion_df, bus_routes_df, bus_stops_df, route_summary_df = load_data()

if traffic_df is None or congestion_df is None:
    st.error("❌ Required datasets could not be loaded.")
    st.stop()

# Main content
tab1, tab2, tab3 = st.tabs([
    "🗺️ Geographic Analysis", 
    "⏰ Temporal Patterns", 
    "📊 Model Insights",
])

# ============================================================================
# TAB 1: GEOGRAPHIC ANALYSIS
# ============================================================================
with tab1:
    st.header("Geographic Analysis")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("Traffic Speed Heatmap")
        
        # Sample data for performance
        sample_size = min(10000, len(traffic_df))
        df_sample = traffic_df.sample(n=sample_size, random_state=42)
        
        # Create map centered on Bangkok
        bangkok_center = [13.7563, 100.5018]
        m = folium.Map(location=bangkok_center, zoom_start=11, tiles='OpenStreetMap')
        
        # Add congestion zones
        for _, zone in congestion_df.iterrows():
            color = {'Critical': 'red', 'High': 'orange', 'Medium': 'yellow', 'Low': 'green'}.get(zone['severity'], 'gray')
            folium.Circle(
                location=[zone['center_lat'], zone['center_lon']],
                radius=500,
                popup=f"Zone {zone['zone_id']}<br>Severity: {zone['severity']}<br>Avg Speed: {zone['avg_speed']:.1f} km/h",
                color=color,
                fill=True,
                fillOpacity=0.3
            ).add_to(m)
        
        # Add traffic points (color by speed)
        for _, row in df_sample.iterrows():
            speed = row['speed']
            if speed < 20:
                color = 'red'
            elif speed < 40:
                color = 'orange'
            elif speed < 60:
                color = 'yellow'
            else:
                color = 'green'
            
            folium.CircleMarker(
                location=[row['lat'], row['lon']],
                radius=2,
                color=color,
                fill=True,
                fillOpacity=0.6,
                popup=f"Speed: {speed:.1f} km/h"
            ).add_to(m)

        st_folium(m, width=800, height=600)
        #folium_static(m, width=800, height=600)
    
    with col2:
        st.subheader("Congestion Zones")
        st.dataframe(
            congestion_df[['zone_id', 'severity', 'avg_speed', 'size']].sort_values('severity'),
            height=300
        )
        
        st.subheader("Speed by Distance from Center")
        if 'distance_from_center' in traffic_df.columns:
            fig = px.scatter(
                traffic_df.sample(n=min(5000, len(traffic_df))),
                x='distance_from_center',
                y='speed',
                color='speed',
                title="Speed vs Distance from Center",
                labels={'distance_from_center': 'Distance from Center', 'speed': 'Speed (km/h)'},
                color_continuous_scale='RdYlGn'
            )
            st.plotly_chart(fig, width="stretch")

# ============================================================================
# TAB 2: TEMPORAL PATTERNS
# ============================================================================
with tab2:
    st.header("Temporal Traffic Patterns")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Traffic by Hour of Day")
        if 'hour' in traffic_df.columns:
            hourly = traffic_df.groupby('hour').agg({
                'speed': ['mean', 'count']
            }).reset_index()
            hourly.columns = ['hour', 'avg_speed', 'count']
            
            fig = make_subplots(specs=[[{"secondary_y": True}]])
            fig.add_trace(
                go.Bar(x=hourly['hour'], y=hourly['count'], name='Traffic Volume', marker_color='lightblue'),
                secondary_y=False
            )
            fig.add_trace(
                go.Scatter(x=hourly['hour'], y=hourly['avg_speed'], name='Avg Speed', 
                          mode='lines+markers', line=dict(color='red', width=3)),
                secondary_y=True
            )
            fig.update_xaxes(title_text="Hour of Day")
            fig.update_yaxes(title_text="Traffic Volume", secondary_y=False)
            fig.update_yaxes(title_text="Average Speed (km/h)", secondary_y=True)
            fig.update_layout(title="Traffic Volume and Speed by Hour")
            st.plotly_chart(fig, width="stretch")
    
    with col2:
        st.subheader("Traffic by Day of Week")
        if 'day_of_week' in traffic_df.columns:
            days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
            daily = traffic_df.groupby('day_of_week')['speed'].mean().reset_index()
            daily['day_name'] = daily['day_of_week'].apply(lambda x: days[x])
            
            fig = px.bar(
                daily,
                x='day_name',
                y='speed',
                title="Average Speed by Day of Week",
                labels={'day_name': 'Day', 'speed': 'Avg Speed (km/h)'},
                color='speed',
                color_continuous_scale='RdYlGn'
            )
            st.plotly_chart(fig, width="stretch")


# ============================================================================
# TAB 3: MODEL INSIGHTS
# ============================================================================
with tab3:
    st.header("Model Insights & Features")
    
    # Feature correlation
    st.subheader("Feature Correlations with Speed")
    
    feature_cols = ['hour', 'day_of_week', 'is_weekend', 'is_rush_hour', 
                   'distance_from_center', 'near_congestion', 'distance_to_congestion']
    available_features = [col for col in feature_cols if col in traffic_df.columns]
    
    if available_features:
        correlations = traffic_df[available_features + ['speed']].corr()['speed'].drop('speed').sort_values()
        
        fig = px.bar(
            x=correlations.values,
            y=correlations.index,
            orientation='h',
            title="Feature Correlation with Speed",
            labels={'x': 'Correlation', 'y': 'Feature'},
            color=correlations.values,
            color_continuous_scale='RdYlGn'
        )
        st.plotly_chart(fig, width="stretch")
    
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Feature Importance Preview")
        st.info("""
        **Key Features for Traffic Prediction:**
        - 🕐 Temporal: hour, day_of_week, is_rush_hour
        - 📍 Spatial: lat, lon, distance_from_center
        - 🚦 Congestion: near_congestion, congestion_severity
        - 📊 Historical: location_avg_speed, hour_avg_speed
        """)
    
    with col2:
        st.subheader("Data Quality Metrics")
        st.metric("Missing Values", f"{traffic_df.isnull().sum().sum()}")
        st.metric("Duplicate Records", f"{traffic_df.duplicated().sum()}")
        if 'speed' in traffic_df.columns:
            st.metric("Speed Outliers (>120 km/h)", f"{(traffic_df['speed'] > 120).sum()}")


# Footer
st.markdown("---")
st.markdown("""
    <div style='text-align: center; color: gray;'>
        <p>Bangkok Traffic Analysis Dashboard | Built with Streamlit & Plotly</p>
    </div>
""", unsafe_allow_html=True)