import streamlit as st
import requests
import pandas as pd

# --- CONFIGURAZIONE ---
API_KEY = "e8996ab4b899041a2107c622fbd3bb5c" 
HEADERS = {'x-rapidapi-key': API_KEY, 'x-rapidapi-host': 'v3.football.api-sports.io'}

# Leghe monitorate con medie gol specifiche (Eredivisie + Eerste Divisie)
LEAGUE_DATA = {
    135: {"name": "Serie A", "avg": 1.22},
    136: {"name": "Serie B", "avg": 1.10},
    39: {"name": "Premier League", "avg": 1.45},
    78: {"name": "Bundesliga", "avg": 1.58},
    140: {"name": "La Liga", "avg": 1.21},
    61: {"name": "Ligue 1", "avg": 1.26},
    207: {"name": "Super League (CH)", "avg": 1.40},
    88: {"name": "Eredivisie", "avg": 1.65},      # Olanda 1
    72: {"name": "Eerste Divisie", "avg": 1.75}   # Olanda 2 (ID Standard API-Football)
}

st.set_page_config(page_title="PROFESSIONAL xG ENGINE", layout="wide")

def fetch_real_stats(l_id, t_id):
    """Recupera statistiche reali. Evita il blocco 2.1300 usando dati lega se il team fallisce."""
    try:
        url = f"https://v3.football.api-sports.io/teams/statistics?league={l_id}&season=2025&team={t_id}"
        res = requests.get(url, headers=HEADERS, timeout=5).json()
        if 'response' in res and res['response']:
            g = res['response']['goals']
            f = float(g['for']['average']['total']) if g['for']['average']['total'] else LEAGUE_DATA[l_id]["avg"]
            s = float(g['against']['average']['total']) if g['against']['average']['total'] else LEAGUE_DATA[l_id]["avg"]
            return f, s
    except:
        pass
    return LEAGUE_DATA[l_id]["avg"], LEAGUE_DATA[l_id]["avg"]

# --- LOGIN ---
if "auth" not in st.session_state: st.session_state["auth"] = False
if not st.session_state["auth"]:
    pwd = st.text_input("Inserisci Password Operativa", type="password")
    if st.button("ACCEDI"):
        if pwd == "DAJE80": st.session_state["auth"] = True; st.rerun()
    st.stop()

st.title("📊 AI Professional xG Predictor - 16.03.2026")
st.subheader("Focus: Serie A, B, Olanda 1 & 2, Top Europei")

if st.button("🔍 GENERA ANALISI SCIENTIFICA"):
    with st.spinner('Analisi incrociata attacco/difesa in corso...'):
        # Data di oggi
        today = "2026-03-16"
        url_fix = f"https://v3.football.api-sports.io/fixtures?date={today}"
        
        try:
            res_fix = requests.get(url_fix, headers=HEADERS, timeout=10).json()
            results = []
            
            if 'response' in res_fix and res_fix['response']:
                # Filtro per le leghe configurate
                fixtures = [m for m in res_fix['response'] if m['league']['id'] in LEAGUE_DATA]
                
                for m in fixtures:
                    l_id = m['league']['id']
                    h_n, h_id = m['teams']['home']['name'], m['teams']['home']['id']
                    a_n, a_id = m['teams']['away']['name'], m['teams']['away']['id']
                    
                    # Calcolo dati reali dinamici
                    h_f, h_s = fetch_real_stats(l_id, h_id)
                    a_f, a_s = fetch_real_stats(l_id, a_id)
                    
                    # Formula xG bilanciata: (Attacco H * Difesa A) + (Attacco A * Difesa H)
                    total_xg = round(((h_f * a_s) + (a_f * h_s)) / 1.30, 2)
                    
                    # Flag per match olandesi (spesso Over)
                    is_dutch = "🇳🇱" if l_id in [88, 72] else ""

                    results.append({
                        "Lega": f"{is_dutch} {LEAGUE_DATA[l_id]['name']}",
                        "Match": f"{h_n} vs {a_n}",
                        "xG Totale": total_xg,
                        "Pronostico": "OVER 1.5" if total_xg > 2.25 else "UNDER 2.5",
                        "Confidenza": f"{int((total_xg/4)*100)}%" if total_xg < 3.5 else "95%"
                    })
                
                if results:
                    df = pd.DataFrame(results).sort_values(by="xG Totale", ascending=False)
                    st.table(df)
                else:
                    st.info("Nessun match trovato per le tue leghe oggi.")
            else:
                st.warning("Nessuna risposta dall'API. Controlla il piano o la chiave.")
        except Exception as e:
            st.error(f"Errore: {e}")
