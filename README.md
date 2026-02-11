# BKK Traffic Route Analytics Dashboard

An interactive Streamlit web application designed to visualize, analyze, and interpret Bangkok bus route and traffic data.
The app automatically loads datasets (via Hugging Face Hub) and provides multi-tab visual analytics including route maps, distance summaries, correlation heatmaps, and route segment analysis.

 Features
- Automated Data Loading
- Route-Level Analytics
- Data Summaries
- Correlation Insights
- Segment-by-Segment Analysis
- Robust UI/UX Design
Quick Start

Create a virtual environment and install requirements:

python -m venv .venv && source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install --upgrade pip
pip install -r requirements.txt


Run the dashboard:

streamlit run app.py


Open in browser:

http://127.0.0.1:8501

Dataset Structure

If running locally with manual dataset:

data/
  routes.csv
  segments.csv
  gps_data.csv


Or configure Hugging Face dataset loader inside the app (default).
