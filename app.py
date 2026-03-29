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
import pandas as pd
from datetime import datetime
import gc 

# 1. KONFIGURATION
st.set_page_config(page_title="Amtsschimmel-Killer", page_icon="📄", layout="wide")
LOGO_DATEI = "icon_final_blau.png"

# 2. DESIGN
st.markdown("""
    <style>
    .stButton>button { width: 100%; border-radius: 10px; height: 3.5em; background-color: #1e3a8a; color: white; font-weight: bold; border: none; }
    .stButton>button:hover { background-color: #2563eb; transform: translateY(-2px); }
    .buy-button { text-decoration: none; display: block; padding: 12px; background: #ffffff; border: 1px solid #e2e8f0; border-radius: 10px; margin-bottom: 10px; color: #1e3a8a !important; text-align: center; box-shadow: 0 2px 4px rgba(0,0,0,0.05); transition: all 0.2s; }
    .buy-button:hover { border-color: #1e3a8a; background: #f8fafc; scale: 1.02; }
    .legal-box { font-size: 0.9em; color: #334155; line-height: 1.6; background: #f8fafc; padding: 25px; border-radius: 10px; border: 1px solid #e2e8f0; }
    .faq-q { font-weight: bold; color: #1e3a8a; margin-top: 15px; font-size: 1.1em; display: block; }
    .faq-a { margin-bottom: 15px; padding-left: 10px; border-left: 3px solid #cbd5e1; color: #475569; }
    </style>
    """, unsafe_allow_html=True)

# 3. SESSION STATE
if "credits" not in st.session_state: st.session_state.credits = 0
if "last_analysis" not in st.session_state: st.session_state.last_analysis = ""
if "processed_sessions" not in st.session_state: st.session_state.processed_sessions = []

# Admin & Stripe Logik
params = st.query_params
if params.get("admin") == "GeheimAmt2024!":
    st.session_state.credits = 999
if "session_id" in params and params["session_id"] not in st.session_state.processed_sessions:
    try:
        pack = int(params.get("pack", 0))
        st.session_state.credits += pack
        st.session_state.processed_sessions.append(params["session_id"])
    except: pass

# 4. FUNKTIONEN
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

def get_text_hybrid(uploaded_file):
    text = ""
    file_bytes = uploaded_file.getvalue()
    if uploaded_file.type == "application/pdf":
        with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
            text = "\n".join([p.extract_text() for p in pdf.pages if p.extract_text()])
        if len(text.strip()) < 50:
            images = convert_from_bytes(file_bytes, dpi=200)
            text = "\n".join([pytesseract.image_to_string(img, lang='deu') for img in images])
    else:
        text = pytesseract.image_to_string(Image.open(uploaded_file), lang='deu')
    return text.strip()

def analyze_letter(raw_text, language):
    sys_p = f"Rechtsexperte. Sprache: {language}. Analysiere den Brief, liste Fristen (Datum) auf und erstelle einen Antworttext mit Platzhaltern."
    resp = client.chat.completions.create(model="gpt-4o", messages=[{"role": "system", "content": sys_p}, {"role": "user", "content": raw_text}])
    return resp.choices[0].message.content # KORRIGIERTER ZUGRIFF

def create_excel_calendar(analysis_text):
    # Einfacher Extraktor für Datumsangaben im Text
    dates = re.findall(r'(\d{2}\.\d{2}\.\d{4})', analysis_text)
    df = pd.DataFrame({"Frist / Termin": dates, "Ereignis": ["Termin aus Brief" for _ in dates]})
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Fristen')
    return output.getvalue()

import re

# 5. SIDEBAR
with st.sidebar:
    if os.path.exists(LOGO_DATEI): st.image(LOGO_DATEI)
    st.metric("Dein Guthaben", f"{st.session_state.credits} Scans")
    lang_choice = st.radio("Sprache", ["Deutsch", "English"], horizontal=True)
    voice_choice = st.selectbox("Vorlese-Stimme", ["Weiblich", "Männlich"])
    st.divider()
    pkgs = [("📄 Basis", st.secrets["STRIPE_LINK_1"], "1 Scan", "3,99 €"), ("🚀 Spar", st.secrets["STRIPE_LINK_3"], "3 Scans", "9,99 €"), ("💎 Profi", st.secrets["STRIPE_LINK_10"], "10 Scans", "19,99 €")]
    for n, l, c, p in pkgs:
        st.markdown(f'<a href="{l}" target="_blank" class="buy-button"><b>{n}</b><br>{p} | {c}<br><small>✔ Einmalzahlung | <b>KEIN ABO</b></small></a>', unsafe_allow_html=True)

# 6. HAUPTBEREICH
t1, t2, t3 = st.tabs(["🚀 Brief-Killer", "⚡ Vorlagen", "❓ FAQ & Hilfe"])

with t1:
    st.title("Amtsschimmel-Killer 📄🚀")
    if st.session_state.last_analysis:
        if st.button("🔄 Nächsten Brief bearbeiten"):
            st.session_state.last_analysis = ""; st.rerun()

    if not st.session_state.last_analysis:
        upload = st.file_uploader("Brief hochladen", type=['pdf', 'png', 'jpg', 'jpeg'])
        if upload:
            if upload.type != "application/pdf": st.image(upload, width=300, caption="Vorschau")
            if st.session_state.credits > 0:
                if st.button("🚀 Analyse starten"):
                    with st.spinner("Amtsschimmel wird vertrieben..."):
                        raw = get_text_hybrid(upload)
                        st.session_state.last_analysis = analyze_letter(raw, lang_choice)
                        st.session_state.credits -= 1; st.rerun()
            else: st.error("Guthaben leer.")

    if st.session_state.last_analysis:
        st.success("Ergebnis:")
        st.markdown(f'<div style="white-space: pre-wrap; background: white; padding: 20px; border-radius: 10px; border: 1px solid #e2e8f0;">{st.session_state.last_analysis}</div>', unsafe_allow_html=True)
        
        col_a, col_b = st.columns(2)
        with col_a:
            st.download_button("💾 Text download", st.session_state.last_analysis, "antwort.txt")
        with col_b:
            excel_data = create_excel_calendar(st.session_state.last_analysis)
            st.download_button("📅 Fristen-Excel (Kalender)", excel_data, "fristen.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

with t2:
    st.subheader("⚡ Vorlagen")
    with st.expander("⏳ Fristverlängerung"):
        st.code("Sehr geehrte Damen und Herren, in der Angelegenheit [Aktenzeichen] bitte ich um Verlängerung der Frist...", language="text")
    with st.expander("🛑 Widerspruch"):
        st.code("Sehr geehrte Damen und Herren, gegen Ihren Bescheid vom [Datum] lege ich Widerspruch ein...", language="text")
    with st.expander("📂 Akteneinsicht"):
        st.code("Sehr geehrte Damen und Herren, hiermit beantrage ich Akteneinsicht gemäß § 25 SGB X...", language="text")

with t3:
    st.subheader("❓ FAQ")
    faq_data = [("Ist das ein Abonnement?", "Nein. Wir hassen Abos... Jede Zahlung ist eine Einmalzahlung."), 
                ("Sicherheit?", "Verschlüsselt via SSL. Keine dauerhafte Speicherung."),
                ("Rechtsberatung?", "Nein. Wir bieten Formulierungshilfe.")]
    for q, a in faq_data:
        st.markdown(f"**{q}**\n\n{a}")

# 7. FOOTER
st.divider()
c1, c2 = st.columns(2)
with c1:
    with st.expander("🏢 Impressum"):
        st.markdown("""**Amtsschimmel-Killer**<br>Elisabeth Reinecke<br>Ringelsweide 9, 40223 Düsseldorf<br>+49 211 15821329<br>amtsschimmel-killer@proton.me""", unsafe_allow_html=True)
with c2:
    with st.expander("⚖️ Datenschutz"):
        st.markdown("""1. Datenschutz vertraulich (DSGVO). 2. Hosting auf Streamlit. 3. Dokumente an OpenAI (TLS). 4. Stripe Zahlungen (Einmal). 5. Recht auf Löschung.""", unsafe_allow_html=True)
