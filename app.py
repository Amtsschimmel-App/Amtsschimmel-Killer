import streamlit as st
from openai import OpenAI
import pytesseract
from PIL import Image
import pdfplumber
from pdf2image import convert_from_bytes
from docx import Document
import io
import os
import pandas as pd
import re
from fpdf import FPDF 
from datetime import datetime

# ==========================================
# 1. KONFIGURATION & OPTIK
# ==========================================
st.set_page_config(page_title="Amtsschimmel-Killer", page_icon="📄", layout="wide")

st.markdown("""
    <style>
        .paket-box { border: 2px solid #0d47a1; padding: 15px; border-radius: 10px; background-color: #f0f7ff; margin-bottom: 10px; text-align: center; }
        .stDownloadButton button { width: 100% !important; background-color: #e1f5fe; border: 1px solid #01579b; }
        .stLinkButton a { width: 100% !important; background-color: #0d47a1 !important; color: white !important; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

LOGO_DATEI = "icon_final_blau.png"
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# ==========================================
# 2. RECHTSTEXTE (OBEN NEBENEINANDER)
# ==========================================
st.title("Amtsschimmel-Killer 🪓")

t1, t2, t3, t4 = st.columns(4)

with t1:
    with st.expander("⚖️ Impressum"):
        st.markdown("""**Amtsschimmel-Killer**  
Betreiberin: Elisabeth Reinecke  
Ringelsweide 9, 40223 Düsseldorf  
Telefon: +49 211 15821329  
amtsschimmel-killer@proton.me""")

with t2:
    with st.expander("🛡️ Datenschutz"):
        st.markdown("""1. Vertrauliche Behandlung (DSGVO).  
2. Hosting: Streamlit Cloud.  
3. Verarbeitung: TLS-verschlüsselt via OpenAI. Keine Speicherung.""")

with t3:
    with st.expander("❓ FAQ"):
        st.markdown("""**Abonnement?** Nein. Einmalzahlung.  
**Sicherheit?** Verschlüsselt & gelöscht.  
**Rechtsberatung?** Nein, Formulierungshilfe.""")

with t4:
    with st.expander("📝 Vorlagen"):
        st.markdown("""**Frist:** Bitte um Verlängerung bis [Datum].  
**Widerspruch:** Lege hiermit Widerspruch ein.""")

st.divider()

# ==========================================
# 3. HAUPTBEREICH (LINKS: PAKETE | RECHTS: APP)
# ==========================================
col_links, col_rechts = st.columns([1, 2.5])

with col_links:
    # Sprachen
    st.subheader("🌐 Sprachen")
    st.selectbox("Wähle deine Sprache", ["Deutsch", "English", "Türkçe", "Polski", "Русский", "العربية"])
    
    # Logo
    if os.path.exists(LOGO_DATEI):
        st.image(LOGO_DATEI, use_container_width=True)
    
    # Pakete als Boxen
    st.subheader("💰 Scans kaufen")
    
    st.markdown('<div class="paket-box"><b>📦 1. Paket</b><br>1 Scan für 3,99€<br><small>Einmalzahlung - Kein Abo</small></div>', unsafe_allow_html=True)
    st.link_button("Jetzt kaufen", "https://buy.stripe.com/eVqcN53Pd5YLgo8alq1gs02")
    
    st.markdown('<div class="paket-box"><b>📦 2. Paket</b><br>3 Scans für 9,99€<br><small>Einmalzahlung - Kein Abo</small></div>', unsafe_allow_html=True)
    st.link_button("Jetzt kaufen", "https://buy.stripe.com/8x228retRbj50paalq1gs03")
    
    st.markdown('<div class="paket-box"><b>📦 3. Paket</b><br>10 Scans für 19,99€<br><small>Einmalzahlung - Kein Abo</small></div>', unsafe_allow_html=True)
    st.link_button("Jetzt kaufen", "https://buy.stripe.com/28EcN50D1bj52xi8di1gs04")

with col_rechts:
    # Session State
    if "credits" not in st.session_state: st.session_state.credits = 0
    if "full_res" not in st.session_state: st.session_state.full_res = ""

    st.subheader("📄 Dokumenten-Analyse")
    st.info(f"Dein Guthaben: **{st.session_state.credits} Scans**")
    
    upped = st.file_uploader("Brief hochladen (PDF oder Foto)", type=["pdf", "jpg", "png", "jpeg"])
    
    if upped and st.session_state.credits > 0:
        if st.button("🚀 JETZT ANALYSIEREN"):
            with st.spinner("Amtsschimmel wird verjagt..."):
                # Simulierter OCR/KI Prozess
                st.session_state.full_res = "### 🚦 Wichtigkeit\nHoch\n\n### 📖 Zusammenfassung\nZusammenfassung des Briefes...\n\n### 📅 Fristen\n15.10.2024\n\n### ✍️ Antwort-Entwurf\nSehr geehrte Damen und Herren..."
                st.session_state.credits -= 1
                st.rerun()

    if st.session_state.full_res:
        res = st.session_state.full_res
        st.divider()
        # Analyse in Boxen
        c_ampel, c_sum = st.columns(2)
        with c_ampel: st.info(f"### 🚦 Wichtigkeit\n{re.search(r'🚦(.*?)(?=📖|$)', res, re.S).group(1) if '🚦' in res else 'Hoch'}")
        with c_sum: st.write(f"### 📖 Zusammenfassung\n{re.search(r'📖(.*?)(?=📅|$)', res, re.S).group(1) if '📖' in res else '...'}")
        
        c_date, c_draft = st.columns(2)
        with c_date: st.warning(f"### 📅 Fristen\n{re.search(r'📅(.*?)(?=✍️|$)', res, re.S).group(1) if '📅' in res else '...'}")
        with c_draft: st.success(f"### ✍️ Antwortschreiben\n{re.search(r'✍️(.*)', res, re.S).group(1) if '✍️' in res else '...'}")

        # Downloads ganz unten
        st.divider()
        st.subheader("📥 Downloads")
        d1, d2, d3, d4 = st.columns(4)
        with d1: st.download_button("📄 PDF", b"PDF_DATA", "Analyse.pdf")
        with d2: st.download_button("📝 Word", b"DOCX_DATA", "Analyse.docx")
        with d3: st.download_button("📊 Excel", b"XLS_DATA", "Fristen.xlsx")
        with d4: st.download_button("📅 Kalender", b"ICS_DATA", "Termin.ics")

