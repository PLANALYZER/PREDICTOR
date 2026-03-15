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

st.set_page_config(page_title="AI REAL STATS xG", layout="wide")

# Funzione per ottenere le medie reali della stagione
def get_team_stats(league_id, team_id, season=2025):
    url = f"https://v3.football.api-sports.io/teams/statistics?league={league_id}&season={season}&team={team_id}"
    res = requests.get(url, headers=HEADERS).json()
    if 'response' in res:
        stats = res['response']['goals']
        # Media Gol Fatti e Subiti (Totali stagionali)
        gf = stats['for']['average']['total']
        gs = stats['against']['average']['total']
        return float(gf), float(gs)
    return 1.0, 1.0

if "auth" not in st.session_state: st.session_state["auth"] = False
if not st.session_state["auth"]:
    pwd = st.text_input("Password", type="password")
    if st.button("SBLOCCA"):
        if pwd == "DAJE80":
            st.session_state["auth"] = True
            st.rerun()
    st.stop()

st.title("⚽ Calcolo xG Reale basato su Stats API")

if st.button("🚀 ANALIZZA DATI REALI SQUADRE"):
    today = datetime.now().strftime('%Y-%m-%d')
    url_fixtures = f"https://v3.football.api-sports.io/fixtures?date={today}"
    
    with st.spinner('Interrogando il database storico delle squadre...'):
        res_fix = requests.get(url_fixtures, headers=HEADERS).json()
        all_matches = []
        
        if 'response' in res_fix:
            # Filtriamo per le tue leghe
            valid_fixtures = [f for f in res_fix['response'] if f['league']['id'] in LEAGUES]
            
            for f in valid_fixtures[:15]: # Limitiamo a 15 per velocità di test
                l_id = f['league']['id']
                h_id = f['teams']['home']['id']
                a_id = f['teams']['away']['id']
                h_name = f['teams']['home']['name']
                a_name = f['teams']['away']['name']
                
                # CHIAMATA STATS REALI
                h_gf, h_gs = get_team_stats(l_id, h_id)
                a_gf, a_gs = get_team_stats(l_id, a_id)
                
                # LOGICA REALE:
                # xG Casa = (Attacco Casa * Difesa Ospite) / Media (approssimata)
                # xG Ospite = (Attacco Ospite * Difesa Casa) / Media (approssimata)
                xg_h = (h_gf * a_gs) / 1.2
                xg_a = (a_gf * h_gs) / 1.2
                total_xg = round(xg_h + xg_a, 2)
                
                # Correzione Cagliari (Esempio forza offensiva reale)
                if h_name == "Cagliari" or a_name == "Cagliari":
                    total_xg = round(total_xg * 0.8, 2) 

                all_matches.append({
                    "Lega": LEAGUES[l_id],
                    "Partita": f"{h_name} vs {a_name}",
                    "GF Media Casa": h_gf,
                    "GF Media Ospite": a_gf,
                    "xG TOTALE": total_xg,
                    "Pronostico": "UNDER 2.5" if total_xg < 2.35 else "OVER 1.5"
                })

            if all_matches:
                st.table(pd.DataFrame(all_matches))
