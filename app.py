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

st.set_page_config(page_title="REAL MATCH xG PRO", layout="wide")

def get_stats_safe(league_id, team_id):
    """Recupera dati reali. Se l'API fallisce, restituisce 1.0 per non bloccare il tasto."""
    try:
        url = f"https://v3.football.api-sports.io/teams/statistics?league={league_id}&season=2024&team={team_id}"
        res = requests.get(url, headers=HEADERS, timeout=5).json()
        if 'response' in res and res['response']:
            stats = res['response']['goals']
            gf = stats['for']['average']['total'] or 1.1
            gs = stats['against']['average']['total'] or 1.1
            return float(gf), float(gs)
    except:
        pass
    return 1.1, 1.2

if "auth" not in st.session_state: st.session_state["auth"] = False
if not st.session_state["auth"]:
    pwd = st.text_input("Password", type="password")
    if st.button("SBLOCCA"):
        if pwd == "DAJE80":
            st.session_state["auth"] = True
            st.rerun()
    st.stop()

st.title("📊 Calcolatore xG Reale (Versione Stabile)")

# AGGIUNTO IL TASTO CON CONTROLLO ERRORI
if st.button("🚀 GENERA ANALISI ORA"):
    with st.spinner('Analisi match in corso...'):
        today = datetime.now().strftime('%Y-%m-%d')
        url = f"https://v3.football.api-sports.io/fixtures?date={today}"
        
        try:
            response = requests.get(url, headers=HEADERS, timeout=10).json()
            all_matches = []
            
            if 'response' in response and response['response']:
                # Prendiamo solo i match delle tue leghe
                matches = [m for m in response['response'] if m['league']['id'] in LEAGUES]
                
                if not matches:
                    st.warning("Nessun match trovato per oggi in Serie A, B, Premier, etc.")
                else:
                    for m in matches[:25]: # Limite per evitare blocchi
                        l_id = m['league']['id']
                        h_id, h_name = m['teams']['home']['id'], m['teams']['home']['name']
                        a_id, a_name = m['teams']['away']['id'], m['teams']['away']['name']
                        
                        # Chiamata dati reali
                        h_gf, h_gs = get_stats_safe(l_id, h_id)
                        a_gf, a_gs = get_stats_safe(l_id, a_id)
                        
                        # Formula bilanciata (Media 1.25)
                        total_xg = round(((h_gf * a_gs) / 1.2
