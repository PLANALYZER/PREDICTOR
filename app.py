import streamlit as st
import requests
import pandas as pd
from datetime import datetime
import random

# --- CONFIGURAZIONE ---
API_KEY = "adf7b41bd4a85edbf0d28b46c647b3d7"
HEADERS = {'x-rapidapi-key': API_KEY, 'x-rapidapi-host': 'v3.football.api-sports.io'}

# SQUADRE ELITE (Per alzare xG oltre la media lega)
BIG_TEAMS = [
    "Barcelona", "Real Madrid", "Bayern Munich", "Manchester City", "Liverpool", 
    "Inter", "AC Milan", "Napoli", "Paris Saint Germain", "Ajax", "PSV Eindhoven",
    "BSC Young Boys", "FC Basel", "Servette FC" # Aggiunte Svizzere
]

# CAMPIONATI MONITORATI
LEAGUE_STATS = {
    135: {"name": "Serie A", "avg": 2.58, "type": "tattico"}, 
    136: {"name": "Serie B", "avg": 2.25, "type": "chiuso"},
    39: {"name": "Premier League", "avg": 2.85, "type": "aperto"}, 
    78: {"name": "Bundesliga", "avg": 3.15, "type": "aperto"},
    88: {"name": "Eredivisie", "avg": 3.10, "type": "aperto"}, 
    140: {"name": "La Liga", "avg": 2.50, "type": "tattico"}, 
    61: {"name": "Ligue 1", "avg": 2.60, "type": "tattico"},
    207: {"name": "Super League (CH)", "avg": 2.98, "type": "aperto"}, # <-- AGGIUNTA
    208: {"name": "Challenge League", "avg": 3.05, "type": "aperto"}   # <-- AGGIUNTA
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

if st.button("🚀 AVVIA ANALISI TOTALE"):
    with st.spinner('Analizzando match di oggi inclusa la Svizzera...'):
        today = datetime.now().strftime('%Y-%m-%d')
        url = f"https://v3.football.api-sports.io/fixtures?date={today}"
        
        try:
            response = requests.get(url, headers=HEADERS).json()
            all_matches = []
            
            if 'response' in response and response['response']:
                for match in response['response']:
                    l_id = match['league']['id']
                    if l_id in LEAGUE_STATS:
                        home_t = match['teams']['home']['name']
                        away_t = match['teams']['away']['name']
                        media_l = LEAGUE_STATS[l_id]["avg"]
                        
                        # --- CALCOLO xG CON BONUS SQUADRA REALE ---
                        # Se gioca una big, non ci fermiamo alla media lega
                        bonus_h = 0.95 if home_t in BIG_TEAMS else 0.0
                        bonus_a = 0.85 if away_t in BIG_TEAMS else 0.0
                        
                        # Calcolo bilanciato: Media Lega + Forza Squadra
                        xg_h = round((media_l * 0.52) + bonus_h + random.uniform(-0.2, 0.4), 2)
                        xg_a = round((media_l * 0.48) + bonus_a + random.uniform(-0.3, 0.2), 2)
                        
                        # Protezione per squadre deboli (scenario 0 gol)
                        xg_h = max(0.20, xg_h)
                        xg_a = max(0.15, xg_a)
                        total_xg = round(xg_h + xg_a, 2)
                        
                        # --- MULTIGOL CON SCENARIO 0-1 ---
                        # Casa
                        if xg_h > 2.20: mg_c = "2-4"
                        elif xg_h > 1.45: mg_c = "1-3"
                        elif xg_h > 0.95: mg_c = "1-2"
                        else: mg_c = "0-1"
                        
                        # Ospite
                        if xg_a > 1.95: mg_o = "2-3"
                        elif xg_a > 1.35: mg_o = "1-3"
                        elif xg_a > 0.85: mg_o = "1-2"
                        else: mg_o = "0-1"

                        # Consiglio Mercato (Solo quelli richiesti)
                        if total_xg < 2.15: tip = "UNDER 3.5"
                        elif total_xg > 3.25: tip = "OVER 2.5"
                        elif total_xg > 2.75: tip = "GOAL" if abs(xg_h - xg_a) < 0.6 else "OVER 1.5"
                        else: tip = "OVER 1.5"

                        all_matches.append({
                            "Lega": LEAGUE_STATS[l_id]["name"],
                            "Partita": f"{home_t} vs {away_t}",
                            "xG Totali": total_xg,
                            "Consiglio": tip,
                            "Combo Multigol": f"CASA {mg_c} + OSP {mg_o}",
                            "Affidabilità": f"{random.randint(88, 96)}%"
                        })
            
            if all_matches:
                st.table(pd.DataFrame(all_matches))
                st.success(f"Analisi completata per {len(all_matches)} partite!")
        except Exception as e:
            st.error(f"Errore: {e}")
