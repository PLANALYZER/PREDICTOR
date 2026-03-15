import streamlit as st
import requests
import pandas as pd

# CONFIGURAZIONE
API_KEY = "adf7b41bd4a85edbf0d28b46c647b3d7"
HEADERS = {'x-rapidapi-key': API_KEY, 'x-rapidapi-host': 'v3.football.api-sports.io'}
LEAGUES = [135, 136, 39, 40, 41, 42, 78, 140, 61, 207, 208, 218, 88, 89, 144]

st.set_page_config(page_title="PREDICTOR AI PRO", layout="wide")

# LOGIN PER VENDITA
if "auth" not in st.session_state:
    st.session_state["auth"] = False

if not st.session_state["auth"]:
    st.title("🔐 Accesso Licenza PRO")
    pwd = st.text_input("Inserisci Codice Licenza", type="password")
    if st.button("Attiva"):
        if pwd == "DAJE80":
            st.session_state["auth"] = True
            st.rerun()
        else:
            st.error("Codice errato")
    st.stop()

# INTERFACCIA APP
st.title("⚽ AI Predictor - Ennesima Potenza")
if st.button("LANCIA SCANSIONE MERCATI"):
    st.write("Analisi xG e Combo in corso...")
    # Qui il software farà le chiamate API reali
    st.success("Scansione completata!")
