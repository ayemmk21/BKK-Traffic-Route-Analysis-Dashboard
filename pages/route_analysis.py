import streamlit as st

st.set_page_config(page_title="Route Analysis", layout="wide")

st.title("Route Analysis - Debug Mode")

# Test imports
try:
    import os, ast, pickle, colorsys, hashlib
    from pathlib import Path
    from datetime import datetime
    st.success("Basic imports OK")
except Exception as e:
    st.error(f"Basic imports failed: {e}")
    st.stop()

try:
    from huggingface_hub import hf_hub_download
    import numpy as np
    import pandas as pd
    st.success("Data library imports OK")
except Exception as e:
    st.error(f"Data imports failed: {e}")
    st.stop()

try:
    import plotly.express as px
    import plotly.graph_objects as go
    import folium
    from folium.plugins import HeatMap
    from streamlit_folium import st_folium
    import requests
    st.success("Visualization imports OK")
except Exception as e:
    st.error(f"Visualization imports failed: {e}")
    st.stop()

# Test data loading
st.subheader("Testing Data Loading...")

DATA_REPO = "Ayemm/BKK_Bus_Data"

@st.cache_data(show_spinner=False)
def load_csv_hf(repo_id: str, filename: str):
    try:
        path = hf_hub_download(
            repo_id=repo_id,
            filename=filename,
            repo_type="dataset"
        )
        df = pd.read_csv(path)
        return df
    except Exception as e:
        st.error(f"Failed to load {filename}: {e}")
        return None

# Test each file
with st.spinner("Loading routes..."):
    routes = load_csv_hf(DATA_REPO, "cleaned_bus_routes_file.csv")
    if routes is not None:
        st.success(f"Routes loaded: {len(routes)} rows")
    else:
        st.warning("Routes failed to load")

with st.spinner("Loading traffic..."):
    traffic = load_csv_hf(DATA_REPO, "traffic.csv")
    if traffic is not None:
        st.success(f"Traffic loaded: {len(traffic)} rows")
    else:
        st.warning("Traffic failed to load")

with st.spinner("Loading congestion zones..."):
    zones = load_csv_hf(DATA_REPO, "congestion_zones.csv")
    if zones is not None:
        st.success(f"Zones loaded: {len(zones)} rows")
    else:
        st.warning("Zones failed to load")

with st.spinner("Loading stops..."):
    stops = load_csv_hf(DATA_REPO, "cleaned_bus_stops_file.csv")
    if stops is not None:
        st.success(f"Stops loaded: {len(stops)} rows")
    else:
        st.warning("Stops failed to load")

# Test model loading (this is likely the problem)
st.subheader("Testing Model Loading...")

@st.cache_resource(show_spinner=False)
def load_models_from_hf():
    try:
        route_models_path = hf_hub_download(
            DATA_REPO,
            "route_models.pkl",
            repo_type="dataset"
        )
        feature_columns_path = hf_hub_download(
            DATA_REPO,
            "feature_columns.pkl",
            repo_type="dataset"
        )

        with open(route_models_path, "rb") as f:
            route_models = pickle.load(f)

        with open(feature_columns_path, "rb") as f:
            feature_columns = pickle.load(f)

        return route_models, feature_columns

    except Exception as e:
        st.error(f"Model loading failed: {e}")
        return {}, {}

with st.spinner("Loading models (this may take a while)..."):
    route_models, feature_columns = load_models_from_hf()
    
    if route_models:
        st.success(f"Models loaded: {len(route_models)} routes")
    else:
        st.warning("No models loaded - predictions will be disabled")

st.success("All components loaded successfully!")
st.info("If you see this message, we can now add back the full analysis code.")