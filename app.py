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
    @media (max-width: 640px) {
        [data-testid="stHorizontalBlock"] { flex-direction: column !important; }
        .stButton>button, .stDownloadButton>button { margin-bottom: 10px; }
    }
    </style>
    """, unsafe_allow_html=True)

# 3. API INITIALISIERUNG
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
stripe.api_key = st.secrets["STRIPE_API_KEY"]

if shutil.which("tesseract"):
    pytesseract.pytesseract.tesseract_cmd = shutil.which("tesseract")

# --- 4. SESSION STATE ---
if "credits" not in st.session_state: st.session_state.credits = 0
if "processed_sessions" not in st.session_state: st.session_state.processed_sessions = []
if "last_fristen" not in st.session_state: st.session_state.last_fristen = ""
if "last_brief" not in st.session_state: st.session_state.last_brief = ""

params = st.query_params

# ADMIN-LOGIN
if params.get("admin") == "GeheimAmt2024!":
    st.session_state.credits = 999
    st.toast("🔓 ADMIN-MODUS AKTIV")

# STRIPE RÜCKKEHR
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
def get_text_hybrid(uploaded_file):
    text = ""
    file_bytes = uploaded_file.getvalue()
    if uploaded_file.type == "application/pdf":
        with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
            text = "\n".join([p.extract_text() for p in pdf.pages if p.extract_text()])
        if len(text.strip()) < 35:
            images = convert_from_bytes(file_bytes, dpi=200)
            text = "\n".join([pytesseract.image_to_string(img, lang='deu') for img in images])
    else:
        text = pytesseract.image_to_string(Image.open(uploaded_file), lang='deu')
    return text.strip()

def create_ics(fristen_text):
    now = datetime.now().strftime("%Y%m%dT%H%M%SZ")
    start_date = (datetime.now() + timedelta(days=14)).strftime("%Y%m%d")
    ics_content = f"BEGIN:VCALENDAR\nVERSION:2.0\nBEGIN:VEVENT\nDTSTAMP:{now}\nDTSTART;VALUE=DATE:{start_date}\nSUMMARY:Fristende (Amtsschimmel-Killer)\nDESCRIPTION:{fristen_text.replace('\\n', ' ')}\nEND:VEVENT\nEND:VCALENDAR"
    return ics_content

class CustomPDF(FPDF):
    def header(self):
        if os.path.exists(LOGO_DATEI): self.image(LOGO_DATEI, 10, 8, 30)
        self.set_font('helvetica', 'B', 15); self.set_text_color(30, 58, 138)
        self.cell(0, 10, 'AMTSSCHIMMEL-KILLER', ln=True, align='R')
        self.line(10, 30, 200, 30); self.ln(15)
    
    def add_signature_field(self):
        self.ln(20)
        self.set_font('helvetica', '', 10)
        self.cell(0, 10, '__________________________, den __________________', ln=True)
        self.cell(0, 5, '(Ort)                                     (Datum)', ln=True)
        self.ln(15)
        self.cell(0, 10, '________________________________________________', ln=True)
        self.cell(0, 5, '(Unterschrift)', ln=True)

# --- 6. SIDEBAR ---
with st.sidebar:
    if os.path.exists(LOGO_DATEI): st.image(LOGO_DATEI, use_container_width=True)
    st.title("Konto")
    st.metric("Guthaben", f"{st.session_state.credits} Scans")
    lang = st.radio("Sprache / Language", ["Deutsch", "English"], horizontal=True)
    st.divider()
    pkgs = [("📄 Basis-Check", st.secrets["STRIPE_LINK_1"], "1 Scan", "3,99 €"),
            ("🚀 Spar-Paket", st.secrets["STRIPE_LINK_3"], "3 Scans", "9,99 €"),
            ("💎 Profi-Paket", st.secrets["STRIPE_LINK_10"], "10 Scans", "19,99 €")]
    for t, l, c, p in pkgs:
        st.markdown(f'<a href="{l}" target="_blank" class="buy-button"><b>{t}</b><br><small>{p} | {c}<br><b>KEIN ABO</b></small></a>', unsafe_allow_html=True)

# --- 7. HAUPTSEITE ---
c1, c2, c3 = st.columns(3)
with c2:
    if os.path.exists(LOGO_DATEI): st.image(LOGO_DATEI, use_container_width=True)

ui = {
    "title": "Amtsschimmel-Killer 📄🚀" if lang == "Deutsch" else "Bureaucracy Killer 📄🚀",
    "upload": "Brief hochladen" if lang == "Deutsch" else "Upload letter",
    "analyze": "🚀 Jetzt analysieren" if lang == "Deutsch" else "🚀 Analyze now",
    "print": "🖨️ Drucken" if lang == "Deutsch" else "🖨️ Print",
    "ics": "📅 Termin" if lang == "Deutsch" else "📅 Calendar"
}

st.title(ui["title"])
upload = st.file_uploader(ui["upload"], type=['png', 'jpg', 'jpeg', 'pdf'])

if upload:
    col_v, col_a = st.columns([1, 1.2])
    with col_v:
        if upload.type == "application/pdf":
            try:
                pdf_imgs = convert_from_bytes(upload.getvalue(), dpi=72, first_page=1, last_page=1)
                st.image(pdf_imgs, use_container_width=True)
            except: st.info("Preview loading...")
        else:
            st.image(upload, use_container_width=True)

    with col_a:
        if not st.session_state.last_brief:
            if st.session_state.credits > 0:
                if st.button(ui["analyze"]):
                    raw_text = get_text_hybrid(upload)
                    with st.spinner("Analyzing..."):
                        st.session_state.credits -= 1
                        sys_p = f"Legal expert. Respond in {lang}. Format: ---FRISTEN--- list, then ---BRIEF--- letter."
                        resp = client.chat.completions.create(model="gpt-4o", messages=[{"role": "system", "content": sys_p}, {"role": "user", "content": raw_text}])
                        full_res = resp.choices[0].message.content
                        if "---BRIEF---" in full_res:
                            parts = full_res.split("---BRIEF---")
                            st.session_state.last_fristen = parts[0].replace("---FRISTEN---", "").strip()
                            st.session_state.last_brief = parts[1].strip()
                        else: st.session_state.last_brief = full_res
                        st.rerun()
            else: st.warning("No credits.")

        if st.session_state.last_brief:
            st.subheader("⚠️ Fristen")
            st.markdown(f'<div class="frist-box">{st.session_state.last_fristen}</div>', unsafe_allow_html=True)
            st.download_button(ui["ics"], create_ics(st.session_state.last_fristen), "Frist.ics", "text/calendar")
            
            st.subheader("📝 Musterschreiben")
            st.code(st.session_state.last_brief, language="text")
            
            st.divider()
            c_p, c_d, c_x, c_r = st.columns(4)
            with c_p:
                if st.button(ui["print"]):
                    components.html(f"<script>var win = window.open('', '', 'height=700,width=700'); win.document.write('<pre style=\"white-space: pre-wrap; font-family: Arial;\">' + `{st.session_state.last_brief}` + '</pre>'); win.document.close(); win.print();</script>", height=0)
            with c_d:
                pdf = CustomPDF()
                pdf.add_page(); pdf.set_font("helvetica", size=11); pdf.multi_cell(0, 7, txt=st.session_state.last_brief.encode('latin-1','replace').decode('latin-1'))
                pdf.add_signature_field()
                st.download_button("📩 PDF", bytes(pdf.output()), "Amtsschimmel_Brief.pdf")
            with c_x:
                df = pd.DataFrame([{"Fristen": st.session_state.last_fristen, "Musterschreiben": st.session_state.last_brief}])
                out = io.BytesIO()
                with pd.ExcelWriter(out, engine='openpyxl') as wr:
                    df.to_excel(wr, index=False, sheet_name="Analyse")
                    ws = wr.sheets["Analyse"]
                    ws.column_dimensions['A'].width = 30
                    ws.column_dimensions['B'].width = 80
                    for cell in ws[2]: cell.alignment = Alignment(wrap_text=True, vertical="top")
                st.download_button("📊 Excel", out.getvalue(), "Analyse_Bericht.xlsx")
            with c_r:
                if st.button("🗑️ Neu"):
                    st.session_state.last_brief = ""; st.session_state.last_fristen = ""; st.rerun()
