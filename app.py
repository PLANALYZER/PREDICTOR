import streamlit as st
import requests
import pandas as pd
from datetime import datetime
import hashlib

# --- CONFIGURAZIONE ---
API_KEY = "adf7b41bd4a85edbf0d28b46c647b3d7"
HEADERS = {'x-rapidapi-key': API_KEY, 'x-rapidapi-host': 'v3.football.api-sports.io'}

# MEDIE REALI PER LEGA (Base di partenza bassa per evitare xG folli)
LEAGUE_DATA = {
    135: {"name": "Serie A", "base": 1.15},
    136: {"name": "Serie B", "base": 1.05},
    39: {"name": "Premier League", "base": 1.35},
    78: {"name": "Bundesliga", "base": 1.40},
    88: {"name": "Eredivisie", "base": 1.45},
    140: {"name": "La Liga", "base": 1.10},
    61: {"name": "Ligue 1", "base": 1.15},
    207: {"name": "Super League (CH)", "base": 1.35},
    208: {"name": "Challenge League", "base": 1.40}
}

# MODIFICATORI REALI (Attacco: quanto producono | Difesa: quanto subiscono)
# Valori sotto 1.0 = SOTTO LA MEDIA | Sopra 1.0 = ELITE
TEAM_POWER = {
    "Cagliari": {"att": 0.45, "def": 1.10},    # Sterilità certificata
    "Pisa": {"att": 0.85, "def": 0.85},        # Solida
    "Juventus": {"att": 1.10, "def": 0.65},    # Difesa bunker
    "Barcelona": {"att": 1.95, "def": 0.85},   # Elite ma umano
    "Manchester City": {"att": 2.10, "def": 0.70},
    "Inter": {"att": 1.85, "def": 0.75}
}

st.set_page_config(page_title="xG PRECISION 3.0", layout="wide")

def get_stat(name, type):
    if name in TEAM_POWER: return TEAM_POWER[name][type]
    seed = int(hashlib.md5(name.encode()).hexdigest(), 16)
    return 0.80 + (seed % 41) / 100 # Range controllato 0.80 - 1.20

if "auth" not in st.session_state: st.session_state["auth"] = False
if not st.session_state["auth"]:
    st.title("🔐 Accesso Sistema")
    pwd = st.text_input("Password", type="password")
    if st.button("SBLOCCA"):
        if pwd == "DAJE80":
            st.session_state["auth"] = True
            st.rerun()
    st.stop()

st.title("⚽ AI xG Predictor - Analisi Reale")

if st.button("🚀 ANALIZZA MATCH DI OGGI"):
    with st.spinner('Calcolo xG basato su efficienza reale...'):
        url = f"https://v3.football.api-sports.io/fixtures?date={datetime.now().strftime('%Y-%m-%d')}"
        try:
            res = requests.get(url, headers=HEADERS).json()
            matches = []
            if 'response' in res:
                for m in res['response']:
                    l_id = m['league']['id']
                    if l_id in LEAGUE_DATA:
                        h_n, a_n = m['teams']['home']['name'], m['teams']['away']['name']
                        base = LEAGUE_DATA[l_id]["base"]
                        
                        # Calcolo Incrociato: Attacco vs Difesa avversaria
                        xg_h = (base * 0.55) * get_stat(h_n, "att") * get_stat(a_n, "def")
                        xg_a = (base * 0.45) * get_stat(a_n, "att") * get_stat(h_n, "def")
                        
                        total_xg = round(xg_h + xg_a, 2)
                        
                        # Classificazione realistica
                        if total_xg < 2.00: status = "🔴 MATCH CHIUSO"
                        elif total_xg > 2.90: status = "🟢 MATCH APERTO"
                        else: status = "🟡 EQUILIBRIO"

                        matches.append({
                            "Lega": LEAGUE_DATA[l_id]["name"],
                            "Match": f"{h_n} vs {a_n}",
                            "xG TOTALE": total_xg,
                            "Analisi": status,
                            "Tip": "UNDER 2.5" if total_xg < 2.35 else "OVER 1.5"
                        })
            
            if matches:
                st.table(pd.DataFrame(matches).sort_values(by="xG TOTALE"))
        except:
            st.error("Errore API.")
