import streamlit as st
import requests
import pandas as pd
from datetime import datetime

# --- CONFIGURAZIONE API ---
API_KEY = "adf7b41bd4a85edbf0d28b46c647b3d7"
HEADERS = {'x-rapidapi-key': API_KEY, 'x-rapidapi-host': 'v3.football.api-sports.io'}

# DATABASE DI FORMA REALE (Aggiornato sui dati che mi hai dato)
# att: capacità di creare occasioni | def: quanto concede all'avversario
TEAM_STATS = {
    "Cagliari": {"att": 0.40, "def": 1.15},   # Attacco sterile (4 gol in 15 gare)
    "Pisa": {"att": 0.90, "def": 0.85},
    "Barcelona": {"att": 2.30, "def": 0.75},
    "Real Madrid": {"att": 2.40, "def": 0.65},
    "Manchester City": {"att": 2.60, "def": 0.55},
    "BSC Young Boys": {"att": 2.10, "def": 0.90},
    "Sassuolo": {"att": 1.10, "def": 1.40},
    "Juventus": {"att": 1.20, "def": 0.60}
}

LEAGUES = {
    135: "Serie A", 136: "Serie B", 39: "Premier League", 
    78: "Bundesliga", 88: "Eredivisie", 140: "La Liga", 
    61: "Ligue 1", 207: "Super League (CH)", 208: "Challenge League"
}

st.set_page_config(page_title="REAL MATCH xG", layout="wide")

# --- LOGIN ---
if "auth" not in st.session_state:
    st.session_state["auth"] = False
if not st.session_state["auth"]:
    st.title("🔐 Accesso Analisi Professionale")
    pwd = st.text_input("Licenza", type="password")
    if st.button("SBLOCCA"):
        if pwd == "DAJE80":
            st.session_state["auth"] = True
            st.rerun()
    st.stop()

st.title("📊 Previsione xG Totale (Basata sulla Forma)")

if st.button("🚀 CALCOLA XG MATCH"):
    with st.spinner('Incrociando i dati di attacco e difesa...'):
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
                        
                        # Recupero dati forma (default 1.0 se non in DB)
                        h_stats = TEAM_STATS.get(h_name, {"att": 1.0, "def": 1.0})
                        a_stats = TEAM_STATS.get(a_name, {"att": 1.0, "def": 1.0})
                        
                        # LOGICA SCIENTIFICA:
                        # Potenziale Casa = (Attacco Casa * Difesa Ospite)
                        # Potenziale Ospite = (Attacco Ospite * Difesa Casa)
                        pot_h = 1.30 * h_stats["att"] * a_stats["def"]
                        pot_a = 1.10 * a_stats["att"] * h_stats["def"]
                        
                        total_match_xg = round(pot_h + pot_a, 2)
                        
                        # --- ANALISI ANDAMENTO ---
                        if total_match_xg < 2.05:
                            status = "🔴 MATCH CHIUSO (Under)"
                        elif total_match_xg > 3.10:
                            status = "🟢 MATCH APERTO (Over)"
                        else:
                            status = "🟡 EQUILIBRIO"

                        all_matches.append({
                            "Lega": LEAGUES[l_id],
                            "Partita": f"{h_name} vs {a_name}",
                            "xG TOTALE MATCH": total_match_xg,
                            "Analisi Tattica": status,
                            "Pronostico": "UNDER 2.5" if total_match_xg < 2.35 else "OVER 1.5"
                        })
            
            if all_matches:
                # Creazione Tabella e Ordinamento per xG (dal più basso al più alto)
                df = pd.DataFrame(all_matches).sort_values(by="xG TOTALE MATCH")
                st.table(df)
                st.info("Nota: Gli xG sono calcolati incrociando l'efficienza realizzativa delle due squadre.")
        except:
            st.error("Errore nel recupero dati API.")
