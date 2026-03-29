import streamlit as st
from openai import OpenAI
import pytesseract
from PIL import Image
import pdfplumber
from pdf2image import convert_from_bytes
import io
import os
import shutil
import stripe
from datetime import datetime
import gc 

# 1. KONFIGURATION
st.set_page_config(page_title="Amtsschimmel-Killer", page_icon="📄", layout="wide")
LOGO_DATEI = "icon_final_blau.png"

# 2. DESIGN & STYLING
st.markdown("""
    <style>
    .stButton>button { width: 100%; border-radius: 10px; height: 3.5em; background-color: #1e3a8a; color: white; font-weight: bold; border: none; }
    .stButton>button:hover { background-color: #2563eb; transform: translateY(-2px); }
    .buy-button { 
        text-decoration: none; display: block; padding: 12px; background: #ffffff; border: 1px solid #e2e8f0; 
        border-radius: 10px; margin-bottom: 10px; color: #1e3a8a !important; text-align: center; 
        box-shadow: 0 2px 4px rgba(0,0,0,0.05); transition: all 0.2s;
    }
    .buy-button:hover { border-color: #1e3a8a; background: #f8fafc; scale: 1.02; }
    .step-box { background: #eff6ff; padding: 15px; border-radius: 10px; border: 1px solid #bfdbfe; text-align: center; min-height: 100px; }
    .legal-box { font-size: 0.85em; color: #475569; line-height: 1.5; background: #f8fafc; padding: 15px; border-radius: 8px; }
    .faq-question { font-weight: bold; color: #1e3a8a; margin-top: 15px; font-size: 1.1em; }
    .faq-answer { margin-bottom: 15px; color: #334155; border-bottom: 1px solid #f1f5f9; padding-bottom: 10px; }
    </style>
    """, unsafe_allow_html=True)

# 3. API INITIALISIERUNG
if "OPENAI_API_KEY" in st.secrets:
    client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# --- 4. SESSION STATE & ADMIN LOGIK ---
if "credits" not in st.session_state: st.session_state.credits = 0
if "last_analysis" not in st.session_state: st.session_state.last_analysis = ""

# Admin-Check
if st.query_params.get("admin") == "GeheimAmt2024!":
    if st.session_state.credits < 100:
        st.session_state.credits = 999
        st.toast("🔓 ADMIN-MODUS AKTIV")

# --- 5. SIDEBAR ---
with st.sidebar:
    if os.path.exists(LOGO_DATEI): 
        st.image(LOGO_DATEI)
    st.metric("Dein Guthaben", f"{st.session_state.credits} Scans")
    st.divider()
    st.subheader("Guthaben aufladen")
    try:
        pkgs = [
            ("📄 Basis-Paket", st.secrets["STRIPE_LINK_1"], "1 Scan", "3,99 €"),
            ("🚀 Spar-Paket", st.secrets["STRIPE_LINK_3"], "3 Scans", "9,99 €"),
            ("💎 Profi-Paket", st.secrets["STRIPE_LINK_10"], "10 Scans", "19,99 €")
        ]
        for name, link, count, price in pkgs:
            st.markdown(f'<a href="{link}" target="_blank" class="buy-button"><b>{name}</b><br>{price} | {count}<br><small>✔ Einmalzahlung</small></a>', unsafe_allow_html=True)
    except: st.error("Stripe-Links fehlen in Secrets.")

# --- 6. HAUPTBEREICH ---
t1, t2, t3 = st.tabs(["🚀 Brief-Killer", "⚡ Sofort-Antworten", "❓ FAQ & Hilfe"])

with t1:
    st.title("Amtsschimmel-Killer 📄🚀")
    # Anleitung
    c1, c2, c3 = st.columns(3)
    with c1: st.markdown('<div class="step-box"><b>1. Guthaben wählen</b><br><small>Paket links buchen.</small></div>', unsafe_allow_html=True)
    with c2: st.markdown('<div class="step-box"><b>2. Brief hochladen</b><br><small>Foto oder PDF wählen.</small></div>', unsafe_allow_html=True)
    with c3: st.markdown('<div class="step-box"><b>3. Antwort nutzen</b><br><small>Kopieren & abschicken.</small></div>', unsafe_allow_html=True)
    
    st.divider()

    if st.session_state.last_analysis:
        if st.button("🔄 Nächsten Brief bearbeiten"):
            st.session_state.last_analysis = ""
            st.rerun()

    if not st.session_state.last_analysis:
        st.info("💡 **Sicherheitshinweis:** Du kannst sensible Daten vor dem Upload schwärzen.")
        upload = st.file_uploader("Datei wählen", type=['pdf', 'png', 'jpg', 'jpeg'])
        if upload and st.session_state.credits > 0:
            if st.button("🚀 Analyse starten"):
                with st.spinner("KI arbeitet..."):
                    st.session_state.last_analysis = "KI Antwortbrief..." 
                    st.session_state.credits -= 1
                    st.rerun()
        elif upload: st.error("Kein Guthaben.")

    if st.session_state.last_analysis:
        st.success("Ergebnis:")
        st.code(st.session_state.last_analysis, language="text")
        st.download_button("💾 Download", st.session_state.last_analysis, "antwort.txt")

with t2:
    st.subheader("⚡ Sofort-Antworten")
    with st.expander("⏳ Fristverlängerung"):
        st.code("Sehr geehrte Damen und Herren...", language="text")

with t3:
    st.subheader("❓ FAQ")
    faqs = [("Abo?", "Nein, Einmalzahlung."), ("Sicherheit?", "Verschlüsselt via SSL.")]
    for q, a in faqs:
        st.markdown(f"**{q}**\n\n{a}")

# --- 7. FOOTER ---
st.divider()
col1, col2 = st.columns(2)
with col1:
    with st.expander("🏢 Impressum"):
        st.markdown("Elisabeth Reinecke, Ringelsweide 9, 40223 Düsseldorf. amtsschimmel-killer@proton.me")
with col2:
    with st.expander("⚖️ Datenschutz"):
        st.markdown("Verantwortlich: Elisabeth Reinecke. Keine Speicherung von Scans.")
