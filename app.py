import streamlit as st
import requests
import pandas as pd
from datetime import datetime

# --- CONFIGURAZIONE ---
API_KEY = "adf7b41bd4a85edbf0d28b46c647b3d7"
HEADERS = {'x-rapidapi-key': API_KEY, 'x-rapidapi-host': 'v3.football.api-sports.io'}

# MEDIE GOL REALI PER CAMPIONATO (Fondamentali per la formula)
LEAGUE_DEFAULTS = {
    135: {"name": "Serie A", "avg": 1.22},
    136: {"name": "Serie B", "avg": 1.10},
    39: {"name": "Premier League", "avg": 1.45},
    78: {"name": "Bundesliga", "avg": 1.58},
    88: {"name": "Eredivisie", "avg": 1.62},
    140: {"name": "La Liga", "avg": 1.18},
    61: {"name": "Ligue 1", "avg": 1.20},
    207: {"name": "Super League (CH)", "avg": 1.40},
    208: {"name": "Challenge League", "avg": 1.48}
}

st.set_page_config(page_title="PROFESSIONAL xG ENGINE", layout="wide")

def get_stats(league_id, team_id):
    """Estrae i dati reali per alimentare la formula"""
    url = f"https://v3.football.api-sports.io/teams/statistics?league={league_id}&season=2025&team={team_id}"
    try:
        res = requests.get(url, headers=HEADERS).json()
        if 'response' in res and res['response']:
            stats = res['response']['goals']
            return float(stats['for']['average']['total']), float(stats['against']['average']['total'])
    except:
        pass
    return 1.10, 1.20

if "auth" not in st.session_state: st.session_state["auth"] = False
if not st.session_state["auth"]:
    pwd = st.text_input("Password", type="password")
    if st.button("SBLOCCA"):
        if pwd == "DAJE80": st.session_state["auth"] = True; st.rerun()
    st.stop()

st.title("🔬 AI Professional xG Predictor")

if st.button("🚀 GENERA ANALISI SCIENTIFICA"):
    url = f"https://v3.football.api-sports.io/fixtures?date={datetime.now().strftime('%Y-%m-%d')}"
    res_fix = requests.get(url, headers=HEADERS).json()
    
    if 'response' in res_fix:
        matches = []
        for f in res_fix['response']:
            l_id = f['league']['id']
            if l_id in LEAGUE_DEFAULTS:
                h_name, h_id = f['teams']['home']['name'], f['teams']['home']['id']
                a_name, a_id = f['teams']['away']['name'], f['teams']['away']['id']
                
                # DATI REALI
                h_gf, h_gs = get_stats(l_id, h_id)
                a_gf, a_gs = get_stats(l_id, a_id)
                l_avg = LEAGUE_DEFAULTS[l_id]["avg"]
                
                # FORMULA DI POISSON APPLICATA
                strength_h = (h_gf / l_avg) * (a_gs / l_avg)
                strength_a = (a_gf / l_avg) * (h_gs / l_avg)
                
                final_xg_h = l_avg * strength_h
                final_xg_a = l_avg * strength_a
                total_xg = round(final_xg_h + final_xg_a, 2)
                
                # FILTRO REALTÀ (Cagliari, Pisa, etc.)
                if h_gf < 0.8 or a_gf < 0.8: total_xg = round(total_xg * 0.85, 2)

                matches.append({
                    "Lega": LEAGUE_DEFAULTS[l_id]["name"],
                    "Partita": f"{h_name} vs {a_name}",
                    "Forza Casa": round(h_gf, 2),
                    "Forza Ospite": round(a_gf, 2),
                    "xG MATCH": total_xg,
                    "Picks": "UNDER 2.5" if total_xg < 2.25 else "OVER 2.5" if total_xg > 2.90 else "OVER 1.5"
                })
        
        if matches:
            st.table(pd.DataFrame(matches).sort_values(by="xG MATCH"))
