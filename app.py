import streamlit as st
import requests
import pandas as pd

# --- CONFIGURAZIONE ---
API_KEY = "e8996ab4b899041a2107c622fbd3bb5c" 
HEADERS = {'x-apisports-key': API_KEY} # Usiamo l'header corretto come da tua documentazione

# Leghe monitorate (Olanda 1 & 2 incluse)
LEAGUES = {
    135: "Serie A", 136: "Serie B", 39: "Premier League", 
    78: "Bundesliga", 88: "Eredivisie", 72: "Eerste Divisie", 
    140: "La Liga", 61: "Ligue 1", 207: "Super League (CH)"
}

st.set_page_config(page_title="REAL STANDINGS XG", layout="wide")

def get_team_stats_from_standings(l_id):
    """Recupera i dati reali di attacco e difesa dalla classifica della lega"""
    url = f"https://v3.football.api-sports.io/standings?league={l_id}&season=2025"
    try:
        res = requests.get(url, headers=HEADERS, timeout=7).json()
        standings_data = {}
        if 'response' in res and res['response']:
            # Estraiamo la lista delle squadre dalla risposta
            league_info = res['response'][0]['league']['standings'][0]
            for team in league_info:
                t_id = team['team']['id']
                played = team['all']['played']
                if played > 0:
                    gf_avg = team['all']['goals']['for'] / played
                    gs_avg = team['all']['goals']['against'] / played
                else:
                    gf_avg, gs_avg = 1.2, 1.2
                standings_data[t_id] = {'gf': gf_avg, 'gs': gs_avg}
        return standings_data
    except:
        return {}

# --- LOGIN ---
if "auth" not in st.session_state: st.session_state["auth"] = False
if not st.session_state["auth"]:
    pwd = st.text_input("Password", type="password")
    if st.button("SBLOCCA"):
        if pwd == "DAJE80": st.session_state["auth"] = True; st.rerun()
    st.stop()

st.title("⚽ AI Predictor 16.03.2026 - Dati Standings")

if st.button("🚀 GENERA ANALISI DAI DATI REALI"):
    with st.spinner('Scansione classifiche e match...'):
        # Data odierna
        today = "2026-03-16"
        url_fix = f"https://v3.football.api-sports.io/fixtures?date={today}"
        
        try:
            res_fix = requests.get(url_fix, headers=HEADERS, timeout=10).json()
            results = []
            
            # Pre-carichiamo le statistiche per ogni lega per non rallentare il calcolo
            stats_cache = {}
            for l_id in LEAGUES.keys():
                stats_cache[l_id] = get_team_stats_from_standings(l_id)

            if 'response' in res_fix and res_fix['response']:
                fixtures = [m for m in res_fix['response'] if m['league']['id'] in LEAGUES]
                
                for m in fixtures:
                    l_id = m['league']['id']
                    h_n, h_id = m['teams']['home']['name'], m['teams']['home']['id']
                    a_n, a_id = m['teams']['away']['name'], m['teams']['away']['id']
                    
                    # Prendiamo i dati reali dalla nostra cache delle classifiche
                    h_stats = stats_cache[l_id].get(h_id, {'gf': 1.2, 'gs': 1.2})
                    a_stats = stats_cache[l_id].get(a_id, {'gf': 1.2, 'gs': 1.2})
                    
                    # Formula xG incrociata basata su medie reali
                    xg_h = h_stats['gf'] * a_stats['gs']
                    xg_a = a_stats['gf'] * h_stats['gs']
                    total_xg = round((xg_h + xg_a) / 1.3, 2)
                    
                    flag = "🇳🇱 " if l_id in [72, 88] else ""

                    results.append({
                        "Lega": f"{flag}{LEAGUES[l_id]}",
                        "Incontro": f"{h_n} vs {a_n}",
                        "xG Totale": total_xg,
                        "Pronostico": "OVER 1.5" if total_xg > 2.20 else "UNDER 2.5",
                        "Attacco Casa": round(h_stats['gf'], 2),
                        "Attacco Ospite": round(a_stats['gf'], 2)
                    })
                
                if results:
                    st.table(pd.DataFrame(results).sort_values(by="xG Totale", ascending=False))
                else:
                    st.info("Nessun match oggi per le leghe monitorate.")
            else:
                st.error("Errore API: Verifica la chiave o l'abbonamento.")
        except Exception as e:
            st.error(f"Errore: {e}")
