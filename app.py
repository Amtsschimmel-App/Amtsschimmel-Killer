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
from openpyxl.utils import get_column_letter

# 1. KONFIGURATION
st.set_page_config(page_title="Amtsschimmel-Killer", page_icon="📄", layout="wide")
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
    .frist-box { background-color: #fef9c3; border-left: 5px solid #facc15; padding: 15px; border-radius: 8px; color: #854d0e; margin-bottom: 20px; font-weight: bold; }
    .brief-box { background-color: #f8fafc; border: 1px solid #e2e8f0; padding: 20px; border-radius: 8px; color: #1e293b; line-height: 1.6; white-space: pre-wrap; }
    [data-testid="stMetricValue"] { color: #1e3a8a; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# 3. API INITIALISIERUNG
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
stripe.api_key = st.secrets["STRIPE_API_KEY"]

if shutil.which("tesseract"):
    pytesseract.pytesseract.tesseract_cmd = shutil.which("tesseract")

# --- 4. SESSION STATE & ADMIN LOGIK ---
if "credits" not in st.session_state: st.session_state.credits = 0
if "processed_sessions" not in st.session_state: st.session_state.processed_sessions = []
if "last_fristen" not in st.session_state: st.session_state.last_fristen = ""
if "last_brief" not in st.session_state: st.session_state.last_brief = ""

params = st.query_params

# ADMIN-LOGIN ÜBER URL
ADMIN_PASSWORT = "GeheimAmt2024!" 
if params.get("admin") == ADMIN_PASSWORT:
    st.session_state.credits = 999
    st.toast("🔓 ADMIN-MODUS AKTIV", icon="🛠️")

# STRIPE RÜCKKEHR VERARBEITUNG
if "session_id" in params and params["session_id"] not in st.session_state.processed_sessions:
    try:
        session = stripe.checkout.Session.retrieve(params["session_id"])
        if session.payment_status in ["paid", "no_payment_required"]:
            pack = int(params.get("pack", 1))
            st.session_state.credits += pack
            st.session_state.processed_sessions.append(params["session_id"])
            st.balloons()
            st.query_params.clear()
    except: pass

# --- 5. HILFSFUNKTIONEN ---
def check_text_quality(text):
    text = text.strip()
    if not text or len(text) < 25: 
        return False, "Das Bild enthält zu wenig Text. Bitte heller und schärfer fotografieren."
    return True, ""

def get_text_hybrid(uploaded_file):
    text = ""
    file_bytes = uploaded_file.getvalue()
    if uploaded_file.type == "application/pdf":
        with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
            text = "\n".join([p.extract_text() for p in pdf.pages if p.extract_text()])
        if len(text.strip()) < 40:
            images = convert_from_bytes(file_bytes, dpi=200)
            text = "\n".join([pytesseract.image_to_string(img, lang='deu') for img in images])
    else:
        text = pytesseract.image_to_string(Image.open(uploaded_file), lang='deu')
    return text.strip()

class CustomPDF(FPDF):
    def header(self):
        if os.path.exists(LOGO_DATEI): self.image(LOGO_DATEI, 10, 8, 30)
        self.set_font('helvetica', 'B', 15); self.set_text_color(30, 58, 138)
        self.cell(0, 10, 'DEIN AMTSSCHIMMEL-KILLER', ln=True, align='R')
        self.line(10, 30, 200, 30); self.ln(15)

# --- 6. SIDEBAR ---
with st.sidebar:
    if os.path.exists(LOGO_DATEI): st.image(LOGO_DATEI, use_container_width=True)
    st.title("Dein Konto")
    st.metric("Guthaben", f"{st.session_state.credits} Scans")
    st.divider()
    st.subheader("💳 Guthaben laden")
    pkgs = [
        ("📄 Basis-Check", st.secrets["STRIPE_LINK_1"], "1 Scan", "3,99 €"),
        ("🚀 Spar-Paket", st.secrets["STRIPE_LINK_3"], "3 Scans", "9,99 €"),
        ("💎 Profi-Paket", st.secrets["STRIPE_LINK_10"], "10 Scans", "19,99 €")
    ]
    for t, l, c, p in pkgs:
        st.markdown(f'''<a href="{l}" target="_blank" class="buy-button"><b>{t}</b><br><small>{p} | {c}<br><b>KEIN ABO | Einmalzahlung</b></small></a>''', unsafe_allow_html=True)

# --- 7. HAUPTSEITE ---
c1, c2, c3 = st.columns([1,2,1])
with c2:
    if os.path.exists(LOGO_DATEI): st.image(LOGO_DATEI, width=300)

st.title("Amtsschimmel-Killer 📄🚀")
upload = st.file_uploader("Behördenbrief hochladen", type=['png', 'jpg', 'jpeg', 'pdf'])

if upload:
    col_v, col_a = st.columns([1, 1.2])
    with col_v:
        st.image(upload, use_container_width=True, caption="Deine Vorschau")

    with col_a:
        if not st.session_state.last_brief:
            if st.session_state.credits > 0:
                if st.button("🚀 Dokument jetzt analysieren"):
                    raw_text = get_text_hybrid(upload)
                    is_ok, err = check_text_quality(raw_text)
                    if not is_ok: st.error(err)
                    else:
                        with st.spinner("Amtsschimmel wird gezähmt..."):
                            st.session_state.credits -= 1
                            resp = client.chat.completions.create(
                                model="gpt-4o",
                                messages=[{"role": "system", "content": "Rechtsexperte. Trenne in ---FRISTEN--- und ---BRIEF---."},
                                          {"role": "user", "content": raw_text}]
                            )
                            txt = resp.choices.message.content
                            if "---BRIEF---" in txt:
                                parts = txt.split("---BRIEF---")
                                st.session_state.last_fristen = parts[0].replace("---FRISTEN---", "").strip()
                                st.session_state.last_brief = parts[1].strip()
                            else: st.session_state.last_brief = txt
                            st.rerun()
            else: st.warning("Guthaben leer. Bitte laden.")

        if st.session_state.last_brief:
            st.subheader("⚠️ Wichtige Fristen")
            st.markdown(f'<div class="frist-box">{st.session_state.last_fristen}</div>', unsafe_allow_html=True)
            st.subheader("📝 Musterschreiben")
            st.markdown(f'<div class="brief-box">{st.session_state.last_brief}</div>', unsafe_allow_html=True)
            
            st.divider()
            cp, cx, cr = st.columns(3)
            with cp:
                pdf = CustomPDF()
                pdf.add_page(); pdf.set_font("helvetica", 'B', 12); pdf.cell(0, 10, "Analyse:", ln=True)
                pdf.set_font("helvetica", size=10); pdf.multi_cell(0, 7, txt=st.session_state.last_brief.encode('latin-1','replace').decode('latin-1'))
                st.download_button("📩 PDF laden", bytes(pdf.output()), "Antwort.pdf")
            with cx:
                df = pd.DataFrame([{"Typ": "Fristen", "Inhalt": st.session_state.last_fristen}, {"Typ": "Brief", "Inhalt": st.session_state.last_brief}])
                out = io.BytesIO()
                with pd.ExcelWriter(out, engine='openpyxl') as wr:
                    df.to_excel(wr, index=False)
                    ws = wr.sheets['Sheet1']
                    ws.column_dimensions['B'].width = 80
                st.download_button("📊 Excel laden", out.getvalue(), "Analyse.xlsx")
            with cr:
                if st.button("🗑️ Neu"):
                    st.session_state.last_brief = ""; st.session_state.last_fristen = ""; st.rerun()
