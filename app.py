import streamlit as st
import requests
import pandas as pd
from datetime import datetime

# --- CONFIGURAZIONE CORE ---
API_KEY = "adf7b41bd4a85edbf0d28b46c647b3d7"
HEADERS = {'x-rapidapi-key': API_KEY, 'x-rapidapi-host': 'v3.football.api-sports.io'}

# Leghe monitorate (Aggiunta Eredivisie ID: 88)
LEAGUES = {
    135: "Serie A", 136: "Serie B", 39: "Premier League", 
    78: "Bundesliga", 88: "Eredivisie", 140: "La Liga", 
    61: "Ligue 1", 207: "Super League (CH)", 208: "Challenge League"
}

st.set_page_config(page_title="AI XG PRECISION 16.03", layout="wide")

def get_stats_safe(l_id, t_id):
    """Recupera medie gol reali. Se l'API fallisce, usa un valore neutro per non bloccare il tasto."""
    try:
        url = f"https://v3.football.api-sports.io/teams/statistics?league={l_id}&season=2025&team={t_id}"
        res = requests.get(url, headers=HEADERS, timeout=5).json()
        if 'response' in res and res['response']:
            stats = res['response']['goals']
            gf = float(stats['for']['average']['total']) if stats['for']['average']['total'] else 1.2
            gs = float(stats['against']['average']['total']) if stats['against']['against']['total'] else 1.2
            return gf, gs
    except:
        pass
    return 1.2, 1.2

# --- LOGIN ---
if "auth" not in st.session_state: st.session_state["auth"] = False
if not st.session_state["auth"]:
    pwd = st.text_input("Password", type="password")
    if st.button("SBLOCCA"):
        if pwd == "DAJE80":
            st.session_state["auth"] = True
            st.rerun()
    st.stop()

# --- INTERFACCIA ---
st.title("📊 AI Real-Stats xG Predictor - 16 Marzo 2026")

if st.button("🚀 GENERA ANALISI SCIENTIFICA"):
    with st.spinner('Scansione database leghe (inclusa Eredivisie)...'):
        # Data impostata correttamente per oggi
        today = "2026-03-16"
        url_fix = f"https://v3.football.api-sports.io/fixtures?date={today}"
        
        try:
            response = requests.get(url_fix, headers=HEADERS, timeout=10).json()
            all_matches = []
            
            if 'response' in response and response['response']:
                # Filtriamo solo i match delle leghe autorizzate
                fixtures = [f for f in response['response'] if f['league']['id'] in LEAGUES]
                
                for f in fixtures:
                    l_id = f['league']['id']
                    h_n, h_id = f['teams']['home']['name'], f['teams']['home']['id']
                    a_n, a_id = f['teams']['away']['name'], f['teams']['away']['id']
                    
                    # Recupero statistiche reali
                    h_gf, h_gs = get_stats_safe(l_id, h_id)
                    a_gf, a_gs = get_stats_safe(l_id, a_id)
                    
                    # Formula xG bilanciata su media 1.3
                    xg_h = (h_gf * a_gs) / 1.3
                    xg_a = (a_gf * h_gs) / 1.3
                    total_xg = round(xg_h + xg_a, 2)
                    
                    # Correzione automatica per squadre "stagnanti"
                    if any(x in [h_n, a_n] for x in ["Cagliari", "Pisa", "Sassuolo"]):
                        total_xg = round(total_xg * 0.85, 2)

                    all_matches.append({
                        "Lega": LEAGUES[l_id],
                        "Match": f"{h_n} vs {a_n}",
                        "xG Totale": total_xg,
                        "Pronostico": "UNDER 2.5" if total_xg < 2.25 else "OVER 1.5",
                        "Trend": "MOLTO CHIUSO" if total_xg < 1.80 else "APERTO" if total_xg > 2.70 else "EQUILIBRATO"
                    })
                
                if all_matches:
                    df = pd.DataFrame(all_matches).sort_values(by="xG Totale")
                    st.table(df)
                else:
                    st.info("Nessun match trovato per le leghe selezionate oggi.")
            else:
                st.error("L'API non ha restituito match. Verifica la tua connessione o riprova tra poco.")
        except Exception as e:
            st.error(f"Errore tecnico durante la generazione: {e}")
