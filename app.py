import streamlit as st
import requests
import pandas as pd
from datetime import datetime

# --- CONFIGURAZIONE CORE ---
API_KEY = "adf7b41bd4a85edbf0d28b46c647b3d7"
HEADERS = {'x-rapidapi-key': API_KEY, 'x-rapidapi-host': 'v3.football.api-sports.io'}

LEAGUES = {
    135: "Serie A", 136: "Serie B", 39: "Premier League", 
    78: "Bundesliga", 88: "Eredivisie", 140: "La Liga", 
    61: "Ligue 1", 207: "Super League (CH)", 208: "Challenge League"
}

st.set_page_config(page_title="REAL STATS xG PRO", layout="wide")

def get_real_data(league_id, team_id):
    """Estrae la media gol reale delle ultime 10 partite dal database API"""
    url = f"https://v3.football.api-sports.io/fixtures?league={league_id}&season=2025&team={team_id}&last=10"
    try:
        res = requests.get(url, headers=HEADERS).json()
        if 'response' in res and res['response']:
            g_fatti = 0
            g_subiti = 0
            count = len(res['response'])
            for match in res['response']:
                is_home = match['teams']['home']['id'] == team_id
                side = 'home' if is_home else 'away'
                opp_side = 'away' if is_home else 'home'
                g_fatti += match['goals'][side] if match['goals'][side] is not None else 0
                g_subiti += match['goals'][opp_side] if match['goals'][opp_side] is not None else 0
            return round(g_fatti / count, 2), round(g_subiti / count, 2)
    except:
        pass
    return 1.15, 1.25 # Fallback realistico in caso di errore dati

if "auth" not in st.session_state: st.session_state["auth"] = False
if not st.session_state["auth"]:
    pwd = st.text_input("Password Licenza", type="password")
    if st.button("SBLOCCA"):
        if pwd == "DAJE80":
            st.session_state["auth"] = True
            st.rerun()
    st.stop()

st.title("⚽ Calcolo xG basato su Medie Gol Reali (Last 10)")

if st.button("🚀 AVVIA ANALISI SCIENTIFICA"):
    today = datetime.now().strftime('%Y-%m-%d')
    url_fixtures = f"https://v3.football.api-sports.io/fixtures?date={today}"
    
    with st.spinner('Scansione database squadre e medie gol...'):
        res_fix = requests.get(url_fixtures, headers=HEADERS).json()
        final_list = []
        
        if 'response' in res_fix:
            fixtures = [f for f in res_fix['response'] if f['league']['id'] in LEAGUES]
            
            for f in fixtures:
                l_id = f['league']['id']
                h_name, h_id = f['teams']['home']['name'], f['teams']['home']['id']
                a_name, a_id = f['teams']['away']['name'], f['teams']['away']['id']
                
                # Prendi dati reali di forma
                h_fatti, h_subiti = get_real_data(l_id, h_id)
                a_fatti, a_subiti = get_real_data(l_id, a_id)
                
                # Calcolo xG reale incrociato (Normalizzato a 1.2 per evitare 'follia')
                # (Attacco Casa * Difesa Ospite) + (Attacco Ospite * Difesa Casa)
                xg_h = (h_fatti * a_subiti) / 1.22
                xg_a = (a_fatti * h_subiti) / 1.22
                total_xg = round(xg_h + xg_a, 2)
                
                # Correzione Cagliari/Pisa (Squadre storicamente da Under)
                if any(x in [h_name, a_name] for x in ["Cagliari", "Pisa", "Sudtirol"]):
                    total_xg = round(total_xg * 0.82, 2)

                final_list.append({
                    "Lega": LEAGUES[l_id],
                    "Match": f"{h_name} vs {a_name}",
                    "Attacco Casa (Media)": h_fatti,
                    "Attacco Ospite (Media)": a_fatti,
                    "xG TOTALE": total_xg,
                    "Pronostico": "UNDER 2.5" if total_xg < 2.30 else "OVER 1.5"
                })

            if final_list:
                st.table(pd.DataFrame(final_list).sort_values(by="xG TOTALE"))
            else:
                st.warning("Nessun match trovato per i campionati selezionati.")
