import streamlit as st
import requests
import pandas as pd
from datetime import datetime

# --- CONFIGURAZIONE CORE ---
API_KEY = "adf7b41bd4a85edbf0d28b46c647b3d7"
HEADERS = {'x-rapidapi-key': API_KEY, 'x-rapidapi-host': 'v3.football.api-sports.io'}

# Leghe monitorate con medie gol reali per calibrare la formula
LEAGUES = {
    135: "Serie A", 136: "Serie B", 39: "Premier League", 
    78: "Bundesliga", 88: "Eredivisie", 140: "La Liga", 
    61: "Ligue 1", 207: "Super League (CH)", 208: "Challenge League"
}

st.set_page_config(page_title="AI XG PRECISION", layout="wide")

def get_team_stats(league_id, team_id):
    """Recupera le medie gol reali. Se mancano, usa un valore neutro sicuro."""
    url = f"https://v3.football.api-sports.io/teams/statistics?league={league_id}&season=2024&team={team_id}"
    try:
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
    st.title("🔐 Accesso Sistema")
    pwd = st.text_input("Inserisci Password", type="password")
    if st.button("SBLOCCA"):
        if pwd == "DAJE80":
            st.session_state["auth"] = True
            st.rerun()
    st.stop()

# --- INTERFACCIA ---
st.title("⚽ AI Real-Stats xG Predictor")
st.write("Analisi basata su medie gol reali e forza difensiva incrociata.")

if st.button("🚀 GENERA ANALISI SCIENTIFICA"):
    with st.spinner('Interrogazione database API...'):
        today = datetime.now().strftime('%Y-%m-%d')
        url = f"https://v3.football.api-sports.io/fixtures?date={today}"
        
        try:
            response = requests.get(url, headers=HEADERS, timeout=10).json()
            matches_data = []
            
            if 'response' in response and response['response']:
                # Filtriamo solo le partite delle tue leghe
                fixtures = [f for f in response['response'] if f['league']['id'] in LEAGUES]
                
                for f in fixtures[:20]: # Analisi dei primi 20 match per massima velocità
                    l_id = f['league']['id']
                    h_name, h_id = f['teams']['home']['name'], f['teams']['home']['id']
                    a_name, a_id = f['teams']['away']['name'], f['teams']['away']['id']
                    
                    # 1. Recupero medie reali
                    h_gf, h_gs = get_team_stats(l_id, h_id)
                    a_gf, a_gs = get_team_stats(l_id, a_id)
                    
                    # 2. Formula xG Professionale (Attacco Casa vs Difesa Ospite)
                    # Usiamo 1.25 come divisore per mantenere i valori nel range reale (1.0 - 3.0)
                    xg_h = (h_gf * a_gs) / 1.25
                    xg_a = (a_gf * h_gs) / 1.25
                    total_xg = round(xg_h + xg_a, 2)
                    
                    # 3. Correzione per squadre 'chiuse' (Cagliari, Pisa, etc.)
                    if any(x in [h_name, a_name] for x in ["Cagliari", "Pisa", "Sassuolo"]):
                        total_xg = round(total_xg * 0.85, 2)

                    matches_data.append({
                        "Lega": LEAGUES[l_id],
                        "Partita": f"{h_name} vs {a_name}",
                        "Forza Attacco Casa": round(h_gf, 2),
                        "Forza Attacco Ospite": round(a_gf, 2),
                        "xG TOTALE": total_xg,
                        "Consiglio": "UNDER 2.5" if total_xg < 2.25 else "OVER 1.5"
                    })
                
                if matches_data:
                    df = pd.DataFrame(matches_data).sort_values(by="xG TOTALE")
                    st.table(df)
                else:
                    st.info("Nessun match trovato per le leghe selezionate oggi.")
            else:
                st.error("Nessuna risposta dall'API delle partite.")
        except Exception as e:
            st.error(f"Errore tecnico durante il calcolo: {e}")
