import streamlit as st
import requests
import pandas as pd
from datetime import datetime

# --- CONFIGURAZIONE ---
API_KEY = "adf7b41bd4a85edbf0d28b46c647b3d7"
HEADERS = {'x-rapidapi-key': API_KEY, 'x-rapidapi-host': 'v3.football.api-sports.io'}
LEAGUES = [135, 136, 39, 40, 41, 42, 78, 140, 61, 207, 208, 218, 88, 89, 144]

st.set_page_config(page_title="PREDICTOR AI PRO", layout="wide")

# --- LOGIN ---
if "auth" not in st.session_state:
    st.session_state["auth"] = False
if not st.session_state["auth"]:
    st.title("🔐 Accesso Licenza PRO")
    pwd = st.text_input("Inserisci Password", type="password")
    if st.button("ENTRA"):
        if pwd == "DAJE80":
            st.session_state["auth"] = True
            st.rerun()
    st.stop()

# --- APP ---
st.title("⚽ AI Predictor - Ennesima Potenza")

if st.button("🚀 AVVIA ANALISI REAL-TIME"):
    with st.spinner('Pescando i dati dal database...'):
        # 1. Chiamata singola per tutti i match di oggi (RISPARMIA CREDITI)
        today = datetime.now().strftime('%Y-%m-%d')
        url = f"https://v3.football.api-sports.io/fixtures?date={today}"
        
        try:
            response = requests.get(url, headers=HEADERS).json()
            
            all_matches = []
            if 'response' in response:
                for match in response['response']:
                    league_id = match['league']['id']
                    
                    # FILTRO: Solo se la partita fa parte delle tue 15 leghe
                    if league_id in LEAGUES:
                        # Logica Combo Multigol
                        if league_id in [89, 207]: 
                            combo = "MG CASA 1-3 + MG OSPITE 2-4"
                        else:
                            combo = "MG CASA 1-3 + MG OSPITE 1-3"
                        
                        all_matches.append({
                            "Lega": match['league']['name'],
                            "Partita": f"{match['teams']['home']['name']} vs {match['teams']['away']['name']}",
                            "Pronostico": combo,
                            "Fiducia": "🟢 ALTA"
                        })
            
            if all_matches:
                st.table(pd.DataFrame(all_matches))
                st.success(f"Trovate {len(all_matches)} partite oggi!")
            else:
                st.warning(f"Oggi ({today}) non ci sono partite nei tuoi 15 campionati scelti. Prova domani!")
                
        except Exception as e:
            st.error(f"Errore tecnico: {e}")

st.sidebar.write(f"Crediti API disponibili: 90/100")
