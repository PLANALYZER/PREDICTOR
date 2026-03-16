import streamlit as st
import requests
import pandas as pd
from datetime import datetime

# --- CONFIGURAZIONE ---
API_KEY = "adf7b41bd4a85edbf0d28b46c647b3d7"
HEADERS = {'x-rapidapi-key': API_KEY, 'x-rapidapi-host': 'v3.football.api-sports.io'}

LEAGUES = {
    135: "Serie A", 136: "Serie B", 39: "Premier League", 
    78: "Bundesliga", 88: "Eredivisie", 140: "La Liga", 
    61: "Ligue 1", 207: "Super League (CH)", 208: "Challenge League"
}

st.set_page_config(page_title="REAL XG PREDICTOR", layout="wide")

def get_stats(l_id, t_id):
    """Prende la media gol reale della stagione corrente"""
    try:
        url = f"https://v3.football.api-sports.io/teams/statistics?league={l_id}&season=2024&team={t_id}"
        res = requests.get(url, headers=HEADERS, timeout=5).json()
        if 'response' in res and res['response']:
            g = res['response']['goals']
            gf = float(g['for']['average']['total']) if g['for']['average']['total'] else 1.1
            gs = float(g['against']['average']['total']) if g['against']['average']['total'] else 1.1
            return gf, gs
    except:
        pass
    return 1.1, 1.2

# --- LOGIN ---
if "auth" not in st.session_state:
    st.session_state["auth"] = False

if not st.session_state["auth"]:
    st.title("🔐 Accesso")
    pwd = st.text_input("Password", type="password")
    if st.button("SBLOCCA"):
        if pwd == "DAJE80":
            st.session_state["auth"] = True
            st.rer
