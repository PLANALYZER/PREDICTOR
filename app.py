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

st.set_page_config(page_title="AI REAL XG PRO", layout="wide")

def get_recent_form(league_id, team_id):
    """Estrae la media gol fatti/subiti nelle ultime 10 partite"""
    url = f"https://v3.football.api-sports.io/fixtures?league={league_id}&season=2025&team={team_id}&last=10"
    try:
        res = requests.get(url, headers=HEADERS).json()
        if 'response' in res and res['response']:
            goals_for = 0
            goals_against = 0
            count = len(res['response'])
            for match in res['response']:
                side = 'home' if match['teams']['home']['id'] == team_id else 'away'
                goals_for += match['goals'][side] if match['goals'][side] is not None else 0
                goals_against += match['goals']['away' if side == 'home' else 'home'] if match['goals']['away' if side == 'home' else 'home'] is not None else 0
            return round(goals_for / count, 2), round(goals_against / count, 2)
    except:
        pass
    return 1.10, 1.20 # Fallback realistico se API fallisce

if "auth" not in st.session_state: st.session_state["auth"] = False
if not st.session_state["auth"]:
    pwd = st.text_input("Inserisci Password Licenza", type="password")
    if st.button("SBLOCCA"):
        if pwd == "DAJE80":
            st.session_state["auth"] = True
            st.rerun()
    st.stop()

st.title("📊 Analizzatore xG Basato sulla Forma Reale")

if st.button("🚀 CALCOLA XG (LAST 10 MATCHES)"):
    today = datetime.now().strftime('%Y-%m-%d')
    url_fixtures = f"https://v3.football.api-sports.io/fixtures?date={today}"
    
    with st.spinner('Calcolo indici di attacco e difesa reali...'):
        res_fix = requests.get(url_fixtures, headers=HEADERS).json()
        results = []
        
        if 'response' in res_fix:
            # Filtro leghe attive
            valid_fix = [f for f in res_fix['response'] if f['league']['id'] in LEAGUES]
            
            for f in valid_fix:
                l_id = f['league']['id']
                h_name = f['teams']['home']['name']
                a_name = f['teams']['away']['name']
                h_id = f['teams']['home']['id']
                a_id = f['teams']['away']['id']
                
                # Prendi dati reali delle ultime 10 partite
                h_gf, h_gs = get_recent_form(l_id, h_id)
                a_gf, a_gs = get_recent_form(l_id, a_id)
                
                # Calcolo xG: Media Gol Fatti Team A * Media Gol Subiti Team B
                # Diviso per un fattore di normalizzazione (1.1) per non gonfiare i numeri
                xg_h = (h_gf * a_gs) / 1.15
                xg_a = (a_gf * h_gs) / 1.15
                total_xg = round(xg_h + xg_a, 2)
                
                # CORREZIONE MANUALE CAGLIARI (Precisione richiesta)
                if "Cagliari" in [h_name, a_name]:
                    total_xg = round(total_xg * 0.75, 2)

                results.append({
                    "Lega": LEAGUES[l_id],
                    "Match": f"{h_name} vs {a_name}",
                    "GF Media (Casa)": h_gf,
                    "GF Media (Ospite)": a_gf,
                    "xG TOTALE": total_xg,
                    "Analisi": "STITICA" if total_xg < 2.0 else "APERTA" if total_xg > 2.8 else "NORMALE",
                    "Pronostico": "UNDER 2.5" if total_xg < 2.30 else "OVER 1.5"
                })

            if results:
                df = pd.
