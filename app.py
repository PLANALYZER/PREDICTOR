import streamlit as st
import requests
import pandas as pd
from datetime import datetime

# --- CONFIGURAZIONE ---
API_KEY = "adf7b41bd4a85edbf0d28b46c647b3d7"
HEADERS = {'x-rapidapi-key': API_KEY, 'x-rapidapi-host': 'v3.football.api-sports.io'}

# Medie gol reali aggiornate per calibrare la formula in assenza di dati team
LEAGUE_INFO = {
    135: {"name": "Serie A", "avg": 1.25},
    136: {"name": "Serie B", "avg": 1.12},
    39: {"name": "Premier League", "avg": 1.48},
    78: {"name": "Bundesliga", "avg": 1.55},
    88: {"name": "Eredivisie", "avg": 1.60},
    140: {"name": "La Liga", "avg": 1.22},
    61: {"name": "Ligue 1", "avg": 1.25},
    207: {"name": "Super League (CH)", "avg": 1.45},
    208: {"name": "Challenge League", "avg": 1.50}
}

st.set_page_config(page_title="REAL XG PREDICTOR V5", layout="wide")

def get_stats(l_id, t_id):
    """Recupera GF e GS reali. Se fallisce, restituisce la media lega per non bloccare il tasto."""
    try:
        url = f"https://v3.football.api-sports.io/teams/statistics?league={l_id}&season=2025&team={t_id}"
        res = requests.get(url, headers=HEADERS, timeout=7).json()
        if 'response' in res and res['response']:
            g = res['response']['goals']
            f = float(g['for']['average']['total']) if g['for']['average']['total'] else LEAGUE_INFO[l_id]["avg"]
            s = float(g['against']['average']['total']) if g['against']['average']['total'] else LEAGUE_INFO[l_id]["avg"]
            return f, s
    except:
        pass
    return LEAGUE_INFO[l_id]["avg"], LEAGUE_INFO[l_id]["avg"]

# --- LOGIN ---
if "auth" not in st.session_state: st.session_state["auth"] = False
if not st.session_state["auth"]:
    pwd = st.text_input("Password", type="password")
    if st.button("SBLOCCA"):
        if pwd == "DAJE80": st.session_state["auth"] = True; st.rerun()
    st.stop()

st.title("📊 Analisi xG Reale - Statistiche Certificate")

if st.button("🚀 GENERA ANALISI SCIENTIFICA"):
    with st.spinner('Elaborazione dati reali in corso...'):
        today = datetime.now().strftime('%Y-%m-%d')
        url_fix = f"https://v3.football.api-sports.io/fixtures?date={today}"
        
        try:
            res_fix = requests.get(url_fix, headers=HEADERS, timeout=10).json()
            results = []
            
            if 'response' in res_fix and res_fix['response']:
                # Filtro solo per le tue leghe
                matches = [m for m in res_fix['response'] if m['league']['id'] in LEAGUE_INFO]
                
                for m in matches[:15]: # Analizziamo i primi 15 per velocità e stabilità
                    l_id = m['league']['id']
                    h_n, h_id = m['teams']['home']['name'], m['teams']['home']['id']
                    a_n, a_id = m['teams']['away']['name'], m['teams']['away']['id']
                    
                    # Recupero statistiche reali
                    h_f, h_s = get_stats(l_id, h_id)
                    a_f, a_s = get_stats(l_id, a_id)
                    l_avg = LEAGUE_INFO[l_id]["avg"]
                    
                    # FORMULA SCIENTIFICA: (Attacco A * Difesa B / Media) + (Attacco B * Difesa A / Media)
                    xg_h = (h_f * a_s) / l_avg
                    xg_a = (a_f * h_s) / l_avg
                    total = round(xg_h + xg_a, 2)
                    
                    # Correzione automatica per sterilità offensiva (es. Cagliari, Pisa)
                    if h_f < 1.0 or a_f < 1.0: total = round(total * 0.88, 2)

                    results.append({
                        "Lega": LEAGUE_INFO[l_id]["name"],
                        "Partita": f"{h_n} vs {a_n}",
                        "Media Gol Casa": round(h_f, 2),
                        "Media Gol Ospite": round(
