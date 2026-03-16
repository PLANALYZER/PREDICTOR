import streamlit as st
import requests
import pandas as pd
from datetime import datetime

# --- CONFIGURAZIONE ---
API_KEY = "e8996ab4b899041a2107c622fbd3bb5c" 
HEADERS = {'x-rapidapi-key': API_KEY, 'x-rapidapi-host': 'v3.football.api-sports.io'}

# Leghe monitorate (Eredivisie inclusa)
LEAGUES = {
    135: "Serie A", 136: "Serie B", 39: "Premier League", 
    78: "Bundesliga", 88: "Eredivisie", 140: "La Liga", 
    61: "Ligue 1", 207: "Super League (CH)", 208: "Challenge League"
}

st.set_page_config(page_title="REAL XG PREDICTOR V6", layout="wide")

def get_stats_real(l_id, t_id):
    """Recupera le medie gol reali per la stagione corrente"""
    try:
        url = f"https://v3.football.api-sports.io/teams/statistics?league={l_id}&season=2025&team={t_id}"
        res = requests.get(url, headers=HEADERS, timeout=5).json()
        if 'response' in res and res['response']:
            g = res['response']['goals']
            # Media gol fatti e subiti
            f = float(g['for']['average']['total']) if g['for']['average']['total'] else 1.2
            s = float(g['against']['average']['total']) if g['against']['average']['total'] else 1.2
            return f, s
    except:
        pass
    return 1.2, 1.2

# --- LOGIN ---
if "auth" not in st.session_state: st.session_state["auth"] = False
if not st.session_state["auth"]:
    st.title("🔐 Accesso Sistema xG")
    pwd = st.text_input("Password", type="password")
    if st.button("SBLOCCA"):
        if pwd == "DAJE80": st.session_state["auth"] = True; st.rerun()
    st.stop()

# --- INTERFACCIA ---
st.title("📊 AI Predictor - Analisi Reale del 16.03.2026")

if st.button("🚀 GENERA PRONOSTICI REAL-TIME"):
    with st.spinner('Interrogazione database API in corso...'):
        # Data odierna
        today = "2026-03-16"
        url_fix = f"https://v3.football.api-sports.io/fixtures?date={today}"
        
        try:
            res_fix = requests.get(url_fix, headers=HEADERS, timeout=10).json()
            
            # Controllo errori account/chiave
            if 'errors' in res_fix and res_fix['errors']:
                st.error(f"Problema con la chiave API: {res_fix['errors']}")
                st.stop()
            
            results = []
            if 'response' in res_fix and res_fix['response']:
                # Filtro leghe autorizzate
                matches = [m for m in res_fix['response'] if m['league']['id'] in LEAGUES]
                
                for m in matches:
                    l_id = m['league']['id']
                    h_n, h_id = m['teams']['home']['name'], m['teams']['home']['id']
                    a_n, a_id = m['teams']['away']['name'], m['teams']['away']['id']
                    
                    # Recupero statistiche reali
                    h_f, h_s = get_stats_real(l_id, h_id)
                    a_f, a_s = get_stats_real(l_id, a_id)
                    
                    # Formula xG incrociata normalizzata
                    total_xg = round(((h_f * a_s) + (a_f * h_s)) / 1.35, 2)
                    
                    # Correzione specifica per squadre Under
                    if any(x in [h_n, a_n] for x in ["Cagliari", "Pisa", "Empoli", "Sassuolo"]):
                        total_xg = round(total_xg * 0.82, 2)

                    results.append({
                        "Lega": LEAGUES[l_id],
                        "Incontro": f"{h_n} vs {a_n}",
                        "xG Totale": total_xg,
                        "Consiglio": "UNDER 2.5" if total_xg < 2.20 else "OVER 1.5",
                        "Stato": "CHIUSO" if total_xg < 1.90 else "BILANCIATO" if total_xg < 2.60 else "OFFENSIVO"
                    })
                
                if results:
                    df = pd.DataFrame(results).sort_values(by="xG Totale")
                    st.table(df)
                else:
                    st.info("Nessuna partita trovata per le leghe selezionate oggi.")
            else:
                st.warning("Nessuna risposta dall'API. Verifica se l'abbonamento è attivo.")
        except Exception as e:
            st.error(f"Errore tecnico: {e}")
