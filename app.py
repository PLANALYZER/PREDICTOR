import streamlit as st
import requests
import pandas as pd
from datetime import datetime

# --- CONFIGURAZIONE CORE ---
API_KEY = "adf7b41bd4a85edbf0d28b46c647b3d7"
HEADERS = {'x-rapidapi-key': API_KEY, 'x-rapidapi-host': 'v3.football.api-sports.io'}

# Leghe monitorate con medie gol reali per calibrare la formula
LEAGUES = {
    135: "Serie A", 136: "Serie B", 39: "Premier League", 
    78: "Bundesliga", 88: "Eredivisie", 140: "La Liga", 
    61: "Ligue 1", 207: "Super League (CH)", 208: "Challenge League"
}

st.set_page_config(page_title="REAL XG PRECISION", layout="wide")

def get_stats(league_id, team_id):
    """Estrae i gol medi reali. Se i dati mancano, restituisce 1.0 per non bloccare il sistema."""
    url = f"https://v3.football.api-sports.io/teams/statistics?league={league_id}&season=2024&team={team_id}"
    try:
        res = requests.get(url, headers=HEADERS, timeout=5).json()
        if 'response' in res and res['response']:
            g = res['response']['goals']
            gf = float(g['for']['average']['total']) if g['for']['average']['total'] else 1.0
            gs = float(g['against']['average']['total']) if g['against']['average']['total'] else 1.0
            return gf, gs
    except:
        pass
    return 1.0, 1.1

# --- LOGIN ---
if "auth" not in st.session_state: st.session_state["auth"] = False
if not st.session_state["auth"]:
    pwd = st.text_input("Password Licenza", type="password")
    if st.button("SBLOCCA"):
        if pwd == "DAJE80":
            st.session_state["auth"] = True
            st.rerun()
    st.stop()

# --- INTERFACCIA ---
st.title("⚽ AI Real-Stats xG Predictor")

if st.button("🚀 GENERA ANALISI SCIENTIFICA"):
    with st.spinner('Lettura dati reali squadre in corso...'):
        today = datetime.now().strftime('%Y-%m-%d')
        url = f"https://v3.football.api-sports.io/fixtures?date={today}"
        
        try:
            response = requests.get(url, headers=HEADERS, timeout=10).json()
            all_results = []
            
            if 'response' in response and response['response']:
                fixtures = [f for f in response['response'] if f['league']['id'] in LEAGUES]
                
                for f in fixtures[:20]: # Limite per stabilità
                    l_id = f['league']['id']
                    h_id, h_n = f['teams']['home']['id'], f['teams']['home']['name']
                    a_id, a_n = f['teams']['away']['id'], f['teams']['away']['name']
                    
                    # Recupero dati reali
                    h_gf, h_gs = get_stats(l_id, h_id)
                    a_gf, a_gs = get_stats(l_id, a_id)
                    
                    # Formula xG: (Attacco Casa * Difesa Ospite) + (Attacco Ospite * Difesa Casa)
                    # Diviso per un coefficiente di normalizzazione (1.2)
                    xg_h = (h_gf * a_gs) / 1.2
                    xg_a = (a_gf * h_gs) / 1.2
                    total_xg = round(

