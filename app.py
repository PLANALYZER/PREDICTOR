import streamlit as st
import requests
import pandas as pd
from datetime import datetime

# --- CONFIGURAZIONE ---
API_KEY = "adf7b41bd4a85edbf0d28b46c647b3d7"
HEADERS = {'x-rapidapi-key': API_KEY, 'x-rapidapi-host': 'v3.football.api-sports.io'}

# Leghe da analizzare
LEAGUES = {
    135: "Serie A", 136: "Serie B", 39: "Premier League", 
    78: "Bundesliga", 88: "Eredivisie", 140: "La Liga", 
    61: "Ligue 1", 207: "Super League (CH)", 208: "Challenge League"
}

st.set_page_config(page_title="XG PREDICTOR 16.03", layout="wide")

def get_real_stats(l_id, t_id):
    """Recupera le medie gol reali della stagione 2025/26"""
    try:
        url = f"https://v3.football.api-sports.io/teams/statistics?league={l_id}&season=2025&team={t_id}"
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
    st.title("🔐 Accesso 16.03.2026")
    pwd = st.text_input("Password", type="password")
    if st.button("SBLOCCA"):
        if pwd == "DAJE80":
            st.session_state["auth"] = True
            st.rerun()
    st.stop()

# --- INTERFACCIA ---
st.title("⚽ AI Predictor - Match del 16 Marzo 2026")

if st.button("🚀 ANALIZZA PARTITE DI OGGI"):
    with st.spinner('Calcolo xG in tempo reale...'):
        # Data impostata correttamente per oggi
        today = "2026-03-16"
        url_fix = f"https://v3.football.api-sports.io/fixtures?date={today}"
        
        try:
            res_fix = requests.get(url_fix, headers=HEADERS, timeout=10).json()
            results = []
            
            if 'response' in res_fix and res_fix['response']:
                fixtures = [f for f in res_fix['response'] if f['league']['id'] in LEAGUES]
                
                for f in fixtures:
                    l_id = f['league']['id']
                    h_n, h_id = f['teams']['home']['name'], f['teams']['home']['id']
                    a_n, a_id = f['teams']['away']['name'], f['teams']['away']['id']
                    
                    # 1. Recupero dati reali (GF = Gol Fatti, GS = Gol Subiti)
                    h_gf, h_gs = get_real_stats(l_id, h_id)
                    a_gf, a_gs = get_real_stats(l_id, a_id)
                    
                    # 2. Formula xG Incrociata (Normalizzata su media 1.25)
                    xg_h = (h_gf * a_gs) / 1.25
                    xg_a = (a_gf * h_gs) / 1.25
                    total_xg = round(xg_h + xg_a, 2)
                    
                    # 3. Filtro per squadre Under (Pisa, Cagliari, etc.)
                    if any(x in [h_n, a_n] for x in ["Cagliari", "Pisa", "Empoli"]):
                        total_xg = round(total_xg * 0.82, 2)

                    results.append({
                        "Lega": LEAGUES[l_id],
                        "Incontro": f"{h_n} vs {a_n}",
                        "xG Totale": total_xg,
                        "Pronostico": "UNDER 2.5" if total_xg < 2.25 else "OVER 1.5",
                        "Analisi": "MATCH CHIUSO" if total_xg < 1.90 else "ATTACCO FORTE" if total_xg > 2.80 else "EQUILIBRIO"
                    })
                
                if results:
                    st.table(pd.DataFrame(results).sort_values(by="xG Totale"))
                else:
                    st.warning("Nessun match trovato per le leghe selezionate in data odierna.")
            else:
                st.error("Errore di connessione all'API delle partite.")
        except Exception as e:
            st.error(f"Errore tecnico: {e}")
