import streamlit as st
import pandas as pd
from io import BytesIO
from fpdf import FPDF
from docx import Document

# --- 1. SETUP & DESIGN ---
st.set_page_config(page_title="Amtsschimmel-Killer", layout="wide", page_icon="🏛️")

st.markdown("""
<style>
    .paket-box { border-radius: 10px; padding: 15px; margin-bottom: 15px; border: 2px solid; background: #fff; text-align: center; }
    .blue { border-color: #007bff; background-color: #f0f7ff; }
    .green { border-color: #28a745; background-color: #f1f9f1; }
    .gold { border-color: #fcc419; background-color: #fffdf5; }
    .price { font-size: 22px; font-weight: bold; color: #1E3A8A; }
    .no-abo { font-size: 12px; color: #d32f2f; font-weight: bold; }
    .buy-btn {
        display: inline-block; padding: 10px; background-color: #1E3A8A; color: white !important;
        text-decoration: none; border-radius: 5px; font-weight: bold; width: 100%; margin-top: 10px;
    }
</style>
""", unsafe_allow_html=True)

# --- 2. LOGIK FÜR CREDITS ---
if 'credits' not in st.session_state:
    st.session_state.credits = 0

params = st.query_params
if "pack" in params:
    if params["pack"] == "1": st.session_state.credits += 1
    elif params["pack"] == "3": st.session_state.credits += 3
    elif params["pack"] == "10": st.session_state.credits += 10
    st.query_params.clear()

# --- 3. SEITENSTRUKTUR ---
col_sidebar, col_content = st.columns([1, 3])

with col_sidebar:
    st.image("https://placeholder.com", width=150) # Dein Logo hier
    st.selectbox("Sprache / Language", ["Deutsch", "English", "Türkçe", "Polski", "عربي", "Español", "Français", "Italiano"], key="lang")
    
    st.write(f"**Guthaben: {st.session_state.credits} Scans**")
    st.write("---")
    
    # Pakete in Boxen
    st.markdown("""
    <div class="paket-box blue">
        <strong>🛡️ Amtsschimmel-Killer Analyse</strong><br>(1 Dokument)
        <div class="price">3,99 €</div><div class="no-abo">Einmalzahlung kein Abo</div>
        <a href="https://buy.stripe.com/eVqcN53Pd5YLgo8alq1gs02" class="buy-btn">Jetzt kaufen</a>
    </div>
    <div class="paket-box green">
        <strong>⚔️ Amtsschimmel-Killer Spar-Paket</strong><br>(3 Dokumente)
        <div class="price">9,99 €</div><div class="no-abo">Einmalzahlung kein Abo</div>
        <a href="https://buy.stripe.com/8x228retRbj50paalq1gs03" class="buy-btn">Jetzt kaufen</a>
    </div>
    <div class="paket-box gold">
        <strong>🚀 Amtsschimmel-Killer Sorglos-Paket</strong><br>(10 Dokumente)
        <div class="price">19,99 €</div><div class="no-abo">Einmalzahlung kein Abo</div>
        <a href="https://stripe.com" class="buy-btn">Jetzt kaufen</a>
    </div>
    """, unsafe_allow_html=True)

with col_content:
    st.title("Amtsschimmel-Killer ⚖️")
    
    if st.session_state.credits > 0:
        u_file = st.file_uploader("Dokument hochladen (PDF, JPG, PNG)", type=["pdf", "jpg", "png"])
        if u_file:
            st.success("Dokument bereit zur Analyse.")
            if st.button("Analyse starten"):
                st.info("KI wertet aus...")
    else:
        st.warning("Bitte wähle links ein Paket aus, um Scans freizuschalten.")

    st.write("---")
    # Rechtstexte & Vorlagen
    tabs = st.tabs(["📋 Vorlagen", "❓ FAQ", "⚖️ Impressum", "🛡️ Datenschutz"])
    
    with tabs[0]:
        st.markdown("**Fristverlängerung:**\n`Sehr geehrte Damen und Herren, in der Angelegenheit [Aktenzeichen] bitte ich um Verlängerung der gesetzten Frist bis zum [Datum], da mir noch notwendige Unterlagen fehlen. Mit freundlichen Grüßen, [Name]`")
        st.markdown("**Widerspruch:**\n`Sehr geehrte Damen und Herren, gegen Ihren Bescheid vom [Datum], erhalten am [Datum], lege ich hiermit Widerspruch ein. Eine detaillierte Begründung folgt in einem separaten Schreiben. Mit freundlichen Grüßen, [Name]`")

    with tabs[1]:
        st.write("**Ist das ein Abo?** Nein. Einmalzahlung. **Sicherheit?** Verschlüsselt & keine Speicherung. **Rechtsberatung?** Nein, nur Hilfe.")

    with tabs[2]:
        st.text("Amtsschimmel-Killer\nBetreiberin: Elisabeth Reinecke\nRingelsweide 9, 40223 Düsseldorf\nE-Mail: amtsschimmel-killer@proton.me")

    with tabs[3]:
        st.write("Wir behandeln Ihre Daten vertraulich (DSGVO). Verarbeitung via OpenAI (USA). Keine dauerhafte Speicherung.")
