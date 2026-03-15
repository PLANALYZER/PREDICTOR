import streamlit as st
import requests
import pandas as pd
from datetime import datetime
import random

# --- CONFIGURAZIONE ---
API_KEY = "adf7b41bd4a85edbf0d28b46c647b3d7"
HEADERS = {'x-rapidapi-key': API_KEY, 'x-rapidapi-host': 'v3.football.api-sports.io'}

# SQUADRE ELITE (Per alzare xG oltre la media lega)
BIG_TEAMS = ["Barcelona", "Real Madrid", "Bayern Munich", "Manchester City", "Liverpool", "Inter", "AC Milan", "Napoli", "Paris Saint Germain", "Ajax", "PSV Eindhoven"]

LEAGUE_STATS = {
    135: {"name": "Serie A", "avg": 2.58, "type": "tattico"}, 
    136: {"name": "Serie B", "avg": 2.25, "type": "chiuso"},
    39: {"name": "Premier League", "avg": 2.85, "type": "aperto"}, 
    78: {"name": "Bundesliga", "avg": 3.15, "type": "aperto"},
    88: {"name": "Eredivisie", "avg": 3.10, "type": "aperto"}, 
    140: {"name": "La Liga", "avg": 2.50, "type": "tattico"}, 
    61: {"name": "Ligue 1", "avg": 2.60, "type": "tattico"},
    207: {"name": "Super League (CH)", "avg": 2.98, "type": "aperto"},  # AGGIUNTA
    208: {"name": "Challenge League", "avg": 3.05, "type": "aperto"}    # AGGIUNTA
}

st.set_page_config(page_title="PREDICTOR AI PRO", layout="wide")

if "auth" not in st.session_state:
    st.session_state["auth"] = False
if not st.session_state["auth"]:
    st.title("🔐 Accesso Enterprise 2.0")
    pwd = st.text_input("Password", type="password")
    if st.button("SBLOCCA"):
        if pwd == "DAJE80":
            st.session_state["auth"] = True
            st.rerun()
    st.stop()

st.title("⚽ AI Predictor - Power Stats Edition")

if st.button("🚀 AVVIA ANALISI SQUADRE"):
    with st.spinner('Calcolando xG basati su Ranking Squadre...'):
        today = datetime.now().strftime('%Y-%m-%d')
        url = f"https://v3.football.api-sports.io/fixtures?date={today}"
        
        try:
            response = requests.get(url, headers=HEADERS).json()
            all_matches = []
            
            if 'response' in response and response['response']:
                for match in response['response']:
                    l_id = match['league']['id']
                    if l_id in LEAGUE_STATS:
                        home_team = match['teams']['home']['name']
                        away_team = match['teams']['away']['name']
                        media_l = LEAGUE_STATS[l_id]["avg"]
                        
                        # --- CALCOLO xG CON BONUS ELITE ---
                        bonus_h = 0.8 if home_team in BIG_TEAMS else 0.0
                        bonus_a = 0.7 if away_team in BIG_TEAMS else 0.0
                        
                        # Calcolo base pesato sulla lega + bonus squadra
                        xg_h = round((media_l * 0.55) + bonus_h + random.uniform(-0.3, 0.3), 2)
                        xg_a = round((media_l * 0.45) + bonus_a + random.uniform(-0.4, 0.2), 2)
                        
                        total_xg = round(xg_h + xg_a, 2)
                        
                        # --- MULTIGOL DINAMICI (Con 0-1 reale) ---
                        # Casa (Se è Barcellona, l'xG vola e MG diventa 2-4)
                        if xg_h > 2.10: mg_c = "2-4"
                        elif xg_h > 1.40: mg_c = "1-3"
                        elif xg_h > 0.90: mg_c = "1-2"
                        else: mg_c = "0-1"
                        
                        # Ospite
                        if xg_a > 1.90: mg_o = "2-3"
                        elif xg_a > 1.30: mg_o = "1-3"
                        elif xg_a > 0.80: mg_o = "1-2"
                        else: mg_o = "0-1"

                        # Pronostico IA
                        if total_xg < 2.20: tip = "UNDER 3.5"
                        elif total_xg > 3.20: tip = "OVER 2.5"
                        elif total_xg > 2.70: tip = "GOAL" if abs(xg_h - xg_a) < 0.6 else "OVER 1.5"
                        else: tip = "OVER 1.5"

                        all_matches.append({
                            "Lega": LEAGUE_STATS[l_id]["
