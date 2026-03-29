import streamlit as st
from openai import OpenAI
import pytesseract
from PIL import Image
from fpdf import FPDF 
import pdfplumber
from pdf2image import convert_from_bytes
import pandas as pd
import io
import os
import shutil
import stripe
from datetime import datetime, timedelta
import re

# 1. KONFIGURATION
st.set_page_config(page_title="Amtsschimmel-Killer", page_icon="📄", layout="wide")

# PFAD ZU DEINEM LOGO
LOGO_DATEI = "icon_final_blau.png"

# 2. DESIGN (CSS)
st.markdown("""
    <style>
    .stButton>button { width: 100%; border-radius: 10px; height: 3.5em; background-color: #1e3a8a; color: white; font-weight: bold; border: none; transition: 0.3s; }
    .stButton>button:hover { background-color: #2563eb; transform: translateY(-2px); }
    .stDownloadButton>button { width: 100%; border-radius: 10px; background-color: #10b981; color: white; font-weight: bold; border: none; }
    .buy-button { 
        text-decoration: none; display: block; padding: 15px; background: #ffffff; border: 1px solid #e2e8f0; 
        border-radius: 12px; margin-bottom: 12px; color: #1e3a8a !important; text-align: center; 
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1); transition: all 0.2s;
    }
    .buy-button:hover { transform: scale(1.02); box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1); border-color: #1e3a8a; }
    .frist-box { background-color: #fef9c3; border-left: 5px solid #facc15; padding: 15px; border-radius: 5px; color: #854d0e; margin-bottom: 20px; font-weight: bold; font-size: 1.1em; }
    .error-msg { background-color: #fee2e2; border: 1px solid #ef4444; color: #b91c1c; padding: 15px; border-radius: 8px; margin-bottom: 20px; font-weight: bold; }
    [data-testid="stMetricValue"] { color: #1e3a8a; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# 3. API INITIALISIERUNG
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
stripe.api_key = st.secrets["STRIPE_API_KEY"]

if shutil.which("tesseract"):
    pytesseract.pytesseract.tesseract_cmd = shutil.which("tesseract")

# --- 4. SESSION STATE & ZAHLUNGSLOGIK ---
if "credits" not in st.session_state: st.session_state.credits = 0
if "processed_sessions" not in st.session_state: st.session_state.processed_sessions = []
if "last_fristen" not in st.session_state: st.session_state.last_fristen = ""
if "last_brief" not in st.session_state: st.session_state.last_brief = ""

params = st.query_params

# ADMIN LOGIK
ADMIN_PASSWORT = "GeheimAmt2024!" 
is_admin = params.get("admin") == ADMIN_PASSWORT
if is_admin and st.session_state.credits < 100:
    st.session_state.credits = 999
    st.toast("🔓 ADMIN-MODUS AKTIV", icon="🛠️")

# STRIPE RÜCKKEHR VERARBEITUNG
if "session_id" in params and params["session_id"] not in st.session_state.processed_sessions:
    try:
        session = stripe.checkout.Session.retrieve(params["session_id"])
        if session.payment_status in ["paid", "no_payment_required"]:
            pack_size = int(params.get("pack", 1))
            st.session_state.credits += pack_size
            st.session_state.processed_sessions.append(params["session_id"])
            st.balloons()
            st.success(f"✨ Zahlung erfolgreich! {pack_size} Scan(s) freigeschaltet.")
            st.query_params.clear()
    except: pass

# --- 5. HILFSFUNKTIONEN ---
def check_text_quality(text):
    text = text.strip()
    if not text or len(text) < 50:
        return False, "Das Dokument scheint leer zu sein oder der Text konnte nicht erkannt werden."
    special_chars = len(re.findall(r'[^a-zA-Z0-9\säöüÄÖÜß.,!?\-]', text))
    if len(text) > 0 and (special_chars / len(text)) > 0.3:
        return False, "Der Text ist zu unscharf oder verwackelt. Bitte nochmal mit mehr Licht fotografieren."
    return True, ""

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

def create_ics(fristen_text):
    now = datetime.now().strftime("%Y%m%dT%H%M%SZ")
    dates = re.findall(r'\d{2}\.\d{2}\.\d{4}', fristen_text)
    start_date = dates[0].replace(".", "") if dates else (datetime.now() + timedelta(days=14)).strftime("%Y%m%d")
    ics_content = f"BEGIN:VCALENDAR\nVERSION:2.0\nBEGIN:VEVENT\nDTSTAMP:{now}\nDTSTART;VALUE=DATE:{start_date}\nSUMMARY:Frist Amtsschimmel-Killer\nDESCRIPTION:{fristen_text.replace('\\n', ' ')}\nEND:VEVENT\nEND:VCALENDAR"
    return ics_content

class CustomPDF(FPDF):
    def header(self):
        if os.path.exists(LOGO_DATEI):
            self.image(LOGO_DATEI, 10, 8, 33)
            self.ln(20)
        self.set_font('helvetica', 'B', 16)
        self.set_text_color(30, 58, 138)
        self.cell(0, 10, 'DEIN AMTSSCHIMMEL-KILLER', ln=True, align='R')
        self.line(10, self.get_y()+2, 200, self.get_y()+2)
        self.ln(10)

# --- 6. SIDEBAR ---
with st.sidebar:
    if os.path.exists(LOGO_DATEI):
        st.image(LOGO_DATEI, use_container_width=True)
    
    st.title("Dein Konto")
    st.metric("Guthaben", f"{st.session_state.credits} Scans")
    st.divider()
    st.subheader("💳 Guthaben laden")
    packages = [
        ("📄 Basis-Check", st.secrets.get("STRIPE_LINK_1", "#"), "1 Scan", "3,99 €"),
        ("🚀 Spar-Paket", st.secrets.get("STRIPE_LINK_3", "#"), "3 Scans", "9,99 €"),
        ("💎 Profi-Paket", st.secrets.get("STRIPE_LINK_10", "#"), "10 Scans", "19,99 €")
    ]
    for title, link, count, price in packages:
        st.markdown(f'''
            <a href="{link}" target="_blank" class="buy-button">
                <b>{title}</b><br>
                <small>{price} | {count}<br><b>KEIN ABO | Einmalzahlung</b></small>
            </a>
        ''', unsafe_allow_html=True)

# --- 7. HAUPTSEITE ---
c1, c2, c3 = st.columns([1, 2, 1])
with c2:
    if os.path.exists(LOGO_DATEI):
        st.image(LOGO_DATEI, width=350)

st.title("Amtsschimmel-Killer 📄🚀")
upload = st.file_uploader("Behörden-Dokument hochladen (PDF oder Foto)", type=['png', 'jpg', 'jpeg', 'pdf'])

if upload:
    col_v, col_a = st.columns([1, 1.5])
    with col_v:
        if upload.type == "application/pdf":
            try:
                imgs = convert_from_bytes(upload.getvalue(), dpi=72, first_page=1, last_page=1)
                st.image(imgs, use_container_width=True)
            except: st.info("Vorschau lädt...")
        else:
            st.image(upload, use_container_width=True)

    with col_a:
        raw_text = get_text_hybrid(upload)
        is_valid, error_msg = check_text_quality(raw_text)

        if not is_valid:
            st.markdown(f'<div class="error-msg">⚠️ {error_msg}</div>', unsafe_allow_html=True)
            if st.button("🔄 Nochmal versuchen"): st.rerun()
        
        elif st.session_state.credits <= 0:
            st.warning("Dein Guthaben ist leer. Bitte lade Scans in der Seitenleiste auf.")
        
        else:
            if st.button("🚀 Analyse starten (1 Credit)"):
                with st.spinner("Amtsschimmel wird gezähmt..."):
                    st.session_state.credits -= 1
                    prompt = f"Analysiere:\n{raw_text}\n\nFormat:\n---FRISTEN---\n(Termine)\n---BRIEF---\n(Antwortschreiben)"
                    response = client.chat.completions.create(
                        model="gpt-4o",
                        messages=[{"role": "system", "content": "Du bist Rechtsexperte."}, {"role": "user", "content": prompt}]
                    )
                    res = response.choices.message.content
                    if "---BRIEF---" in res:
                        parts = res.split("---BRIEF---")
                        st.session_state.last_fristen = parts[0].replace("---FRISTEN---", "").strip()
                        st.session_state.last_brief = parts[1].strip()
                    else:
                        st.session_state.last_brief = res
                    st.rerun()

        if st.session_state.last_brief:
            st.subheader("⚠️ Wichtige Fristen")
            st.markdown(f'<div class="frist-box">{st.session_state.last_fristen}</div>', unsafe_allow_html=True)
            st.download_button("📅 Termin speichern", create_ics(st.session_state.last_fristen), "Frist.ics", "text/calendar")
            
            st.subheader("📝 Antwortschreiben")
            st.markdown(st.session_state.last_brief)
            
            st.divider()
            c1, c2 = st.columns(2)
            with c1:
                pdf = CustomPDF()
                pdf.add_page()
                pdf.set_font("helvetica", 'B', 12)
                pdf.cell(0, 10, "Fristen & Termine:", ln=True)
                pdf.set_font("helvetica", size=11)
                pdf.multi_cell(0, 8, txt=st.session_state.last_fristen.encode('latin-1', 'replace').decode('latin-1'))
                pdf.ln(10)
                pdf.set_font("helvetica", 'B', 12)
                pdf.cell(0, 10, "Vorschlag Antwortbrief:", ln=True)
                pdf.set_font("helvetica", size=11)
                pdf.multi_cell(0, 8, txt=st.session_state.last_brief.encode('latin-1', 'replace').decode('latin-1'))
                st.download_button("📩 Brief als PDF laden", bytes(pdf.output()), "Antwort.pdf", "application/pdf")
            with c2:
                if st.button("🗑️ Zurücksetzen"):
                    st.session_state.last_brief = ""
                    st.session_state.last_fristen = ""
                    st.rerun()
