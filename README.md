# BKK Traffic Route Analytics Dashboard

An interactive Streamlit web application designed to visualize, analyze, and interpret Bangkok bus route and traffic data.
The app automatically loads datasets (via Hugging Face Hub) and provides multi-tab visual analytics including route maps, distance summaries, correlation heatmaps, and route segment analysis.

 ## Features
- Automated Data Loading
- Route-Level Analytics
- Data Summaries
- Correlation Insights
- Segment-by-Segment Analysis
- Robust UI/UX Design
  
## Quick Start
Create a virtual environment and install requirements:
```
python -m venv .venv && source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install --upgrade pip
pip install -r requirements.txt

```
Run the dashboard:
```
streamlit run app.py
```
Open in browser:
http://127.0.0.1:8501

Dataset Structure

If running locally with manual dataset:
```
data/
  routes.csv
  segments.csv
  gps_data.csv
```
Or configure Hugging Face dataset loader inside the app (default).

## Dashboard
<img alt="Screenshot from 2026-02-11 18-24-41" src="https://github.com/user-attachments/assets/f9782860-eb0d-4593-8ec7-8938568f6334" width="48%"/> <img alt="Screenshot from 2026-02-11 18-25-03" src="https://github.com/user-attachments/assets/8d0e4f26-76b7-4231-a024-f4fc0313e7d4" width="48%"/>

<img alt="Screenshot from 2026-02-11 18-25-14" src="https://github.com/user-attachments/assets/9b1a9cd2-c4f6-4350-8eed-0c5644c2db5a" width="48%"/> <img alt="Screenshot from 2026-02-11 18-25-10" src="https://github.com/user-attachments/assets/f0d63228-1117-4c87-a5d2-d7af339d6991" width="48%"/>
