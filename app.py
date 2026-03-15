import streamlit as st
import requests
import pandas as pd
from datetime import datetime

# --- CONFIGURAZIONE API ---
API_KEY = "adf7b41bd4a85edbf0d28b46c647b3d7"
HEADERS = {'x-rapidapi-key': API_KEY, 'x-rapidapi-host': 'v3.football.api-sports.io'}

# DATABASE STATISTICO DINAMICO (Aggiustato sui dati reali)
# att: efficienza realizzativa | def: solidità/concessione occasioni
TEAM_POWER = {
    "Cagliari": {"att": 0.35, "def": 1.10},   # Precisione: Attacco molto basso
    "Pisa": {"att": 0.85, "def": 0.80},      # Squadra solida
    "Barcelona": {"att": 2.40, "def": 0.70},
    "Real Madrid": {"att": 2.50, "def": 0.60},
    "Manchester City": {"att": 2.70, "def": 0.50},
    "BSC Young Boys": {"att": 2.15, "def": 0.85},
    "Lazio": {"att": 1.15, "def": 0.90},
    "AC Milan": {"att": 1.80, "def": 1.10},
    "Juventus": {"att": 1.30, "def": 0.65},
    "Inter": {"att": 2.20, "def": 0.55}
}

LEAGUES = {
    135: "Serie A", 136: "Serie B", 39: "Premier League", 
    78: "Bundesliga", 88: "Eredivisie", 140: "La Liga", 
    61: "Ligue 1", 207: "Super League (CH)", 208: "Challenge League"
}

st.set_page_config(page_title="PRECISION xG PREDICTOR", layout="wide")

# --- LOGIN ---
if "auth" not in st.session_state:
    st.session_state["auth"] = False
if not st.session_state["auth"]:
    st.title("🔐 Accesso Analisi Scientifica")
    pwd = st.text_input("Password Licenza", type="password")
    if st.button("SBLOCCA"):
        if pwd == "DAJE80":
            st.session_state["auth"] = True
            st.rerun()
    st.stop()

st.title("📊 xG Totale Match - Analisi Differenziale")

if st.button("🚀 CALCOLA xG SCIENTIFICO"):
    with st.spinner('Incrociando Power Index Squadre...'):
        today = datetime.now().strftime('%Y-%m-%d')
        url = f"https://v3.football.api-sports.io/fixtures?date={today}"
        
        try:
            response = requests.get(url, headers=HEADERS).json()
            all_matches = []
            
            if 'response' in response and response['response']:
                for match in response['response']:
                    l_id = match['league']['id']
                    if l_id in LEAGUES:
                        h_name = match['teams']['home']['name']
                        a_name = match['teams']['away']['name']
                        
                        # Recupero indici (1.0 è il neutro per squadre non in database)
                        h_idx = TEAM_POWER.get(h_name, {"att": 0.95, "def": 1.05})
                        a_idx = TEAM_POWER.get(a_name, {"att": 0.90, "def": 1.10})
                        
                        # CALCOLO MATEMATICO XG TOTALE
                        # Incrocio Attacco A vs Difesa B + Attacco B vs Difesa A
                        base_match = 1.35
                        val_h = base_match * h_idx["att"] * a_idx["def"]
                        val_a = (base_match * 0.85) * a_idx["att"] * h_idx["def"]
                        
                        total_match_xg = round(val_h + val_a, 2)
                        
                        # --- CLASSIFICAZIONE RIGIDA ---
                        if total_match_xg < 1.95:
                            status = "🔴 BLINDATA (Strong Under)"
                        elif total_match_xg < 2.45:
                            status = "🟡 TATTICA (Under/Equilibrio)"
                        elif total_match_xg < 3.05:
                            status = "🟢 APERTA (Over 1.5)"
                        else:
                            status = "🔥 OFFENSIVA (Over 2.5)"

                        all_matches.append({
                            "Lega": LEAGUES[l_id],
                            "Partita": f"{h_name} vs {a_name}",
                            "xG TOTALE": total_match_xg,
                            "Analisi Tattica": status,
                            "Pronostico": "UNDER 2.5" if total_match_xg < 2.30 else "OVER 1.5"
                        })
            
            if all_matches:
                df = pd.DataFrame(all_matches).sort_values(by="xG TOTALE")
                st.table(df)
        except:
            st.error("Errore nel recupero dati API.")
