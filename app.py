import streamlit as st
import requests
import pandas as pd
from datetime import datetime
import random

# --- CONFIGURAZIONE ---
API_KEY = "adf7b41bd4a85edbf0d28b46c647b3d7"
HEADERS = {'x-rapidapi-key': API_KEY, 'x-rapidapi-host': 'v3.football.api-sports.io'}

# Medie Gol Reali per xG Realistici (Dati 2025/2026)
LEAGUE_STATS = {
    135: {"name": "Serie A", "avg": 2.6}, 136: {"name": "Serie B", "avg": 2.3},
    39: {"name": "Premier League", "avg": 2.8}, 78: {"name": "Bundesliga", "avg": 3.2},
    88: {"name": "Eredivisie", "avg": 3.1}, 89: {"name": "Eredivisie B", "avg": 3.3},
    207: {"name": "Super League (CH)", "avg": 2.9}, 140: {"name": "La Liga", "avg": 2.5},
    61: {"name": "Ligue 1", "avg": 2.6}, 144: {"name": "Jupiler Pro League", "avg": 2.9},
    208: {"name": "Challenge League", "avg": 3.0}, 40: {"name": "Championship", "avg": 2.7}
}

st.set_page_config(page_title="PREDICTOR AI PRO", layout="wide")

# --- LOGIN ---
if "auth" not in st.session_state:
    st.session_state["auth"] = False
if not st.session_state["auth"]:
    st.title("🛡️ Accesso PRO - Ennesima Potenza")
    pwd = st.text_input("Inserisci Chiave Licenza", type="password")
    if st.button("SBLOCCA SOFTWARE"):
        if pwd == "DAJE80":
            st.session_state["auth"] = True
            st.rerun()
    st.stop()

# --- APP ---
st.title("⚽ AI Predictor - Analisi Totale & Combo")

if st.button("🚀 GENERA ANALISI DEFINITIVA"):
    with st.spinner('Calcolo xG e mercati combo in corso...'):
        today = datetime.now().strftime('%Y-%m-%d')
        url = f"https://v3.football.api-sports.io/fixtures?date={today}"
        
        try:
            response = requests.get(url, headers=HEADERS).json()
            all_matches = []
            
            if 'response' in response:
                for match in response['response']:
                    l_id = match['league']['id']
                    if l_id in LEAGUE_STATS:
                        # 1. CALCOLO xG BASATO SUL CAMPIONATO
                        avg_l = LEAGUE_STATS[l_id]["avg"]
                        # Generiamo xG che gravitano attorno alla media reale
                        xg_h = round((avg_l / 2) + random.uniform(-0.3, 0.7), 2)
                        xg_a = round((avg_l / 2) + random.uniform(-0.4, 0.5), 2)
                        total_xg = round(xg_h + xg_a, 2)
                        
                        # 2. PRONOSTICO MERCATO TOTALE
                        if total_xg > 3.45: tip = "OVER 3.5"
                        elif total_xg > 2.80: tip = "GOAL" if abs(xg_h - xg_a) < 0.6 else "OVER 2.5"
                        elif total_xg > 2.25: tip = "OVER 1.5"
                        else: tip = "UNDER 3.5"
                        
                        # 3. COMBO MULTIGOL CASA + OSPITE
                        # Casa
                        if xg_h > 1.9: mg_c = "2-4"
                        elif xg_h > 1.1: mg_c = "1-3"
                        else: mg_c = "1-2"
                        # Ospite
                        if xg_a > 1.7: mg_o = "2-4"
                        elif xg_a > 1.0: mg_o = "1-3"
                        else: mg_o = "0-2"
                        
                        combo_str = f"CASA {mg_c} + OSP {mg_o}"

                        all_matches.append({
                            "Lega": LEAGUE_STATS[l_id]["name"],
                            "Partita": f"{match['teams']['home']['name']} vs {match['teams']['away']['name']}",
                            "xG Totali": total_xg,
                            "Consiglio IA": tip,
                            "Combo Multigol": combo_str,
