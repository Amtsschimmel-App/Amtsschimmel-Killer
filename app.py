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
from openpyxl.styles import Alignment
import streamlit.components.v1 as components
import gc 
import urllib.parse

# 1. KONFIGURATION
st.set_page_config(page_title="Amtsschimmel-Killer", page_icon="📄", layout="wide")
LOGO_DATEI = "icon_final_blau.png"

# 2. DESIGN (CSS)
st.markdown("""
    <style>
    .stButton>button { width: 100%; border-radius: 10px; height: 3.5em; background-color: #1e3a8a; color: white; font-weight: bold; border: none; }
    .stButton>button:hover { background-color: #2563eb; transform: translateY(-2px); }
    .stDownloadButton>button { width: 100%; border-radius: 10px; background-color: #10b981; color: white; font-weight: bold; border: none; }
    .buy-button { 
        text-decoration: none; display: block; padding: 15px; background: #ffffff; border: 1px solid #e2e8f0; 
        border-radius: 12px; margin-bottom: 12px; color: #1e3a8a !important; text-align: center; 
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1); transition: all 0.2s;
    }
    .buy-button:hover { transform: scale(1.02); border-color: #1e3a8a; }
    .frist-box { background-color: #fef9c3; border-left: 5px solid #facc15; padding: 15px; border-radius: 8px; color: #854d0e; margin-bottom: 20px; font-weight: bold; }
    .admin-stats { background-color: #ecfdf5; border: 1px solid #10b981; padding: 20px; border-radius: 10px; margin-bottom: 20px; color: #065f46; }
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
if "total_revenue" not in st.session_state: st.session_state.total_revenue = 0.0
if "last_files" not in st.session_state: st.session_state.last_files = []
if "last_fristen" not in st.session_state: st.session_state.last_fristen = ""
if "last_brief" not in st.session_state: st.session_state.last_brief = ""
if "last_amt" not in st.session_state: st.session_state.last_amt = ""

params = st.query_params
is_admin = params.get("admin") == "GeheimAmt2024!"
if is_admin and st.session_state.credits < 100:
    st.session_state.credits = 999
    st.toast("🔓 ADMIN-MODUS AKTIV")

if "session_id" in params and params["session_id"] not in st.session_state.processed_sessions:
    try:
        session = stripe.checkout.Session.retrieve(params["session_id"])
        if session.payment_status in ["paid", "no_payment_required"]:
            pack = int(params.get("pack", 1))
            st.session_state.credits += pack
            price_map = {1: 3.99, 3: 9.99, 10: 19.99}
            st.session_state.total_revenue += price_map.get(pack, 0.0)
            st.session_state.processed_sessions.append(params["session_id"])
            st.balloons()
            st.query_params.clear()
    except: pass

# --- 5. HILFSFUNKTIONEN ---
def get_text_hybrid(uploaded_file):
    text = ""
    file_bytes = uploaded_file.getvalue()
    if uploaded_file.type == "application/pdf":
        with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
            text = "\n".join([p.extract_text() for p in pdf.pages if p.extract_text()])
        if len(text.strip()) < 35:
            images = convert_from_bytes(file_bytes, dpi=250)
            text = "\n".join([pytesseract.image_to_string(img, lang='deu') for img in images])
    else:
        text = pytesseract.image_to_string(Image.open(uploaded_file), lang='deu')
    return text.strip()

def text_to_speech(text, voice_choice):
    """Erzeugt Sprachausgabe mit gewählter Stimme."""
    try:
        voice_map = {"Weiblich": "nova", "Männlich": "onyx"}
        response = client.audio.speech.create(
            model="tts-1",
            voice=voice_map.get(voice_choice, "nova"),
            input=text[:4000]
        )
        return response.content
    except:
        return None

class CustomPDF(FPDF):
    def header(self):
        if os.path.exists(LOGO_DATEI): self.image(LOGO_DATEI, 10, 8, 30)
        self.set_font('helvetica', 'B', 15); self.set_text_color(30, 58, 138)
        self.cell(0, 10, 'AMTSSCHIMMEL-KILLER', ln=True, align='R')
        self.line(10, 30, 200, 30); self.ln(15)

# --- 6. SIDEBAR ---
with st.sidebar:
    if os.path.exists(LOGO_DATEI): st.image(LOGO_DATEI, use_container_width=True)
    st.title("Konto")
    st.metric("Guthaben", f"{st.session_state.credits} Scans")
    
    st.divider()
    lang = st.radio("Sprache / Language", ["Deutsch", "English"], horizontal=True)
    voice = st.selectbox("Vorlese-Stimme", ["Weiblich", "Männlich"])
    
    st.divider()
    pkgs = [("📄 Basis", st.secrets["STRIPE_LINK_1"], "1 Scan", "3,99 €"),
            ("🚀 Spar", st.secrets["STRIPE_LINK_3"], "3 Scans", "9,99 €"),
            ("💎 Profi", st.secrets["STRIPE_LINK_10"], "10 Scans", "19,99 €")]
    for t, l, c, p in pkgs:
        st.markdown(f'<a href="{l}" target="_blank" class="buy-button"><b>{t}</b><br><small>{p} | {c}<br><b>KEIN ABO</b></small></a>', unsafe_allow_html=True)

# --- 7. HAUPTSEITE ---
if is_admin:
    st.markdown(f'<div class="admin-stats">📊 Admin: {st.session_state.total_revenue:.2f} € Umsatz | {len(st.session_state.last_files)} Scans</div>', unsafe_allow_html=True)

c1, c2, c3 = st.columns(3)
with c2:
    if os.path.exists(LOGO_DATEI): st.image(LOGO_DATEI, use_container_width=True)

st.title("Amtsschimmel-Killer 📄🚀")
upload = st.file_uploader("Brief hochladen", type=['png', 'jpg', 'jpeg', 'pdf'])

if upload:
    col_v, col_a = st.columns([1, 1.2])
    with col_v:
        if upload.type == "application/pdf":
            try:
                pdf_imgs = convert_from_bytes(upload.getvalue(), dpi=72, first_page=1, last_page=1)
                st.image(pdf_imgs, use_container_width=True)
            except: st.info("Preview lädt...")
        else: st.image(upload, use_container_width=True)

    with col_a:
        if not st.session_state.last_brief:
            if st.session_state.credits > 0:
                if st.button("🚀 Analyse starten"):
                    st.session_state.last_files.append(upload.name)
                    raw_text = get_text_hybrid(upload)
                    with st.spinner("KI arbeitet..."):
                        st.session_state.credits -= 1
                        sys_p = f"""Rechtsexperte. Sprache: {lang}. 
                        Format: 
                        ---AMT---
                        (Behörde)
                        ---FRISTEN---
                        (Termine)
                        ---BRIEF---
                        (Antwortbrief)"""
                        
                        resp = client.chat.completions.create(model="gpt-4o", messages=[{"role": "system", "content": sys_p}, {"role": "user", "content": raw_text}])
                        full_res = resp.choices[0].message.content
                        
                        # Sichereres Parsing
                        try:
                            st.session_state.last_amt = full_res.split("---AMT---")[1].split("---FRISTEN---")[0].strip()
                            st.session_state.last_fristen = full_res.split("---FRISTEN---")[1].split("---BRIEF---")[0].strip()
                            st.session_state.last_brief = full_res.split("---BRIEF---")[1].strip()
                        except:
                            st.session_state.last_brief = full_res
                        
                        del raw_text; gc.collect(); st.rerun()
            else: st.warning("Guthaben leer.")

        if st.session_state.last_brief:
            if st.session_state.last_amt:
                st.subheader("🏢 Behörde")
                st.info(st.session_state.last_amt)
            
            st.subheader("⚠️ Fristen")
            st.markdown(f'<div class="frist-box">{st.session_state.last_fristen}</div>', unsafe_allow_html=True)
            
            st.subheader("📝 Antwortentwurf")
            st.code(st.session_state.last_brief, language="text")
            
            # AUDIO VORLESEN
            st.divider()
            if st.button(f"🔊 Analyse & Brief vorlesen ({voice})"):
                with st.spinner("Sprache wird generiert..."):
                    audio_data = text_to_speech(f"Behörde: {st.session_state.last_amt}. Fristen: {st.session_state.last_fristen}. Brief: {st.session_state.last_brief}", voice)
                    if audio_data:
                        st.audio(audio_data, format="audio/mp3")
            
            st.divider()
            c_p, c_d, c_x, c_r = st.columns(4)
            with c_p:
                if st.button("🖨️ Drucken"):
                    components.html(f"<script>var win = window.open('', '', 'height=700,width=700'); win.document.write('<pre style=\"white-space: pre-wrap; font-family: Arial;\">' + `{st.session_state.last_brief}` + '</pre>'); win.document.close(); win.print();</script>", height=0)
            with c_d:
                pdf = CustomPDF()
                pdf.add_page(); pdf.set_font("helvetica", size=11); pdf.multi_cell(0, 7, txt=st.session_state.last_brief.encode('latin-1','replace').decode('latin-1'))
                st.download_button("📩 PDF", bytes(pdf.output()), "Antwort.pdf")
            with c_x:
                df = pd.DataFrame([{"Brief": st.session_state.last_brief}])
                out = io.BytesIO()
                with pd.ExcelWriter(out, engine='openpyxl') as wr:
                    df.to_excel(wr, index=False)
                st.download_button("📊 Excel", out.getvalue(), "Analyse.xlsx")
            with c_r:
                if st.button("🗑️ Neu"): st.session_state.last_brief = ""; st.rerun()

# --- 8. FOOTER ---
st.divider()
cols_f = st.columns(3)
with cols_f[0]:
    with st.expander("⚖️ Impressum"):
        st.write("Elisabeth Reinecke\nRingelsweide 9\n40223 Düsseldorf\nTel: +49 211 15821329")
with cols_f[1]:
    with st.expander("🛡️ Datenschutz"):
        st.write("Dokumente werden nach Analyse gelöscht.")
with cols_f[2]:
    with st.expander("💬 Feedback"):
        fb = st.text_area("Feedback...")
        if st.button("Senden"):
            st.markdown(f'<a href="mailto:amtsschimmel-killer@proton.me?body={urllib.parse.quote(fb)}">Mail senden</a>', unsafe_allow_html=True)
