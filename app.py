import streamlit as st
import requests
import pandas as pd

# --- CONFIGURAZIONE ---
API_KEY = "e8996ab4b899041a2107c622fbd3bb5c" 
HEADERS = {'x-rapidapi-key': API_KEY, 'x-rapidapi-host': 'v3.football.api-sports.io'}

# Configurazione Leghe (Aggiunta Eerste Divisie ID 72)
LEAGUE_DATA = {
    135: {"name": "Serie A", "avg": 1.22},
    136: {"name": "Serie B", "avg": 1.10},
    39: {"name": "Premier League", "avg": 1.45},
    78: {"name": "Bundesliga", "avg": 1.58},
    88: {"name": "Eredivisie", "avg": 1.65},      # Olanda 1
    72: {"name": "Eerste Divisie", "avg": 1.78},   # Olanda 2 (Serie B)
    140: {"name": "La Liga", "avg": 1.21}
}

st.set_page_config(page_title="REAL XG HOLLAND EDITION", layout="wide")

def get_stats_real(l_id, t_id):
    """Estrae gol medi reali. Se fallisce, usa la media alta olandese per evitare i 2.13 fissi."""
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
    pwd = st.text_input("Password Operativa", type="password")
    if st.button("SBLOCCA"):
        if pwd == "DAJE80": st.session_state["auth"] = True; st.rerun()
    st.stop()

# --- INTERFACCIA ---
st.title("⚽ AI Predictor: Focus Olanda & Top Europei")
st.write("Data: 16.03.2026 | Analisi basata su forza offensiva reale")

if st.button("🚀 GENERA ANALISI SCIENTIFICA"):
    with st.spinner('Calcolo xG reali in corso...'):
        url_fix = "https://v3.football.api-sports.io/fixtures?date=2026-03-16"
        
        try:
            res_fix = requests.get(url_fix, headers=HEADERS, timeout=10).json()
            results = []
            
            if 'response' in res_fix and res_fix['response']:
                fixtures = [m for m in res_fix['response'] if m['league']['id'] in LEAGUE_DATA]
                
                for m in fixtures:
                    l_id = m['league']['id']
                    h_n, h_id = m['teams']['home']['name'], m['teams']['home']['id']
                    a_n, a_id = m['teams']['away']['name'], m['teams']['away']['id']
                    
                    # Recupero dati reali (GF e GS)
                    h_f, h_s = get_stats_real(l_id, h_id)
                    a_f, a_s = get_stats_real(l_id, a_id)
                    
                    # Formula xG incrociata (Normalizzata su coefficiente 1.32)
                    total_xg = round(((h_f * a_s) + (a_f * h_s)) / 1.32, 2)
                    
                    # Flag Olanda per visibilità
                    flag = "🇳🇱 " if l_id in [72, 88] else ""

                    results.append({
                        "Lega": f"{flag}{LEAGUE_DATA[l_id]['name']}",
                        "Incontro": f"{h_n} vs {a_n}",
                        "xG Totale": total_xg,
                        "Pronostico": "OVER 1.5" if total_xg > 2.25 else "UNDER 2.5",
                        "Confidenza": f"{min(98, int((total_xg/3.8)*100))}%"
                    })
                
                if results:
                    df = pd.DataFrame(results).sort_values(by="xG Totale", ascending=False)
                    st.table(df)
                else:
                    st.info("Nessun match trovato per le leghe selezionate.")
            else:
                st.error("Errore API: Account sospeso o limite raggiunto.")
        except Exception as e:
            st.error(f"Errore tecnico: {e}")
