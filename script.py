import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import random
import uuid
import time
import json
import requests
import base64
from io import BytesIO
import re
from PIL import Image
from wordcloud import WordCloud
from collections import Counter
import networkx as nx
from supabase import create_client, Client

# Import AgGrid for Airtable-like grid
from st_aggrid import AgGrid, GridOptionsBuilder, JsCode, GridUpdateMode
# Import extra components
from streamlit_extras.colored_header import colored_header
from streamlit_extras.metric_cards import style_metric_cards
from streamlit_extras.switch_page_button import switch_page
from streamlit_extras.chart_container import chart_container
from streamlit_lottie import st_lottie
from streamlit_elements import elements, dashboard, mui, html, lazy, sync
from contextlib import contextmanager

# -----------------------------
# PAGE CONFIGURATION & STYLING
# -----------------------------
st.set_page_config(
    page_title="Premium Chat Analytics",
    page_icon="💬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load custom CSS
def load_css():
    css = """
    <style>
        /* Main container styling */
        .main {
            background-color: #f9fafb;
            background-image: 
                radial-gradient(at 47% 33%, hsla(162, 77%, 40%, 0.04) 0, transparent 59%), 
                radial-gradient(at 82% 65%, hsla(218, 39%, 11%, 0.08) 0, transparent 55%);
        }
        
        /* Dark mode adjustments */
        .dark-mode .main {
            background-color: #0e1117;
            background-image: 
                radial-gradient(at 47% 33%, hsla(162, 77%, 40%, 0.08) 0, transparent 59%), 
                radial-gradient(at 82% 65%, hsla(218, 39%, 11%, 0.12) 0, transparent 55%);
        }
        
        /* Card styling */
        .css-1r6slb0, .css-1y4p8pa {
            border-radius: 10px;
            border: 1px solid rgba(49, 51, 63, 0.1);
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
            padding: 1rem;
            margin-bottom: 1rem;
            background-color: rgba(255, 255, 255, 0.8);
            backdrop-filter: blur(10px);
        }
        
        .dark-mode .css-1r6slb0, .dark-mode .css-1y4p8pa {
            background-color: rgba(17, 25, 40, 0.8);
            border: 1px solid rgba(255, 255, 255, 0.1);
        }
        
        /* Metric card styling */
        .metric-card {
            background-color: white;
            border-radius: 10px;
            padding: 1.5rem;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
            transition: transform 0.3s ease, box-shadow 0.3s ease;
            height: 100%;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
        }
        
        .dark-mode .metric-card {
            background-color: rgba(17, 25, 40, 0.9);
            border: 1px solid rgba(255, 255, 255, 0.1);
        }
        
        .metric-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
        }
        
        /* Tabs styling */
        .stTabs [data-baseweb="tab-list"] {
            gap: 8px;
            border-radius: 10px;
            padding: 0.5rem;
            background-color: rgba(255, 255, 255, 0.8);
            backdrop-filter: blur(10px);
        }
        
        .dark-mode .stTabs [data-baseweb="tab-list"] {
            background-color: rgba(17, 25, 40, 0.8);
        }
        
        .stTabs [data-baseweb="tab"] {
            height: 50px;
            white-space: pre-wrap;
            border-radius: 8px;
            gap: 1px;
            padding: 10px 16px;
            font-weight: 500;
            transition: all 0.2s ease;
        }
        
        .stTabs [aria-selected="true"] {
            background-color: rgba(28, 131, 225, 0.1);
            color: #1c83e1;
            font-weight: 600;
        }
        
        /* Button styling */
        .stButton>button {
            border-radius: 8px;
            padding: 0.5rem 1rem;
            font-weight: 500;
            transition: all 0.2s ease;
            border: none;
            background-color: #1c83e1;
            color: white;
        }
        
        .stButton>button:hover {
            background-color: #1665b0;
            transform: translateY(-2px);
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
        }
        
        /* Sidebar styling */
        .css-1d391kg, .css-163ttbj {
            background-color: rgba(255, 255, 255, 0.8);
            backdrop-filter: blur(10px);
        }
        
        .dark-mode .css-1d391kg, .dark-mode .css-163ttbj {
            background-color: rgba(17, 25, 40, 0.8);
        }
        
        /* Progress bar */
        .stProgress > div > div {
            background-color: #1c83e1;
            border-radius: 10px;
        }
        
        /* Tooltip */
        .tooltip {
            position: relative;
            display: inline-block;
        }
        
        .tooltip .tooltiptext {
            visibility: hidden;
            width: 120px;
            background-color: rgba(0, 0, 0, 0.8);
            color: #fff;
            text-align: center;
            border-radius: 6px;
            padding: 5px;
            position: absolute;
            z-index: 1;
            bottom: 125%;
            left: 50%;
            margin-left: -60px;
            opacity: 0;
            transition: opacity 0.3s;
        }
        
        .tooltip:hover .tooltiptext {
            visibility: visible;
            opacity: 1;
        }
        
        /* Custom scrollbar */
        ::-webkit-scrollbar {
            width: 8px;
            height: 8px;
        }
        
        ::-webkit-scrollbar-track {
            background: rgba(0, 0, 0, 0.05);
            border-radius: 10px;
        }
        
        ::-webkit-scrollbar-thumb {
            background: rgba(0, 0, 0, 0.2);
            border-radius: 10px;
        }
        
        ::-webkit-scrollbar-thumb:hover {
            background: rgba(0, 0, 0, 0.3);
        }
        
        /* AgGrid customizations */
        .ag-theme-alpine, .ag-theme-alpine-dark {
            --ag-border-radius: 10px;
            --ag-border-color: rgba(49, 51, 63, 0.1);
            --ag-row-hover-color: rgba(28, 131, 225, 0.1);
            --ag-selected-row-background-color: rgba(28, 131, 225, 0.2);
            --ag-header-background-color: rgba(28, 131, 225, 0.1);
            --ag-odd-row-background-color: rgba(0, 0, 0, 0.02);
            --ag-header-column-separator-display: none;
            --ag-header-column-resize-handle-display: block;
        }
        
        .dark-mode .ag-theme-alpine, .dark-mode .ag-theme-alpine-dark {
            --ag-background-color: rgba(17, 25, 40, 0.8);
            --ag-border-color: rgba(255, 255, 255, 0.1);
            --ag-header-background-color: rgba(28, 131, 225, 0.2);
            --ag-odd-row-background-color: rgba(255, 255, 255, 0.03);
        }
        
        /* Animation classes */
        .fade-in {
            animation: fadeIn 0.5s ease-in-out;
        }
        
        @keyframes fadeIn {
            from { opacity: 0; }
            to { opacity: 1; }
        }
        
        .slide-up {
            animation: slideUp 0.5s ease-in-out;
        }
        
        @keyframes slideUp {
            from { transform: translateY(20px); opacity: 0; }
            to { transform: translateY(0); opacity: 1; }
        }
        
        /* Chat message styling */
        .chat-message {
            padding: 1rem;
            border-radius: 10px;
            margin-bottom: 1rem;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
            position: relative;
            transition: transform 0.2s ease;
        }
        
        .chat-message:hover {
            transform: translateY(-2px);
        }
        
        .user-message {
            background-color: rgba(28, 131, 225, 0.1);
            margin-right: 2rem;
            margin-left: 0.5rem;
        }
        
        .bot-message {
            background-color: rgba(255, 255, 255, 0.8);
            margin-left: 2rem;
            margin-right: 0.5rem;
        }
        
        .dark-mode .bot-message {
            background-color: rgba(17, 25, 40, 0.8);
        }
        
        /* Loading animation */
        .loading-spinner {
            display: inline-block;
            width: 50px;
            height: 50px;
            border: 3px solid rgba(0, 0, 0, 0.1);
            border-radius: 50%;
            border-top-color: #1c83e1;
            animation: spin 1s ease-in-out infinite;
        }
        
        @keyframes spin {
            to { transform: rotate(360deg); }
        }
        
        /* Custom header */
        .custom-header {
            background: linear-gradient(90deg, #4b6cb7 0%, #182848 100%);
            padding: 2rem;
            border-radius: 10px;
            margin-bottom: 2rem;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
            text-align: center;
            position: relative;
            overflow: hidden;
        }
        
        .custom-header::before {
            content: "";
            position: absolute;
            top: -50%;
            left: -50%;
            width: 200%;
            height: 200%;
            background: radial-gradient(circle, rgba(255, 255, 255, 0.1) 0%, transparent 80%);
            animation: pulse 15s infinite;
        }
        
        @keyframes pulse {
            0% { transform: scale(1); opacity: 0.3; }
            50% { transform: scale(1.05); opacity: 0.5; }
            100% { transform: scale(1); opacity: 0.3; }
        }
        
        .header-content {
            position: relative;
            z-index: 1;
        }
        
        /* Sentiment indicators */
        .sentiment-indicator {
            display: inline-block;
            width: 12px;
            height: 12px;
            border-radius: 50%;
            margin-right: 5px;
        }
        
        .sentiment-positive {
            background-color: #4CAF50;
        }
        
        .sentiment-neutral {
            background-color: #FFC107;
        }
        
        .sentiment-negative {
            background-color: #F44336;
        }
        
        /* Tooltip for charts */
        .tooltip-chart {
            background-color: rgba(0, 0, 0, 0.8);
            color: white;
            padding: 10px;
            border-radius: 5px;
            font-size: 12px;
            pointer-events: none;
        }
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)

# Load SVG icons
def load_svg_icons():
    icons = {
        "dashboard": """<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="7" height="9"/><rect x="14" y="3" width="7" height="5"/><rect x="14" y="12" width="7" height="9"/><rect x="3" y="16" width="7" height="5"/></svg>""",
        "chat": """<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/></svg>""",
        "analytics": """<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="20" x2="18" y2="10"/><line x1="12" y1="20" x2="12" y2="4"/><line x1="6" y1="20" x2="6" y2="14"/></svg>""",
        "settings": """<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"/></svg>""",
        "refresh": """<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M23 4v6h-6"/><path d="M1 20v-6h6"/><path d="M3.51 9a9 9 0 0 1 14.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0 0 20.49 15"/></svg>""",
        "filter": """<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polygon points="22 3 2 3 10 12.46 10 19 14 21 14 12.46 22 3"/></svg>""",
        "download": """<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/></svg>""",
        "search": """<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>""",
        "user": """<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>""",
        "bot": """<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="11" width="18" height="10" rx="2"/><circle cx="12" cy="5" r="2"/><path d="M12 7v4"/><line x1="8" y1="16" x2="8" y2="16"/><line x1="16" y1="16" x2="16" y2="16"/></svg>""",
        "sentiment_positive": """<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#4CAF50" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><path d="M8 14s1.5 2 4 2 4-2 4-2"/><line x1="9" y1="9" x2="9.01" y2="9"/><line x1="15" y1="9" x2="15.01" y2="9"/></svg>""",
        "sentiment_neutral": """<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#FFC107" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><line x1="8" y1="15" x2="16" y2="15"/><line x1="9" y1="9" x2="9.01" y2="9"/><line x1="15" y1="9" x2="15.01" y2="9"/></svg>""",
        "sentiment_negative": """<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#F44336" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><path d="M16 16s-1.5-2-4-2-4 2-4 2"/><line x1="9" y1="9" x2="9.01" y2="9"/><line x1="15" y1="9" x2="15.01" y2="9"/></svg>""",
        "time": """<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>""",
        "message": """<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 11.5a8.38 8.38 0 0 1-.9 3.8 8.5 8.5 0 0 1-7.6 4.7 8.38 8.38 0 0 1-3.8-.9L3 21l1.9-5.7a8.38 8.38 0 0 1-.9-3.8 8.5 8.5 0 0 1 4.7-7.6 8.38 8.38 0 0 1 3.8-.9h.5a8.48 8.48 0 0 1 8 8v.5z"/></svg>""",
        "3d": """<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 3l8 4.5v9L12 21l-8-4.5v-9L12 3"/><line x1="12" y1="12" x2="12" y2="21"/><path d="M12 12l8-4.5"/><path d="M12 12l-8-4.5"/></svg>""",
        "network": """<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="18" cy="5" r="3"/><circle cx="6" cy="12" r="3"/><circle cx="18" cy="19" r="3"/><line x1="8.59" y1="13.51" x2="15.42" y2="17.49"/><line x1="15.41" y1="6.51" x2="8.59" y2="10.49"/></svg>""",
        "calendar": """<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="4" width="18" height="18" rx="2" ry="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/></svg>""",
        "globe": """<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><line x1="2" y1="12" x2="22" y2="12"/><path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"/></svg>""",
        "tag": """<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M20.59 13.41l-7.17 7.17a2 2 0 0 1-2.83 0L2 12V2h10l8.59 8.59a2 2 0 0 1 0 2.82z"/><line x1="7" y1="7" x2="7.01" y2="7"/></svg>""",
        "topic": """<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M2 3h6a4 4 0 0 1 4 4v14a3 3 0 0 0-3-3H2z"/><path d="M22 3h-6a4 4 0 0 0-4 4v14a3 3 0 0 1 3-3h7z"/></svg>""",
        "intent": """<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polygon points="22 3 2 3 10 12.46 10 19 14 21 14 12.46 22 3"/></svg>""",
        "region": """<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 22s-8-4.5-8-11.8A8 8 0 0 1 12 2a8 8 0 0 1 8 8.2c0 7.3-8 11.8-8 11.8z"/><circle cx="12" cy="10" r="3"/></svg>"""
    }
    return icons

# Load animation JSON
@st.cache_data
def load_lottie_animation(url):
    try:
        r = requests.get(url)
        if r.status_code != 200:
            return None
        return r.json()
    except:
        return None

# -----------------------------
# CONFIGURATION & AUTO-REFRESH
# -----------------------------
# Configure Supabase credentials
SUPABASE_URL = "https://svjindgyokubrdxesdlp.supabase.co"
SUPABASE_KEY = (
"eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InN2amluZGd5b2t1YnJkeGVzZGxwIiwicm9sZSI6ImFub24iLCJpYXQiOjE3Mzk1OTM2MTQsImV4cCI6MjA1NTE2OTYxNH0.P_giMWMPtnBT4Ca7AsHCcuNtoV0OWgsY6VHTqDqh0Sw"
)

# -----------------------------
# DATA FUNCTIONS
# -----------------------------
@st.cache_data(ttl=300)
def fetch_chat_logs() -> pd.DataFrame:
    """
    Fetch chat logs from Supabase.
    Returns a DataFrame. If no data is available, an empty DataFrame is returned.
    """
    try:
        with st.spinner("Fetching data from Supabase..."):
            supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
            response = supabase.table("chat_logs").select("*").execute()
            data = response.data
            if not data:
                return pd.DataFrame()
            df = pd.DataFrame(data)
            if 'timestamp' in df.columns:
                df['timestamp'] = pd.to_datetime(df['timestamp'])
            return df
    except Exception as e:
        st.error(f"Error fetching data: {e}")
        return pd.DataFrame()

def generate_random_data(n=100) -> pd.DataFrame:
    """
    Generate random chat log data for demonstration with more realistic patterns.
    """
    # Create more realistic conversation patterns
    num_conversations = max(5, n // 15)
    conv_ids = [str(uuid.uuid4()) for _ in range(num_conversations)]
    
    # Create user profiles with characteristics
    user_profiles = {
        'user1': {'verbosity': 'high', 'sentiment_bias': 0.3, 'response_time_factor': 0.8, 'avatar': 'https://randomuser.me/api/portraits/men/32.jpg'},
        'user2': {'verbosity': 'medium', 'sentiment_bias': -0.2, 'response_time_factor': 1.2, 'avatar': 'https://randomuser.me/api/portraits/women/44.jpg'},
        'user3': {'verbosity': 'low', 'sentiment_bias': 0.1, 'response_time_factor': 1.0, 'avatar': 'https://randomuser.me/api/portraits/men/67.jpg'},
        'user4': {'verbosity': 'high', 'sentiment_bias': -0.4, 'response_time_factor': 0.7, 'avatar': 'https://randomuser.me/api/portraits/women/33.jpg'},
        'user5': {'verbosity': 'medium', 'sentiment_bias': 0.5, 'response_time_factor': 1.1, 'avatar': 'https://randomuser.me/api/portraits/men/91.jpg'},
    }
    
    # Common topics and phrases
    topics = ['account issues', 'product inquiry', 'technical support', 'billing questions', 'feature requests']
    
    # Topic images from Unsplash
    topic_images = {
        'account issues': 'https://images.unsplash.com/photo-1573496359142-b8d87734a5a2?ixlib=rb-1.2.1&auto=format&fit=crop&w=300&q=80',
        'product inquiry': 'https://images.unsplash.com/photo-1542744095-fcf48d80b0fd?ixlib=rb-1.2.1&auto=format&fit=crop&w=300&q=80',
        'technical support': 'https://images.unsplash.com/photo-1581092921461-7031e4bfb83a?ixlib=rb-1.2.1&auto=format&fit=crop&w=300&q=80',
        'billing questions': 'https://images.unsplash.com/photo-1554224155-6726b3ff858f?ixlib=rb-1.2.1&auto=format&fit=crop&w=300&q=80',
        'feature requests': 'https://images.unsplash.com/photo-1596079890744-c1a0462d0975?ixlib=rb-1.2.1&auto=format&fit=crop&w=300&q=80'
    }
    
    # Generate data with patterns
    data = []
    for _ in range(n):
        conv_id = random.choice(conv_ids)
        user_id = random.choice(list(user_profiles.keys()))
        profile = user_profiles[user_id]
        
        # Generate message based on verbosity
        topic = random.choice(topics)
        if profile['verbosity'] == 'high':
            msg_length = random.randint(50, 200)
        elif profile['verbosity'] == 'medium':
            msg_length = random.randint(20, 80)
        else:
            msg_length = random.randint(5, 30)
            
        user_message = f"Topic: {topic}. " + "Lorem ipsum " * (msg_length // 10)
        chatbot_reply = f"Response about {topic}. " + "Lorem ipsum " * (msg_length // 12)
        
        # Response time based on profile and message length
        base_response_time = 0.5 + (msg_length / 100)
        response_time = round(base_response_time * profile['response_time_factor'] * random.uniform(0.8, 1.2), 2)
        
        # Sentiment with bias from profile
        sentiment_base = random.uniform(-0.7, 0.7)
        sentiment_score = round(min(1.0, max(-1.0, sentiment_base + profile['sentiment_bias'])), 2)
        
        if sentiment_score > 0.3:
            sentiment_label = 'positive'
        elif sentiment_score < -0.3:
            sentiment_label = 'negative'
        else:
            sentiment_label = 'neutral'
            
        # Timestamp with realistic patterns (more activity during business hours)
        now = datetime.now()
        days_ago = random.randint(0, 14)
        hour = random.choices(
            range(24), 
            weights=[1, 1, 1, 1, 1, 2, 5, 10, 15, 20, 18, 15, 20, 18, 15, 12, 10, 8, 5, 3, 2, 2, 1, 1]
        )[0]
        timestamp = now - timedelta(days=days_ago, hours=now.hour-hour)
        
        # Drop-off more likely for negative sentiment or long response times
        drop_off_prob = 0.1 + (0.3 if sentiment_score < -0.5 else 0) + (0.3 if response_time > 1.5 else 0)
        drop_off = random.random() < drop_off_prob
        
        # Add some user intent classification
        intents = ['question', 'complaint', 'feedback', 'request', 'information']
        intent = random.choice(intents)
        
        # Add some tags for categorization
        tags = random.sample(['urgent', 'resolved', 'escalated', 'follow-up', 'new-user'], k=random.randint(0, 2))
        
        # Add geographic data
        regions = ['North America', 'Europe', 'Asia', 'South America', 'Africa', 'Oceania']
        region = random.choice(regions)
        
        # Add user satisfaction score
        satisfaction = None
        if random.random() < 0.7:  # 70% chance of having a satisfaction score
            satisfaction = random.randint(1, 5)
        
        # Add resolution status
        resolution_statuses = ['resolved', 'pending', 'escalated', 'closed', 'reopened']
        resolution_status = random.choice(resolution_statuses)
        
        # Add first-time user flag
        first_time_user = random.random() < 0.3  # 30% chance of being a first-time user
        
        # Add response quality score (from AI evaluation)
        response_quality = round(random.uniform(0.5, 1.0), 2)
        
        data.append({
            "conversation_id": conv_id,
            "user_id": user_id,
            "user_message": user_message,
            "chatbot_reply": chatbot_reply,
            "response_time": response_time,
            "timestamp": timestamp,
            "sentiment_label": sentiment_label,
            "sentiment_score": sentiment_score,
            "drop_off": drop_off,
            "message_length": len(user_message),
            "intent": intent,
            "tags": ','.join(tags) if tags else '',
            "region": region,
            "topic": topic,
            "topic_image": topic_images[topic],
            "user_avatar": profile['avatar'],
            "satisfaction": satisfaction,
            "resolution_status": resolution_status,
            "first_time_user": first_time_user,
            "response_quality": response_quality
        })
    
    return pd.DataFrame(data)

# -----------------------------
# DATA PROCESSING FUNCTIONS
# -----------------------------
@st.cache_data
def generate_word_cloud(text_series):
    """Generate a word cloud from a series of text"""
    all_text = ' '.join(text_series.astype(str))
    # Remove common words and punctuation
    all_text = re.sub(r'[^\w\s]', '', all_text.lower())
    stop_words = set(['the', 'and', 'to', 'of', 'a', 'in', 'for', 'is', 'on', 'that', 'by', 'this', 'with', 'i', 'you', 'it', 'not', 'or', 'be', 'are', 'from', 'at', 'as', 'your', 'have', 'topic', 'lorem', 'ipsum'])
    word_list = [word for word in all_text.split() if word not in stop_words and len(word) > 2]
    word_freq = Counter(word_list)
    
    # Generate word cloud
    wc = WordCloud(width=800, height=400, background_color='black', colormap='viridis', max_words=100)
    if word_freq:
        wc.generate_from_frequencies(word_freq)
        return wc
    return None

@st.cache_data
def create_conversation_network(df):
    """Create a network graph of conversations"""
    if df.empty:
        return None, None
    
    G = nx.DiGraph()
    
    # Add nodes for users and topics
    users = df['user_id'].unique()
    topics = df['topic'].unique() if 'topic' in df.columns else []
    
    for user in users:
        G.add_node(user, type='user')
    
    for topic in topics:
        G.add_node(topic, type='topic')
    
    # Add edges between users and topics
    for user in users:
        user_topics = df[df['user_id'] == user]['topic'].value_counts()
        for topic, count in user_topics.items():
            G.add_edge(user, topic, weight=count)
    
    # Calculate positions using a spring layout
    pos = nx.spring_layout(G, seed=42)
    
    # Create edge and node data for visualization
    edge_data = []
    for edge in G.edges(data=True):
        source_idx = list(G.nodes()).index(edge[0])
        target_idx = list(G.nodes()).index(edge[1])
        edge_data.append({
            'source': source_idx,
            'target': target_idx,
            'weight': edge[2].get('weight', 1)
        })
    
    node_data = []
    for node in G.nodes(data=True):
        node_data.append({
            'name': node[0],
            'type': node[1]['type']
        })
    
    return edge_data, node_data

@st.cache_data
def create_heatmap(df):
    """Create a heatmap of chat activity by hour and day"""
    if df.empty:
        return None
    
    # Extract hour and day of week
    df = df.copy()
    df['hour'] = df['timestamp'].dt.hour
    df['day_of_week'] = df['timestamp'].dt.day_name()
    
    # Order days of week
    day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    
    # Create pivot table
    heatmap_data = pd.pivot_table(
        df, 
        values='conversation_id', 
        index='day_of_week',
        columns='hour',
        aggfunc='count',
        fill_value=0
    )
    
    # Reorder days
    heatmap_data = heatmap_data.reindex(day_order)
    
    # Convert to format for Altair
    heatmap_df = heatmap_data.reset_index().melt(
        id_vars='day_of_week', 
        var_name='hour', 
        value_name='count'
    )
    
    return heatmap_df

@st.cache_data
def create_user_journey_sankey(df):
    """Create a Sankey diagram data of user journeys through intents and sentiments"""
    if df.empty or 'intent' not in df.columns:
        return None
    
    # Create source-target pairs for Sankey diagram
    sources = []
    targets = []
    values = []
    labels = []
    
    # Add users to intents
    user_intent_counts = df.groupby(['user_id', 'intent']).size().reset_index(name='count')
    
    # Create a mapping of labels to indices
    all_users = df['user_id'].unique()
    all_intents = df['intent'].unique()
    all_sentiments = df['sentiment_label'].unique()
    
    # Create label list
    labels = list(all_users) + list(all_intents) + list(all_sentiments)
    
    # Map labels to indices
    label_to_idx = {label: i for i, label in enumerate(labels)}
    
    # User to intent flows
    for _, row in user_intent_counts.iterrows():
        sources.append(label_to_idx[row['user_id']])
        targets.append(label_to_idx[row['intent']])
        values.append(row['count'])
    
    # Intent to sentiment flows
    intent_sentiment_counts = df.groupby(['intent', 'sentiment_label']).size().reset_index(name='count')
    for _, row in intent_sentiment_counts.iterrows():
        sources.append(label_to_idx[row['intent']])
        targets.append(label_to_idx[row['sentiment_label']])
        values.append(row['count'])
    
    # Create Sankey data
    sankey_data = pd.DataFrame({
        'source': sources,
        'target': targets,
        'value': values,
        'source_label': [labels[s] for s in sources],
        'target_label': [labels[t] for t in targets]
    })
    
    return sankey_data, labels

# Function to create an Airtable-like grid
def create_airtable_grid(df, editable_columns=None, key=None):
    """
    Create an Airtable-like grid with AgGrid
    
    Parameters:
    - df: DataFrame to display
    - editable_columns: List of column names that should be editable
    - key: Unique key for the grid
    
    Returns:
    - The AgGrid response object
    """
    if editable_columns is None:
        editable_columns = []
    
    gb = GridOptionsBuilder.from_dataframe(df)
    
    # Enable selection
    gb.configure_selection('multiple', use_checkbox=True, groupSelectsChildren=True)
    gb.configure_grid_options(domLayout='normal', enableCellTextSelection=True)
    
    # Configure pagination
    gb.configure_pagination(paginationAutoPageSize=False, paginationPageSize=15)
    
    # Configure default column settings
    gb.configure_default_column(
        resizable=True, 
        filterable=True, 
        sortable=True, 
        editable=False,
        groupable=True,
        wrapText=True,
        autoHeight=True
    )
    
    # Configure specific columns
    for col in df.columns:
        if col in editable_columns:
            gb.configure_column(col, editable=True)
        
        # Special formatting for specific column types
        if col == 'timestamp':
            gb.configure_column(
                col, 
                type=["dateColumnFilter", "customDateTimeFormat"], 
                custom_format_string="yyyy-MM-dd HH:mm",
                width=160
            )
        elif col == 'sentiment_score':
            gb.configure_column(
                col,
                cellRenderer=JsCode("""
                function(params) {
                    const value = params.value;
                    let color = 'gray';
                    if (value > 0.3) color = '#4CAF50';
                    else if (value < -0.3) color = '#F44336';
                    else color = '#FFC107';
                    
                    const barWidth = Math.abs(value) * 100;
                    const direction = value >= 0 ? 'right' : 'left';
                    
                    return `
                        <div style="width: 100%; height: 20px; position: relative;">
                            <div style="position: absolute; top: 0; ${direction}: 50%; background-color: ${color}; height: 100%; width: ${barWidth}%; opacity: 0.7; border-radius: 2px;"></div>
                            <div style="position: absolute; width: 100%; text-align: center; color: black;">${value.toFixed(2)}</div>
                        </div>
                    `;
                }
                """),
                width=140
            )
        elif col == 'sentiment_label':
            gb.configure_column(
                col,
                cellRenderer=JsCode("""
                function(params) {
                    const value = params.value;
                    let color = 'gray';
                    let icon = '😐';
                    
                    if (value === 'positive') {
                        color = '#4CAF50';
                    } else if (value === 'negative') {
                        color = '#F44336';
                        icon = '😞';
                    } else {
                        color = '#FFC107';
                        icon = '😐';
                    }
                    
                    return `
                        <div style="display: flex; align-items: center; gap: 5px;">
                            <span style="font-size: 16px;">${icon}</span>
                            <span style="color: ${color}; font-weight: 500;">${value}</span>
                        </div>
                    `;
                }
                """),
                width=120
            )
        elif col == 'drop_off':
            gb.configure_column(
                col,
                cellRenderer=JsCode("""
                function(params) {
                    const value = params.value;
                    const color = value ? '#F44336' : '#4CAF50';
                    const text = value ? 'Yes' : 'No';
                    const icon = value ? '❌' : '✅';
                    
                    return `
                        <div style="display: flex; align-items: center; gap: 5px;">
                            <span>${icon}</span>
                            <span style="color: ${color};">${text}</span>
                        </div>
                    `;
                }
                """),
                width=100
            )
        elif col == 'user_id':
            gb.configure_column(
                col,
                cellRenderer=JsCode("""
                function(params) {
                    const value = params.value;
                    const avatar = params.data.user_avatar || 'https://ui-avatars.com/api/?name=' + value;
                    
                    return `
                        <div style="display: flex; align-items: center; gap: 8px;">
                            <img src="${avatar}" style="width: 24px; height: 24px; border-radius: 50%;" />
                            <span>${value}</span>
                        </div>
                    `;
                }
                """),
                width=120
            )
        elif col == 'response_time':
            gb.configure_column(
                col,
                cellRenderer=JsCode("""
                function(params) {
                    const value = params.value;
                    let color = '#4CAF50';
                    
                    if (value > 1.5) color = '#F44336';
                    else if (value > 1.0) color = '#FFC107';
                    
                    return `
                        <div style="display: flex; align-items: center; gap: 5px;">
                            <span style="color: ${color}; font-weight: 500;">${value.toFixed(2)}s</span>
                        </div>
                    `;
                }
                """),
                width=120
            )
        elif col == 'topic':
            gb.configure_column(
                col,
                cellRenderer=JsCode("""
                function(params) {
                    const value = params.value;
                    const image = params.data.topic_image || '';
                    
                    return `
                        <div style="display: flex; align-items: center; gap: 8px;">
                            ${image ? `<img src="${image}" style="width: 24px; height: 24px; border-radius: 4px; object-fit: cover;" />` : ''}
                            <span>${value}</span>
                        </div>
                    `;
                }
                """),
                width=150
            )
        elif col == 'tags':
            gb.configure_column(
                col,
                cellRenderer=JsCode("""
                function(params) {
                    const value = params.value;
                    if (!value) return '';
                    
                    const tags = value.split(',');
                    let html = '<div style="display: flex; flex-wrap: wrap; gap: 4px;">';
                    
                    const colors = {
                        'urgent': '#F44336',
                        'resolved': '#4CAF50',
                        'escalated': '#FF9800',
                        'follow-up': '#2196F3',
                        'new-user': '#9C27B0'
                    };
                    
                    tags.forEach(tag => {
                        const color = colors[tag] || '#607D8B';
                        html += `
                            <span style="
                                background-color: ${color}; 
                                color: white; 
                                padding: 2px 6px; 
                                border-radius: 12px; 
                                font-size: 11px;
                                white-space: nowrap;
                            ">${tag}</span>
                        `;
                    });
                    
                    html += '</div>';
                    return html;
                }
                """),
                width=150
            )
        elif col == 'user_message' or col == 'chatbot_reply':
            gb.configure_column(
                col,
                cellRenderer=JsCode("""
                function(params) {
                    const value = params.value;
                    if (!value) return '';
                    
                    // Truncate long messages
                    const maxLength = 100;
                    const displayText = value.length > maxLength ? value.substring(0, maxLength) + '...' : value;
                    
                    return `
                        <div title="${value.replace(/"/g, '&quot;')}">
                            ${displayText}
                        </div>
                    `;
                }
                """),
                width=200
            )
        elif col == 'satisfaction':
            gb.configure_column(
                col,
                cellRenderer=JsCode("""
                function(params) {
                    const value = params.value;
                    if (value === null || value === undefined) return 'N/A';
                    
                    let stars = '';
                    for (let i = 1; i <= 5; i++) {
                        if (i <= value) {
                            stars += '<span style="color: gold;">★</span>';
                        } else {
                            stars += '<span style="color: #ccc;">★</span>';
                        }
                    }
                    
                    return `<div>${stars} (${value})</div>`;
                }
                """),
                width=120
            )
        elif col == 'resolution_status':
            gb.configure_column(
                col,
                cellRenderer=JsCode("""
                function(params) {
                    const value = params.value;
                    let color = '#607D8B';
                    
                    if (value === 'resolved') color = '#4CAF50';
                    else if (value === 'pending') color = '#FFC107';
                    else if (value === 'escalated') color = '#F44336';
                    else if (value === 'closed') color = '#9E9E9E';
                    else if (value === 'reopened') color = '#2196F3';
                    
                    return `
                        <div style="display: flex; align-items: center; gap: 5px;">
                            <span style="
                                background-color: ${color}; 
                                color: white; 
                                padding: 2px 6px; 
                                border-radius: 12px; 
                                font-size: 11px;
                            ">${value}</span>
                        </div>
                    `;
                }
                """),
                width=120
            )
        elif col == 'first_time_user':
            gb.configure_column(
                col,
                cellRenderer=JsCode("""
                function(params) {
                    const value = params.value;
                    return value ? 
                        '<span style="color: #2196F3; font-weight: 500;">✨ New</span>' : 
                        '<span style="color: #9E9E9E;">Returning</span>';
                }
                """),
                width=100
            )
        elif col == 'response_quality':
            gb.configure_column(
                col,
                cellRenderer=JsCode("""
                function(params) {
                    const value = params.value;
                    const percentage = Math.round(value * 100);
                    let color = '#4CAF50';
                    
                    if (value < 0.7) color = '#F44336';
                    else if (value < 0.85) color = '#FFC107';
                    
                    return `
                        <div style="width: 100%; height: 20px; position: relative;">
                            <div style="position: absolute; top: 0; left: 0; background-color: ${color}; height: 100%; width: ${percentage}%; opacity: 0.7; border-radius: 2px;"></div>
                            <div style="position: absolute; width: 100%; text-align: center; color: black;">${percentage}%</div>
                        </div>
                    `;
                }
                """),
                width=120
            )
    
    # Build grid options
    grid_options = gb.build()
    
    # Create the grid
    return AgGrid(
        df,
        gridOptions=grid_options,
        data_return_mode='AS_INPUT',
        update_mode=GridUpdateMode.MODEL_CHANGED,
        fit_columns_on_grid_load=False,
        theme='alpine',
        enable_enterprise_modules=True,
        height=500,
        width='100%',
        reload_data=False,
        key=key
    )

# Function to fetch images from Unsplash
@st.cache_data(ttl=3600)
def fetch_unsplash_images(query, count=1):
    """Fetch images from Unsplash based on query"""
    try:
        # Using a demo API key - in production, use your own key
        access_key = "demo-access-key"
        url = f"https://api.unsplash.com/photos/random?query={query}&count={count}&client_id={access_key}"
        
        # For demo purposes, return predefined images instead of making actual API calls
        predefined_images = {
            "chat": [
                "https://images.unsplash.com/photo-1577563908411-5077b6dc7624?ixlib=rb-1.2.1&auto=format&fit=crop&w=800&q=80",
                "https://images.unsplash.com/photo-1573497019940-1c28c88b4f3e?ixlib=rb-1.2.1&auto=format&fit=crop&w=800&q=80"
            ],
            "analytics": [
                "https://images.unsplash.com/photo-1551288049-bebda4e38f71?ixlib=rb-1.2.1&auto=format&fit=crop&w=800&q=80",
                "https://images.unsplash.com/photo-1460925895917-afdab827c52f?ixlib=rb-1.2.1&auto=format&fit=crop&w=800&q=80"
            ],
            "dashboard": [
                "https://images.unsplash.com/photo-1543286386-713bdd548da4?ixlib=rb-1.2.1&auto=format&fit=crop&w=800&q=80",
                "https://images.unsplash.com/photo-1543286386-2e659306cd6c?ixlib=rb-1.2.1&auto=format&fit=crop&w=800&q=80"
            ],
            "sentiment": [
                "https://images.unsplash.com/photo-1499750310107-5fef28a66643?ixlib=rb-1.2.1&auto=format&fit  [
                "https://images.unsplash.com/photo-1499750310107-5fef28a66643?ixlib=rb-1.2.1&auto=format&fit=crop&w=800&q=80",
                "https://images.unsplash.com/photo-1484069560501-87d72b0c3669?ixlib=rb-1.2.1&auto=format&fit=crop&w=800&q=80"
            ],
            "customer service": [
                "https://images.unsplash.com/photo-1556745757-8d76bdb6984b?ixlib=rb-1.2.1&auto=format&fit=crop&w=800&q=80",
                "https://images.unsplash.com/photo-1521791136064-7986c2920216?ixlib=rb-1.2.1&auto=format&fit=crop&w=800&q=80"
            ],
            "support": [
                "https://images.unsplash.com/photo-1549923746-c502d488b3ea?ixlib=rb-1.2.1&auto=format&fit=crop&w=800&q=80",
                "https://images.unsplash.com/photo-1517245386807-bb43f82c33c4?ixlib=rb-1.2.1&auto=format&fit=crop&w=800&q=80"
            ],
            "conversation": [
                "https://images.unsplash.com/photo-1573497019236-61f12a415e6e?ixlib=rb-1.2.1&auto=format&fit=crop&w=800&q=80",
                "https://images.unsplash.com/photo-1529156069898-49953e39b3ac?ixlib=rb-1.2.1&auto=format&fit=crop&w=800&q=80"
            ]
        }
        
        # Return predefined images if available, otherwise return placeholder
        if query.lower() in predefined_images:
            return predefined_images[query.lower()][:count]
        else:
            return ["https://images.unsplash.com/photo-1568667256549-094345857637?ixlib=rb-1.2.1&auto=format&fit=crop&w=800&q=80"] * count
            
    except Exception as e:
        st.error(f"Error fetching images: {e}")
        return ["https://images.unsplash.com/photo-1568667256549-094345857637?ixlib=rb-1.2.1&auto=format&fit=crop&w=800&q=80"] * count

# -----------------------------
# MAIN APPLICATION
# -----------------------------
def main():
    # Load CSS and SVG icons
    load_css()
    icons = load_svg_icons()
    
    # Set up session state
    if 'dark_mode' not in st.session_state:
        st.session_state.dark_mode = False
    
    if 'refresh_interval' not in st.session_state:
        st.session_state.refresh_interval = 5
    
    if 'last_refresh' not in st.session_state:
        st.session_state.last_refresh = datetime.now()
    
    if 'show_filters' not in st.session_state:
        st.session_state.show_filters = False
    
    if 'selected_tab' not in st.session_state:
        st.session_state.selected_tab = 0
    
    # Toggle dark mode
    if st.session_state.dark_mode:
        st.markdown('<div class="dark-mode">', unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.markdown(f"""
        <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 20px;">
            {icons['dashboard']}
            <h2 style="margin: 0;">Chat Analytics</h2>
        </div>
        """, unsafe_allow_html=True)
        
        # Dark mode toggle
        dark_mode = st.toggle("Dark Mode", value=st.session_state.dark_mode)
        if dark_mode != st.session_state.dark_mode:
            st.session_state.dark_mode = dark_mode
            st.experimental_rerun()
        
        # Auto-refresh settings
        st.markdown("### Auto-Refresh Settings")
        refresh_interval = st.slider(
            "Refresh interval (seconds)", 
            min_value=1, 
            max_value=60, 
            value=st.session_state.refresh_interval,
            step=1
        )
        
        if refresh_interval != st.session_state.refresh_interval:
            st.session_state.refresh_interval = refresh_interval
        
        # Manual refresh button
        if st.button(f"{icons['refresh']} Refresh Data", use_container_width=True, type="primary"):
            st.session_state.last_refresh = datetime.now()
            st.experimental_rerun()
        
        # Show/hide filters
        if st.button(
            f"{icons['filter']} {'Hide' if st.session_state.show_filters else 'Show'} Filters", 
            use_container_width=True
        ):
            st.session_state.show_filters = not st.session_state.show_filters
            st.experimental_rerun()
        
        # Display filters if enabled
        if st.session_state.show_filters:
            st.markdown("### Filters")
            
            # Time period filter
            st.markdown(f"{icons['calendar']} **Time Period**")
            time_period = st.selectbox(
                "Select time period",
                ["Last 24 Hours", "Last 7 Days", "Last 30 Days", "All Time"],
                index=3,
                label_visibility="collapsed"
            )
            
            # User filter
            st.markdown(f"{icons['user']} **Users**")
            # This will be populated after data is loaded
            
            # Sentiment filter
            st.markdown(f"{icons['sentiment_positive']} **Sentiment**")
            # This will be populated after data is loaded
            
            # Topic filter
            st.markdown(f"{icons['topic']} **Topics**")
            # This will be populated after data is loaded
            
            # Intent filter
            st.markdown(f"{icons['intent']} **Intents**")
            # This will be populated after data is loaded
            
            # Region filter
            st.markdown(f"{icons['region']} **Regions**")
            # This will be populated after data is loaded
        
        # Display last refresh time
        st.markdown(f"""
        <div style="margin-top: 20px; font-size: 0.8rem; color: #666;">
            Last refreshed: {st.session_state.last_refresh.strftime('%Y-%m-%d %H:%M:%S')}
        </div>
        """, unsafe_allow_html=True)
    
    # Main content
    # Custom header with animation
    st.markdown(f"""
    <div class="custom-header">
        <div class="header-content">
            <h1 style="color: white; margin: 0; font-size: 2.5rem;">
                {icons['chat']} Premium Chat Analytics Dashboard
            </h1>
            <p style="color: rgba(255, 255, 255, 0.8); margin-top: 10px;">
                Advanced insights and visualizations for your chat data
            </p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Check if it's time to auto-refresh
    current_time = datetime.now()
    time_diff = (current_time - st.session_state.last_refresh).total_seconds()
    
    if time_diff >= st.session_state.refresh_interval:
        st.session_state.last_refresh = current_time
        st.experimental_rerun()
    
    # Fetch data
    with st.spinner("Loading chat data..."):
        df = fetch_chat_logs()
        if df.empty:
            st.info("No chat logs found in Supabase. Generating random data for demo purposes.")
            df = generate_random_data(100)
    
    # Apply time period filter
    if 'time_period' in locals():
        if time_period != "All Time":
            days = {"Last 24 Hours": 1, "Last 7 Days": 7, "Last 30 Days": 30}
            cutoff_date = datetime.now() - timedelta(days=days[time_period])
            df = df[df['timestamp'] >= cutoff_date]
    
    # Populate sidebar filters with actual data
    if st.session_state.show_filters and 'df' in locals():
        with st.sidebar:
            # User filter
            unique_users = sorted(df['user_id'].unique().tolist()) if 'user_id' in df.columns else []
            selected_users = st.multiselect("Select users", unique_users, label_visibility="collapsed")
            
            # Sentiment filter
            unique_sentiments = sorted(df['sentiment_label'].unique().tolist()) if 'sentiment_label' in df.columns else []
            selected_sentiments = st.multiselect("Select sentiments", unique_sentiments, label_visibility="collapsed")
            
            # Topic filter
            unique_topics = sorted(df['topic'].unique().tolist()) if 'topic' in df.columns else []
            selected_topics = st.multiselect("Select topics", unique_topics, label_visibility="collapsed")
            
            # Intent filter
            unique_intents = sorted(df['intent'].unique().tolist()) if 'intent' in df.columns else []
            selected_intents = st.multiselect("Select intents", unique_intents, label_visibility="collapsed")
            
            # Region filter
            unique_regions = sorted(df['region'].unique().tolist()) if 'region' in df.columns else []
            selected_regions = st.multiselect("Select regions", unique_regions, label_visibility="collapsed")
            
            # Apply filters
            if selected_users:
                df = df[df['user_id'].isin(selected_users)]
            
            if selected_sentiments:
                df = df[df['sentiment_label'].isin(selected_sentiments)]
            
            if selected_topics:
                df = df[df['topic'].isin(selected_topics)]
            
            if selected_intents:
                df = df[df['intent'].isin(selected_intents)]
            
            if selected_regions:
                df = df[df['region'].isin(selected_regions)]
    
    # Key metrics
    st.markdown("### Key Performance Indicators")
    
    # Fetch relevant images for metrics
    metric_images = {
        "messages": fetch_unsplash_images("chat message", 1)[0],
        "response_time": fetch_unsplash_images("time clock", 1)[0],
        "sentiment": fetch_unsplash_images("emotion sentiment", 1)[0],
        "retention": fetch_unsplash_images("customer retention", 1)[0]
    }
    
    # Create metric cards with images
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_messages = len(df)
        unique_users = df['user_id'].nunique() if 'user_id' in df.columns else 0
        
        st.markdown(f"""
        <div class="metric-card">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
                <h3 style="margin: 0; font-size: 1rem; color: #1c83e1;">Total Messages</h3>
                {icons['message']}
            </div>
            <p style="font-size: 2.5rem; font-weight: bold; margin: 10px 0; color: #333;">{total_messages}</p>
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <p style="font-size: 0.9rem; color: #666; margin: 0;">From {unique_users} users</p>
                <div style="width: 30px; height: 30px; border-radius: 50%; overflow: hidden;">
                    <img src="{metric_images['messages']}" style="width: 100%; height: 100%; object-fit: cover;" />
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        avg_response = f"{df['response_time'].mean():.2f}" if not df.empty else "N/A"
        target_response = 1.0
        response_status = "✅" if float(avg_response) < target_response else "⚠️"
        
        st.markdown(f"""
        <div class="metric-card">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
                <h3 style="margin: 0; font-size: 1rem; color: #1c83e1;">Avg. Response Time</h3>
                {icons['time']}
            </div>
            <p style="font-size: 2.5rem; font-weight: bold; margin: 10px 0; color: #333;">{avg_response}s</p>
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <p style="font-size: 0.9rem; color: #666; margin: 0;">{response_status} Target: < {target_response}s</p>
                <div style="width: 30px; height: 30px; border-radius: 50%; overflow: hidden;">
                    <img src="{metric_images['response_time']}" style="width: 100%; height: 100%; object-fit: cover;" />
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        positive_ratio = f"{(df['sentiment_label'] == 'positive').mean() * 100:.1f}%" if not df.empty else "N/A"
        target_positive = 60
        sentiment_status = "✅" if float(positive_ratio.replace('%', '')) > target_positive else "⚠️"
        
        st.markdown(f"""
        <div class="metric-card">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
                <h3 style="margin: 0; font-size: 1rem; color: #1c83e1;">Positive Sentiment</h3>
                {icons['sentiment_positive']}
            </div>
            <p style="font-size: 2.5rem; font-weight: bold; margin: 10px 0; color: #333;">{positive_ratio}</p>
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <p style="font-size: 0.9rem; color: #666; margin: 0;">{sentiment_status} Target: > {target_positive}%</p>
                <div style="width: 30px; height: 30px; border-radius: 50%; overflow: hidden;">
                    <img src="{metric_images['sentiment']}" style="width: 100%; height: 100%; object-fit: cover;" />
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        dropoff_rate = f"{(df['drop_off'] == True).mean() * 100:.1f}%" if not df.empty else "N/A"
        target_dropoff = 10
        dropoff_status = "✅" if float(dropoff_rate.replace('%', '')) < target_dropoff else "⚠️"
        
        st.markdown(f"""
        <div class="metric-card">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
                <h3 style="margin: 0; font-size: 1rem; color: #1c83e1;">Drop-off Rate</h3>
                {icons['user']}
            </div>
            <p style="font-size: 2.5rem; font-weight: bold; margin: 10px 0; color: #333;">{dropoff_rate}</p>
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <p style="font-size: 0.9rem; color: #666; margin: 0;">{dropoff_status} Target: < {target_dropoff}%</p>
                <div style="width: 30px; height: 30px; border-radius: 50%; overflow: hidden;">
                    <img src="{metric_images['retention']}" style="width: 100%; height: 100%; object-fit: cover;" />
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # Apply styling to metric cards
    style_metric_cards()
    
    # Tabbed interface
    tab_titles = [
        f"{icons['dashboard']} Overview", 
        f"{icons['analytics']} Detailed Analysis", 
        f"{icons['3d']} Visualizations", 
        f"{icons['network']} User Journeys",
        f"{icons['chat']} Chat Explorer"
    ]
    
    tabs = st.tabs(tab_titles)
    
    # Tab 1: Overview
    with tabs[0]:
        col1, col2 = st.columns(2)
        
        with col1:
            with chart_container(
                "Message Volume Over Time", 
                "Displays the trend of message volume over time"
            ):
                # Resample by day and count messages
                if not df.empty:
                    daily_counts = df.resample('D', on='timestamp').size().reset_index(name='count')
                    daily_counts.columns = ['Date', 'Message Count']
                    
                    # Create time series chart with Altair
                    chart = alt.Chart(daily_counts).mark_line(
                        point=True,
                        interpolate='basis'
                    ).encode(
                        x=alt.X('Date:T', title='Date'),
                        y=alt.Y('Message Count:Q', title='Message Count'),
                        tooltip=['Date:T', 'Message Count:Q']
                    ).properties(
                        height=300
                    ).interactive()
                    
                    st.altair_chart(chart, use_container_width=True)
                else:
                    st.info("No data available for time series visualization")
        
        with col2:
            with chart_container(
                "Sentiment Distribution", 
                "Shows the distribution of sentiment across all messages"
            ):
                if not df.empty:
                    sentiment_counts = df['sentiment_label'].value_counts().reset_index()
                    sentiment_counts.columns = ['Sentiment', 'Count']
                    
                    # Create pie chart with Altair
                    # Define color scale for sentiments
                    domain = ['positive', 'neutral', 'negative']
                    range_ = ['#4CAF50', '#FFC107', '#F44336']
                    
                    # Create a base chart with a centered position
                    base = alt.Chart(sentiment_counts).encode(
                        theta=alt.Theta("Count:Q", stack=True),
                        radius=alt.Radius("Count:Q", scale=alt.Scale(type="sqrt", zero=True, rangeMin=20)),
                        color=alt.Color('Sentiment:N', scale=alt.Scale(domain=domain, range=range_)),
                        tooltip=['Sentiment:N', 'Count:Q', alt.Tooltip('Count:Q', format='.1%', title='Percentage')]
                    ).transform_joinaggregate(
                        total='sum(Count)'
                    ).transform_calculate(
                        percentage="datum.Count / datum.total"
                    )
                    
                    # Draw the pie chart
                    pie = base.mark_arc(innerRadius=50, outerRadius=100)
                    
                    # Add text labels
                    text = base.mark_text(radiusOffset=15).encode(
                        text=alt.Text('percentage:Q', format='.1%')
                    )
                    
                    chart = (pie + text).properties(
                        height=300,
                        width=300
                    )
                    
                    st.altair_chart(chart, use_container_width=True)
                else:
                    st.info("No data available for sentiment visualization")
        
        # Activity heatmap
        with chart_container(
            "Chat Activity Patterns", 
            "Displays chat activity patterns by day of week and hour of day"
        ):
            heatmap_df = create_heatmap(df)
            if heatmap_df is not None:
                # Create heatmap with Altair
                heatmap = alt.Chart(heatmap_df).mark_rect().encode(
                    x=alt.X('hour:O', title='Hour of Day'),
                    y=alt.Y('day_of_week:O', title='Day of Week', 
                           sort=['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']),
                    color=alt.Color('count:Q', scale=alt.Scale(scheme='viridis'), title='Message Count'),
                    tooltip=['day_of_week:O', 'hour:O', 'count:Q']
                ).properties(
                    title='Chat Activity Heatmap by Day and Hour'
                )
                
                st.altair_chart(heatmap, use_container_width=True)
            else:
                st.info("Not enough data for heatmap visualization")
        
        # Word cloud from messages
        with chart_container(
            "Common Terms in User Messages", 
            "Visualizes frequently used terms in user messages"
        ):
            wordcloud = generate_word_cloud(df['user_message'])
            if wordcloud:
                # Convert the word cloud to an image
                fig, ax = plt.subplots(figsize=(10, 5))
                ax.imshow(wordcloud, interpolation='bilinear')
                ax.axis('off')
                st.pyplot(fig)
            else:
                st.info("Not enough text data for word cloud visualization")
    
    # Tab 2: Detailed Analysis
    with tabs[1]:
        col1, col2 = st.columns(2)
        
        with col1:
            with chart_container(
                "Response Time Distribution", 
                "Shows the distribution of response times"
            ):
                if not df.empty:
                    # Create histogram with Altair
                    hist = alt.Chart(df).mark_bar().encode(
                        alt.X('response_time:Q', bin=alt.Bin(maxbins=20), title='Response Time (seconds)'),
                        alt.Y('count()', title='Count'),
                        tooltip=['count()', alt.Tooltip('response_time:Q', title='Response Time')]
                    ).properties(
                        height=300
                    )
                    
                    st.altair_chart(hist, use_container_width=True)
                    
                    # Add statistics
                    st.markdown(f"""
                    <div style="background-color: rgba(28, 131, 225, 0.1); padding: 15px; border-radius: 10px;">
                        <h4 style="margin-top: 0;">Response Time Statistics:</h4>
                        <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 10px;">
                            <div>
                                <span style="font-weight: 500;">Mean:</span> {df['response_time'].mean():.2f}s
                            </div>
                            <div>
                                <span style="font-weight: 500;">Median:</span> {df['response_time'].median():.2f}s
                            </div>
                            <div>
                                <span style="font-weight: 500;">90th Percentile:</span> {df['response_time'].quantile(0.9):.2f}s
                            </div>
                            <div>
                                <span style="font-weight: 500;">Max:</span> {df['response_time'].max():.2f}s
                            </div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.info("No data available for response time analysis")
        
        with col2:
            with chart_container(
                "Sentiment Score vs Message Length", 
                "Explores the relationship between message length and sentiment"
            ):
                if not df.empty:
                    # Create scatter plot with Altair
                    scatter = alt.Chart(df).mark_circle(size=60, opacity=0.6).encode(
                        x=alt.X('message_length:Q', title='Message Length (chars)'),
                        y=alt.Y('sentiment_score:Q', title='Sentiment Score (-1 to 1)'),
                        color=alt.Color('user_id:N', title='User'),
                        size=alt.Size('response_time:Q', title='Response Time'),
                        tooltip=['user_id:N', 'message_length:Q', 'sentiment_score:Q', 'response_time:Q', 'timestamp:T']
                    ).properties(
                        height=300
                    ).interactive()
                    
                    # Add regression line
                    regression = alt.Chart(df).transform_regression(
                        'message_length', 'sentiment_score'
                    ).mark_line(color='red').encode(
                        x='message_length:Q',
                        y='sentiment_score:Q'
                    )
                    
                    st.altair_chart(scatter + regression, use_container_width=True)
                    
                    # Add correlation info
                    correlation = df['message_length'].corr(df['sentiment_score'])
                    st.markdown(f"""
                    <div style="background-color: rgba(28, 131, 225, 0.1); padding: 15px; border-radius: 10px;">
                        <h4 style="margin-top: 0;">Correlation Analysis:</h4>
                        <p>Correlation between message length and sentiment: <b>{correlation:.3f}</b></p>
                        <p style="margin-bottom: 0;">
                            {
                                "Strong positive correlation" if correlation > 0.7 else
                                "Moderate positive correlation" if correlation > 0.3 else
                                "Weak positive correlation" if correlation > 0 else
                                "Strong negative correlation" if correlation < -0.7 else
                                "Moderate negative correlation" if correlation < -0.3 else
                                "Weak negative correlation"
                            }
                        </p>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.info("No data available for sentiment analysis")
        
        # User performance comparison
        with chart_container(
            "User Performance Comparison", 
            "Compares performance metrics across different users"
        ):
            if not df.empty and len(df['user_id'].unique()) > 1:
                user_metrics = df.groupby('user_id').agg({
                    'response_time': 'mean',
                    'sentiment_score': 'mean',
                    'message_length': 'mean',
                    'drop_off': lambda x: x.mean() * 100,  # Convert to percentage
                    'conversation_id': 'count'
                }).reset_index()
                
                user_metrics.columns = ['User ID', 'Avg Response Time', 'Avg Sentiment', 'Avg Message Length', 'Drop-off %', 'Message Count']
                
                # Create radar chart data
                radar_data = []
                for user in user_metrics['User ID']:
                    user_data = user_metrics[user_metrics['User ID'] == user]
                    
                    # Normalize values for radar chart
                    response_time_norm = 1 - (user_data['Avg Response Time'].values[0] / user_metrics['Avg Response Time'].max())
                    sentiment_norm = (user_data['Avg Sentiment'].values[0] + 1) / 2  # Convert from [-1,1] to [0,1]
                    length_norm = user_data['Avg Message Length'].values[0] / user_metrics['Avg Message Length'].max()
                    retention_norm = 1 - (user_data['Drop-off %'].values[0] / 100)
                    volume_norm = user_data['Message Count'].values[0] / user_metrics['Message Count'].max()
                    
                    # Add to radar data
                    radar_data.extend([
                        {'User': user, 'Metric': 'Response Speed', 'Value': response_time_norm},
                        {'User': user, 'Metric': 'Sentiment', 'Value': sentiment_norm},
                        {'User': user, 'Metric': 'Message Length', 'Value': length_norm},
                        {'User': user, 'Metric': 'Retention', 'Value': retention_norm},
                        {'User': user, 'Metric': 'Volume', 'Value': volume_norm}
                    ])
                
                radar_df = pd.DataFrame(radar_data)
                
                # Create radar chart with Altair
                radar = alt.Chart(radar_df).mark_line(point=True).encode(
                    alt.X('Metric:N', title=None),
                    alt.Y('Value:Q', scale=alt.Scale(domain=[0, 1])),
                    alt.Color('User:N'),
                    alt.Detail('User:N'),
                    tooltip=['User:N', 'Metric:N', 'Value:Q']
                ).properties(
                    width=600,
                    height=400
                )
                
                st.altair_chart(radar, use_container_width=True)
                
                # Show metrics table with Airtable-like grid
                st.subheader("User Performance Metrics")
                grid_response = create_airtable_grid(
                    user_metrics,
                    key="user_metrics_grid"
                )
            else:
                st.info("Not enough user data for comparison")
    
    # Tab 3: Visualizations
    with tabs[2]:
        # Create tabs for different visualizations
        viz_tabs = st.tabs([
            "Sentiment Over Time", 
            "User-Topic Network", 
            "Advanced Metrics"
        ])
        
        with viz_tabs[0]:
            st.subheader("Sentiment Analysis Over Time")
            if not df.empty:
                # Prepare data
                df_time = df.copy()
                df_time['date'] = df_time['timestamp'].dt.date
                sentiment_time = df_time.groupby('date')['sentiment_score'].mean().reset_index()
                
                # Create line chart with Altair
                line = alt.Chart(sentiment_time).mark_line(point=True).encode(
                    x=alt.X('date:T', title='Date'),
                    y=alt.Y('sentiment_score:Q', title='Average Sentiment Score',
                           scale=alt.Scale(domain=[-1, 1])),
                    tooltip=['date:T', alt.Tooltip('sentiment_score:Q', format='.2f')]
                ).properties(
                    height=400
                ).interactive()
                
                st.altair_chart(line, use_container_width=True)
                
                st.caption("""
                This visualization shows the average sentiment score over time.
                Positive values indicate positive sentiment, while negative values indicate negative sentiment.
                """)
            else:
                st.info("Not enough data for sentiment over time visualization")
        
        with viz_tabs[1]:
            st.subheader("User-Topic Network Graph")
            edge_data, node_data = create_conversation_network(df)
            if edge_data and node_data:
                # Create network visualization with Altair
                nodes_df = pd.DataFrame(node_data)
                edges_df = pd.DataFrame(edge_data)
                
                # Create a visualization that shows the network structure
                # First, create a selection that is used to highlight nodes
                highlight = alt.selection_point(
                    on='mouseover', fields=['name'], nearest=True
                )
                
                # Create the nodes visualization
                node_chart = alt.Chart(nodes_df).mark_circle(size=300).encode(
                    x=alt.X('index:O', axis=None),
                    y=alt.Y('type:N'),
                    color=alt.Color('type:N', scale=alt.Scale(
                        domain=['user', 'topic'],
                        range=['#4b6cb7', '#ff7f0e']
                    )),
                    tooltip=['name:N', 'type:N'],
                    opacity=alt.condition(highlight, alt.value(1), alt.value(0.3))
                ).add_params(highlight)
                
                # Create text labels for nodes
                text_chart = alt.Chart(nodes_df).mark_text(dy=-15).encode(
                    x=alt.X('index:O', axis=None),
                    y=alt.Y('type:N'),
                    text='name:N',
                    opacity=alt.condition(highlight, alt.value(1), alt.value(0.7))
                )
                
                # Combine the visualizations
                network_chart = (node_chart + text_chart).properties(
                    height=400
                ).interactive()
                
                st.altair_chart(network_chart, use_container_width=True)
                
                # Add legend
                st.markdown("""
                <div style="display: flex; gap: 20px; margin-top: 10px;">
                    <div style="display: flex; align-items: center; gap: 5px;">
                        <div style="width: 12px; height: 12px; border-radius: 50%; background-color: #4b6cb7;"></div>
                        <span>Users</span>
                    </div>
                    <div style="display: flex; align-items: center; gap: 5px;">
                        <div style="width: 12px; height: 12px; border-radius: 50%; background-color: #ff7f0e;"></div>
                        <span>Topics</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                st.caption("""
                This network graph shows connections between users and conversation topics. 
                Hover over nodes to highlight connections. The visualization helps identify which users 
                are discussing which topics most frequently.
                """)
            else:
                st.info("Not enough data for network visualization")
        
        with viz_tabs[2]:
            st.subheader("Advanced Metrics Visualization")
            
            if not df.empty:
                # Create a scatter plot matrix for multiple metrics
                metrics_df = df[['sentiment_score', 'response_time', 'message_length']].copy()
                
                # Create correlation heatmap
                corr = metrics_df.corr().reset_index().melt('index')
                corr.columns = ['Variable 1', 'Variable 2', 'Correlation']
                
                corr_chart = alt.Chart(corr).mark_rect().encode(
                    x='Variable 1:O',
                    y='Variable 2:O',
                    color=alt.Color('Correlation:Q', scale=alt.Scale(domain=[-1, 1], scheme='blueorange')),
                    tooltip=['Variable 1:O', 'Variable 2:O', alt.Tooltip('Correlation:Q', format='.2f')]
                ).properties(
                    title='Correlation Matrix',
                    width=300,
                    height=300
                )
                
                # Add correlation values as text
                text = alt.Chart(corr).mark_text().encode(
                    x='Variable 1:O',
                    y='Variable 2:O',
                    text=alt.Text('Correlation:Q', format='.2f'),
                    color=alt.condition(
                        alt.datum.Correlation > 0.5,
                        alt.value('white'),
                        alt.condition(
                            alt.datum.Correlation < -0.5,
                            alt.value('white'),
                            alt.value('black')
                        )
                    )
                )
                
                st.altair_chart(corr_chart + text, use_container_width=True)
                
                # Create a bubble chart of sentiment, response time, and message length
                bubble_chart = alt.Chart(df).mark_circle(opacity=0.7).encode(
                    x=alt.X('sentiment_score:Q', title='Sentiment Score'),
                    y=alt.Y('response_time:Q', title='Response Time (s)'),
                    size=alt.Size('message_length:Q', title='Message Length'),
                    color=alt.Color('user_id:N', title='User'),
                    tooltip=['user_id:N', 'sentiment_score:Q', 'response_time:Q', 'message_length:Q', 'topic:N']
                ).properties(
                    title='Bubble Chart: Sentiment vs Response Time vs Message Length',
                    height=500
                ).interactive()
                
                st.altair_chart(bubble_chart, use_container_width=True)
                
                # Add explanation
                st.markdown("""
                <div style="background-color: rgba(28, 131, 225, 0.1); padding: 15px; border-radius: 10px; margin-top: 20px;">
                    <h4 style="margin-top: 0;">How to Interpret These Visualizations:</h4>
                    <ul>
                        <li><b>Correlation Matrix:</b> Shows the relationship strength between different metrics. Values close to 1 or -1 indicate strong correlations.</li>
                        <li><b>Bubble Chart:</b> Each bubble represents a message, with:
                            <ul>
                                <li>X-axis: Sentiment score from negative to positive</li>
                                <li>Y-axis: Response time in seconds</li>
                                <li>Bubble size: Message length</li>
                                <li>Color: Different users</li>
                            </ul>
                        </li>
                    </ul>
                    <p style="margin-bottom: 0;">
                        Look for patterns such as clusters of bubbles or correlations between metrics to identify insights about user behavior and chat performance.
                    </p>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.info("Not enough data for advanced metrics visualization")
    
    # Tab 4: User Journeys
    with tabs[3]:
        st.subheader("User Journey Flow")
        sankey_data, labels = create_user_journey_sankey(df) if not df.empty else (None, None)
        if sankey_data is not None:
            # Since Altair doesn't have a built-in Sankey diagram, we'll use matplotlib to create one
            # and display it as an image
            
            # Display a simplified version of the data
            st.markdown("### User → Intent → Sentiment Flow")
            
            # Create a grouped bar chart to show the flow
            user_intent = sankey_data[sankey_data['source_label'].isin(df['user_id'].unique())]
            
            # Create a chart showing user to intent flow
            user_intent_chart = alt.Chart(user_intent).mark_bar().encode(
                x=alt.X('source_label:N', title='User'),
                y=alt.Y('value:Q', title='Count'),
                color=alt.Color('target_label:N', title='Intent'),
                tooltip=['source_label:N', 'target_label:N', 'value:Q']
            ).properties(
                title='User to Intent Flow',
                height=300
            ).interactive()
            
            # Create a chart showing intent to sentiment flow
            intent_sentiment = sankey_data[sankey_data['source_label'].isin(df['intent'].unique())]
            
            intent_sentiment_chart = alt.Chart(intent_sentiment).mark_bar().encode(
                x=alt.X('source_label:N', title='Intent'),
                y=alt.Y('value:Q', title='Count'),
                color=alt.Color('target_label:N', title='Sentiment', 
                               scale=alt.Scale(
                                   domain=['positive', 'neutral', 'negative'],
                                   range=['#4CAF50', '#FFC107', '#F44336']
                               )),
                tooltip=['source_label:N', 'target_label:N', 'value:Q']
            ).properties(
                title='Intent to Sentiment Flow',
                height=300
            ).interactive()
            
            # Display the charts
            st.altair_chart(user_intent_chart, use_container_width=True)
            st.altair_chart(intent_sentiment_chart, use_container_width=True)
            
            st.caption("""
            These charts show the flow of users through different intents and sentiment outcomes.
            The top chart shows which intents each user engages with, while the bottom chart shows 
            how each intent leads to different sentiment outcomes.
            """)
        else:
            st.info("Not enough data for user journey visualization")
        
        # Conversation timeline
        st.subheader("Detailed Chat Timeline")
        if not df.empty:
            # Limit to most recent conversations for clarity
            recent_convs = df.sort_values('timestamp', ascending=False)['conversation_id'].unique()[:3]
            timeline_df = df[df['conversation_id'].isin(recent_convs)].copy()
            
            # Create user and bot dataframes
            user_df = timeline_df[['conversation_id', 'timestamp', 'user_message', 'sentiment_score', 'user_id']].copy()
            user_df['role'] = 'User'
            user_df = user_df.rename(columns={'user_message': 'message'})
            
            bot_df = timeline_df[['conversation_id', 'timestamp', 'chatbot_reply']].copy()
            bot_df['role'] = 'AI'
            bot_df['sentiment_score'] = 0  # Neutral for bot responses
            bot_df['user_id'] = 'AI Assistant'
            bot_df = bot_df.rename(columns={'chatbot_reply': 'message'})
            
            # Combine and sort by timestamp
            combined_df = pd.concat([user_df, bot_df]).sort_values(by="timestamp")
            
            # Create timeline visualization with Altair
            timeline = alt.Chart(combined_df).mark_circle(size=100).encode(
                x=alt.X('timestamp:T', title='Time'),
                y=alt.Y('conversation_id:N', title='Conversation ID'),
                color=alt.Color('role:N', scale=alt.Scale(domain=['User', 'AI'], range=['#4b6cb7', '#182848'])),
                tooltip=['role:N', 'user_id:N', 'timestamp:T', 'message:N', alt.Tooltip('sentiment_score:Q', format='.2f')]
            ).properties(
                height=400
            ).interactive()
            
            # Add connecting lines for conversations
            lines = alt.Chart(combined_df).mark_line(opacity=0.3).encode(
                x='timestamp:T',
                y='conversation_id:N',
                color='conversation_id:N'
            )
            
            st.altair_chart(timeline + lines, use_container_width=True)
            
            # Show conversation details
            st.subheader("Conversation Explorer")
            selected_conv = st.selectbox("Select Conversation", recent_convs)
            
            conv_messages = df[df['conversation_id'] == selected_conv].sort_values('timestamp')
            
            # Display conversation details with improved styling
            st.markdown("""
            <style>
            .chat-container {
                max-width: 100%;
                margin: 0 auto;
            }
            .message-row {
                display: flex;
                margin-bottom: 15px;
            }
            .user-row {
                justify-content: flex-end;
            }
            .bot-row {
                justify-content: flex-start;
            }
            .avatar {
                width: 40px;
                height: 40px;
                border-radius: 50%;
                overflow: hidden;
                margin: 0 10px;
            }
            .avatar img {
                width: 100%;
                height: 100%;
                object-fit: cover;
            }
            .message-bubble {
                max-width: 70%;
                padding: 10px 15px;
                border-radius: 18px;
                position: relative;
                box-shadow: 0 1px 2px rgba(0,0,0,0.1);
            }
            .user-bubble {
                background-color: #DCF8C6;
                border-bottom-right-radius: 5px;
            }
            .bot-bubble {
                background-color: #F1F0F0;
                border-bottom-left-radius: 5px;
            }
            .message-content {
                margin-bottom: 5px;
            }
            .message-meta {
                display: flex;
                justify-content: space-between;
                font-size: 0.7rem;
                color: #999;
            }
            .sentiment-indicator {
                display: inline-block;
                width: 8px;
                height: 8px;
                border-radius: 50%;
                margin-right: 5px;
            }
            </style>
            
            <div class="chat-container">
            """, unsafe_allow_html=True)
            
            for i, row in conv_messages.iterrows():
                # Determine sentiment color
                if row['sentiment_label'] == 'positive':
                    sentiment_color = "#4CAF50"
                    sentiment_icon = "😊"
                elif row['sentiment_label'] == 'negative':
                    sentiment_color = "#F44336"
                    sentiment_icon = "😞"
                else:
                    sentiment_color = "#FFC107"
                    sentiment_icon = "😐"
                
                # User message
                st.markdown(f"""
                <div class="message-row user-row">
                    <div class="message-bubble user-bubble">
                        <div class="message-content">{row['user_message']}</div>
                        <div class="message-meta">
                            <span>
                                <span class="sentiment-indicator" style="background-color: {sentiment_color};"></span>
                                {sentiment_icon} {row['sentiment_score']:.2f}
                            </span>
                            <span>{row['timestamp'].strftime('%H:%M:%S')}</span>
                        </div>
                    </div>
                    <div class="avatar">
                        <img src="{row.get('user_avatar', 'https://ui-avatars.com/api/?name=' + row['user_id'])}" alt="User Avatar">
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                # Bot response
                st.markdown(f"""
                <div class="message-row bot-row">
                    <div class="avatar">
                        <img src="https://ui-avatars.com/api/?name=AI&background=182848&color=fff" alt="Bot Avatar">
                    </div>
                    <div class="message-bubble bot-bubble">
                        <div class="message-content">{row['chatbot_reply']}</div>
                        <div class="message-meta">
                            <span>Response time: {row['response_time']}s</span>
                            <span>{row['timestamp'].strftime('%H:%M:%S')}</span>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown("</div>", unsafe_allow_html=True)
        else:
            st.info("No conversation data available")
    
    # Tab 5: Chat Explorer
    with tabs[4]:
        st.subheader("Chat Data Explorer")
        
        # Add search and filter options
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col1:
            search_term = st.text_input(
                "Search in messages", 
                placeholder="Enter search term...",
                help="Search in user messages and chatbot replies"
            )
        
        with col2:
            sentiment_filter = st.selectbox(
                "Filter by sentiment",
                ["All", "Positive", "Neutral", "Negative"],
                index=0
            )
        
        with col3:
            if 'topic' in df.columns:
                topic_filter = st.selectbox(
                    "Filter by topic",
                    ["All"] + sorted(df['topic'].unique().tolist()),
                    index=0
                )
        
        # Apply filters
        filtered_df = df.copy()
        
        if search_term:
            filtered_df = filtered_df[
                filtered_df['user_message'].str.contains(search_term, case=False) | 
                filtered_df['chatbot_reply'].str.contains(search_term, case=False)
            ]
        
        if sentiment_filter != "All":
            filtered_df = filtered_df[filtered_df['sentiment_label'].str.lower() == sentiment_filter.lower()]
        
        if 'topic_filter' in locals() and topic_filter != "All":
            filtered_df = filtered_df[filtered_df['topic'] == topic_filter]
        
        # Create Airtable-like grid
        st.markdown("### Chat Logs")
        
        # Define editable columns
        editable_columns = ['sentiment_label', 'tags', 'resolution_status']
        
        # Create the grid
        grid_response = create_airtable_grid(
            filtered_df.sort_values(by="timestamp", ascending=False),
            editable_columns=editable_columns,
            key="chat_logs_grid"
        )
        
        # Handle grid edits
        if grid_response['data'] is not None and len(grid_response['selected_rows']) > 0:
            st.markdown(f"**{len(grid_response['selected_rows'])} rows selected**")
            
            # Create action buttons for selected rows
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if st.button("Mark as Resolved", use_container_width=True):
                    st.success(f"Marked {len(grid_response['selected_rows'])} conversations as resolved")
            
            with col2:
                if st.button("Export Selected", use_container_width=True):
                    selected_df = pd.DataFrame(grid_response['selected_rows'])
                    csv = selected_df.to_csv(index=False).encode('utf-8')
                    st.download_button(
                        label="Download CSV",
                        data=csv,
                        file_name="selected_chat_logs.csv",
                        mime="text/csv",
                    )
            
            with col3:
                if st.button("Analyze Selected", use_container_width=True):
                    selected_df = pd.DataFrame(grid_response['selected_rows'])
                    
                    # Show quick analysis of selected rows
                    st.markdown("### Quick Analysis of Selected Rows")
                    
                    # Create metrics for selected rows
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Avg. Sentiment Score", f"{selected_df['sentiment_score'].mean():.2f}")
                    with col2:
                        st.metric("Avg. Response Time", f"{selected_df['response_time'].mean():.2f}s")
                    with col3:
                        st.metric("Drop-off Rate", f"{(selected_df['drop_off'] == True).mean() * 100:.1f}%")
        
        # Add export functionality
        st.markdown("### Export Options")
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button(f"{icons['download']} Export All Data as CSV", use_container_width=True):
                csv = filtered_df.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="Download CSV",
                    data=csv,
                    file_name="chat_analytics_data.csv",
                    mime="text/csv",
                )
        
        with col2:
            if st.button(f"{icons['download']} Export as Excel", use_container_width=True):
                # Create Excel file in memory
                output = BytesIO()
                with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                    filtered_df.to_excel(writer, sheet_name='Chat Logs', index=False)
                    
                    # Get the xlsxwriter workbook and worksheet objects
                    workbook = writer.book
                    worksheet = writer.sheets['Chat Logs']
                    
                    # Add some formatting
                    header_format = workbook.add_format({
                        'bold': True,
                        'text_wrap': True,
                        'valign': 'top',
                        'fg_color': '#D7E4BC',
                        'border': 1
                    })
                    
                    # Write the column headers with the defined format
                    for col_num, value in enumerate(filtered_df.columns.values):
                        worksheet.write(0, col_num, value, header_format)
                        
                    # Set column widths
                    worksheet.set_column('A:Z', 15)
                
                # Set up download button
                st.download_button(
                    label="Download Excel",
                    data=output.getvalue(),
                    file_name="chat_analytics_data.xlsx",
                    mime="application/vnd.ms-excel"
                )

    # -----------------------------
    # FOOTER
    # -----------------------------
    st.markdown("""
    <div style="background-color: rgba(28, 131, 225, 0.1); padding: 15px; border-radius: 5px; margin-top: 20px; text-align: center;">
        <p style="margin: 0; color: #666;">
            <b>Premium Chat Analytics Dashboard</b> | Auto-refreshes every {st.session_state.refresh_interval} seconds | 
            Data timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Close dark mode div if enabled
    if st.session_state.dark_mode:
        st.markdown('</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()

