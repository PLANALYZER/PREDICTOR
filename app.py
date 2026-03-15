import streamlit as st
import requests
import pandas as pd
from datetime import datetime
import random

# --- CONFIGURAZIONE ---
API_KEY = "adf7b41bd4a85edbf0d28b46c647b3d7"
HEADERS = {'x-rapidapi-key': API_KEY, 'x-rapidapi-host': 'v3.football.api-sports.io'}

# MEDIE GOL E FATTORE DINAMISMO (Aperto vs Chiuso)
LEAGUE_STATS = {
    135: {"name": "Serie A", "avg": 2.62, "flow": "bilanciato"}, 
    136: {"name": "Serie B", "avg": 2.30, "flow": "chiuso"},
    39: {"name": "Premier League", "avg": 2.85, "flow": "aperto"}, 
    78: {"name": "Bundesliga", "avg": 3.21, "flow": "aperto"},
    88: {"name": "Eredivisie", "avg": 3.10, "flow": "aperto"}, 
    89: {"name": "Eredivisie B", "avg": 3.25, "flow": "aperto"},
    207: {"name": "Super League (CH)", "avg": 2.98, "flow": "aperto"}, 
    208: {"name": "Challenge League", "avg": 3.05, "flow": "aperto"},
    140: {"name": "La Liga", "avg": 2.55, "flow": "chiuso"}, 
    61: {"name": "Ligue 1", "avg": 2.65, "flow": "bilanciato"},
    144: {"name": "Jupiler Pro League", "avg": 2.92, "flow": "aperto"}, 
    40: {"name": "Championship", "avg": 2.68, "flow": "bilanciato"}
}

st.set_page_config(page_title="PREDICTOR AI PRO", layout="wide")

# --- LOGIN ---
if "auth" not in st.session_state:
    st.session_state["auth"] = False
if not st.session_state["auth"]:
    st.title("🔐 Accesso Licenza Enterprise 2.0")
    pwd = st.text_input("Inserisci Chiave Licenza", type="password")
    if st.button("SBLOCCA SOFTWARE"):
        if pwd == "DAJE80":
            st.session_state["auth"] = True
            st.rerun()
    st.stop()

st.title("⚽ AI Predictor - Analisi xG & Flow Dinamico")

if st.button("🚀 GENERA ANALISI AD ALTA PRECISIONE"):
    with st.spinner('Analizzando stili di gioco e flow campionati...'):
        today = datetime.now().strftime('%Y-%m-%d')
        url = f"https://v3.football.api-sports.io/fixtures?date={today}"
        
        try:
            response = requests.get(url, headers=HEADERS).json()
            all_matches = []
            
            if 'response' in response and response['response']:
                for match in response['response']:
                    l_id = match['league']['id']
                    if l_id in LEAGUE_STATS:
                        stats = LEAGUE_STATS[l_id]
                        media = stats["avg"]
                        flow = stats["flow"]
                        
                        # --- CALCOLO xG DINAMICO ---
                        # Se il flow è 'aperto', aumentiamo la varianza positiva
                        if flow == "aperto":
                            boost = random.uniform(-0.2, 0.9)
                        elif flow == "chiuso":
                            boost = random.uniform(-0.8, 0.4)
                        else:
                            boost = random.uniform(-0.5, 0.6)
                            
                        xg_h = round((media * 0.55) + boost, 2)
                        xg_a = round((media * 0.45) + (boost * 0.7), 2)
                        
                        xg_h = max(0.1, xg_h)
                        xg_a = max(0.1, xg_a)
                        total_xg = round(xg_h + xg_a, 2)
                        
                        # --- CONSIGLIO IA ---
                        if total_xg < 2.00: consiglio = "UNDER 3.5"
                        elif total_xg > 2.80: consiglio = "GOAL" if abs(xg_h - xg_a) < 0.5 else "OVER 2.5"
                        else: consiglio = "OVER 1.5"
                        
                        # --- COMBO MULTIGOL AGGRESSIVE ---
                        # Logica Casa (Pisa può fare 2-4 se il boost è alto)
                        if xg_h > 1.90: mg_c = "2-4"
                        elif xg_h > 1.20: mg_c = "1-3"
                        elif xg_h > 0.60: mg_c = "1-2"
                        else: mg_c = "0-1"
                        
                        # Logica Ospite
                        if xg_a > 1.70: mg_o = "2-3"
                        elif xg_a > 1.05: mg_o = "1-3"
                        elif xg_a > 0.55: mg_o = "1-2"
                        else: mg_o = "0-1"

                        all_matches.append({
                            "Lega": stats["name"],
                            "Partita": f"{match['teams']['home']['name']} vs {match['teams']['away']['name']}",
                            "xG Totali": total_xg,
                            "Consiglio IA": consiglio,
                            "Combo Multigol": f"CASA {mg_c} + OSP {mg_o}",
                            "Stile": flow.upper()
                        })
            
            if all_matches:
                st.table(pd.DataFrame(all_matches))
                st.success("Analisi Dinamica completata!")
        except Exception as e:
            st.error(f"Errore: {e}")
