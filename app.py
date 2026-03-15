import streamlit as st
import requests
import pandas as pd
from datetime import datetime

# --- CONFIGURAZIONE ---
API_KEY = "adf7b41bd4a85edbf0d28b46c647b3d7"
HEADERS = {'x-rapidapi-key': API_KEY, 'x-rapidapi-host': 'v3.football.api-sports.io'}

# ID Leghe e Medie Gol storiche per calcolare la Forza Relativa
LEAGUE_STATS = {
    135: {"name": "Serie A", "avg_gf": 1.28},
    136: {"name": "Serie B", "avg_gf": 1.15},
    39: {"name": "Premier League", "avg_gf": 1.42},
    78: {"name": "Bundesliga", "avg_gf": 1.55},
    88: {"name": "Eredivisie", "avg_gf": 1.60},
    140: {"name": "La Liga", "avg_gf": 1.25},
    61: {"name": "Ligue 1", "avg_gf": 1.22},
    207: {"name": "Super League (CH)", "avg_gf": 1.48},
    208: {"name": "Challenge League", "avg_gf": 1.52}
}

st.set_page_config(page_title="REAL STATS xG PREDICTOR", layout="wide")

def get_real_team_stats(league_id, team_id):
    """Estrae i gol medi fatti e subiti reali dall'API"""
    url = f"https://v3.football.api-sports.io/teams/statistics?league={league_id}&season=2024&team={team_id}"
    try:
        res = requests.get(url, headers=HEADERS).json()
        if 'response' in res and res['response']:
            goals = res['response']['goals']
            gf_avg = goals['for']['average']['total']
            gs_avg = goals['against']['average']['total']
            return float(gf_avg), float(gs_avg)
    except:
        pass
    return 1.0, 1.0 # Fallback neutro se i dati mancano

if "auth" not in st.session_state: st.session_state["auth"] = False
if not st.session_state["auth"]:
    pwd = st.text_input("Inserisci Password", type="password")
    if st.button("SBLOCCA"):
        if pwd == "DAJE80":
            st.session_state["auth"] = True
            st.rerun()
    st.stop()

st.title("📊 Calcolo xG basato su Forza Offensiva/Difensiva Reale")

if st.button("🚀 ANALIZZA MATCH CON DATI REALI"):
    today = datetime.now().strftime('%Y-%m-%d')
    url_fixtures = f"https://v3.football.api-sports.io/fixtures?date={today}"
    
    with st.spinner('Lettura dati storici API in corso...'):
        res_fix = requests.get(url_fixtures, headers=HEADERS).json()
        all_results = []
        
        if 'response' in res_fix:
            fixtures = [f for f in res_fix['response'] if f['league']['id'] in LEAGUE_STATS]
            
            for f in fixtures[:20]: # Analisi dei primi 20 match per evitare timeout
                l_id = f['league']['id']
                h_id, h_name = f['teams']['home']['id'], f['teams']['home']['name']
                a_id, a_name = f['teams']['away']['id'], f['teams']['away']['name']
                
                # 1. Recupero medie gol reali del team
                h_gf, h_gs = get_real_team_stats(l_id, h_id)
                a_gf, a_gs = get_real_team_stats(l_id, a_id)
                
                # 2. Calcolo Forza Relativa rispetto alla media Lega
                league_avg = LEAGUE_STATS[l_id]["avg_gf"]
                
                # Attacco Casa vs Difesa Ospite
                attack_strength_h = h_gf / league_avg
                defense_weakness_a = a_gs / league_avg
                exp_goals_h = league_avg * attack_strength_h * defense_weakness_a
                
                # Attacco Ospite vs Difesa Casa
                attack_strength_a = a_gf / league_avg
                defense_weakness_h = h_gs / league_avg
                exp_goals_a = league_avg * attack_strength_a * defense_weakness_h
                
                total_xg = round(exp_goals_h + exp_goals_a, 2)
                
                all_results.append({
                    "Lega": LEAGUE_STATS[l_id]["name"],
                    "Match": f"{h_name} vs {a_name}",
                    "Forza Att. Casa": round(h_gf, 2),
                    "Forza Att. Ospite": round(a_gf, 2),
                    "xG TOTALE": total_xg,
                    "Pronostico": "UNDER 2.5" if total_xg < 2.30 else "OVER 1.5"
                })

            if all_results:
                df = pd.DataFrame(all_results).sort_values(by="xG TOTALE")
                st.table(df)
