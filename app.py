import streamlit as st
from openai import OpenAI
import pytesseract
from PIL import Image
import pdfplumber
from pdf2image import convert_from_bytes
import io
import os
import pandas as pd
import re
from fpdf import FPDF 
from datetime import datetime

# ==========================================
# 1. RECHTSTEXTE & KONSTANTEN (FIXIERT)
# ==========================================
st.set_page_config(page_title="Amtsschimmel-Killer", page_icon="📄", layout="wide")

LOGO_DATEI = "icon_final_blau.png"

IMPRESSUM_TEXT = """
**Amtsschimmel-Killer**  
Betreiberin: Elisabeth Reinecke  
Ringelsweide 9  
40223 Düsseldorf  
**Kontakt:**  
Telefon: +49 211 15821329  
E-Mail: amtsschimmel-killer@proton.me  
"""

DATENSCHUTZ_TEXT = """
**Datenschutz**  
Ihre Dokumente werden per TLS-verschlüsselter Schnittstelle an OpenAI übertragen, dort nur kurzzeitig im Arbeitsspeicher verarbeitet und niemals dauerhaft gespeichert.
"""

FAQ_TEXT = """
**Ist das ein Abo?** Nein, Einmalzahlungen.  
**Sicherheit?** Keine dauerhafte Speicherung Ihrer Briefe.
"""

VORLAGEN = [
    ("Fristverlängerung", "Sehr geehrte Damen und Herren, in der Angelegenheit [Aktenzeichen] bitte ich um Verlängerung der Frist bis zum [Datum]..."),
    ("Widerspruch (Fristwahrend)", "Sehr geehrte Damen und Herren, gegen Ihren Bescheid vom [Datum] lege ich hiermit Widerspruch ein..."),
    ("Akteneinsicht", "Sehr geehrte Damen und Herren, ich beantrage hiermit Akteneinsicht gemäß § 25 SGB X...")
]

# STRIPE LINKS (HIER DEINE LINKS EINTRAGEN)
STRIPE_1_SCAN = "https://buy.stripe.com" 
STRIPE_5_SCANS = "https://buy.stripe.com"
STRIPE_10_SCANS = "https://buy.stripe.com0"

# ==========================================
# 2. SESSION STATE & ZAHLUNGSLOGIK
# ==========================================
if "credits" not in st.session_state: st.session_state.credits = 0
if "full_res" not in st.session_state: st.session_state.full_res = ""
if "processed_sessions" not in st.session_state: st.session_state.processed_sessions = []

# Admin & Zahlungs-Handling
params = st.query_params
if params.get("admin") == "GeheimAmt2024!" and st.session_state.credits < 500:
    st.session_state.credits = 999

if "session_id" in params and params["session_id"] not in st.session_state.processed_sessions:
    try:
        st.session_state.credits += int(params.get("pack", 0))
        st.session_state.processed_sessions.append(params["session_id"])
        st.balloons()
        st.success(f"Erfolgreich geladen! +{params.get('pack')} Scans.")
    except: pass

# ==========================================
# 3. EXPORT FUNKTIONEN
# ==========================================
def clean_txt(t):
    return t.replace("###","").replace("**","").replace("🚦","").replace("📖","").replace("📅","").replace("✍️","").replace("📋","").encode('latin-1', 'replace').decode('latin-1')

def create_pdf_final(text):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", 'B', 16)
    pdf.cell(0, 10, "ANALYSE-ERGEBNIS", ln=True)
    pdf.ln(10)
    pdf.set_font("Helvetica", size=11)
    pdf.multi_cell(0, 8, txt=clean_txt(text))
    return pdf.output(dest='S').encode('latin-1')

def create_excel_final(text):
    dates = re.findall(r'(\d{2}\.\d{2}\.\d{4})', text)
    if not dates: dates = ["Nicht erkannt"]
    df = pd.DataFrame({"Datum": dates, "Inhalt": [text[:200] for _ in range(len(dates))]})
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False)
    return output.getvalue()

# ==========================================
# 4. KI-LOGIK
# ==========================================
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

def get_text(file):
    text = ""
    try:
        if file.type == "application/pdf":
            with pdfplumber.open(file) as pdf:
                for page in pdf.pages: text += page.extract_text() or ""
            if len(text.strip()) < 30:
                imgs = convert_from_bytes(file.getvalue())
                for i in imgs: text += pytesseract.image_to_string(i)
        else:
            text = pytesseract.image_to_string(Image.open(file))
    except: pass
    return text

def run_ai(raw_text, lang, mode):
    if len(raw_text.strip()) < 40: return "FEHLER_UNSCHARF"
    label = "Widerspruch" if mode == "W" else "Antwortbrief"
    sys_p = f"Rechtsexperte. Sprache: {lang}. Erstelle 1. Ampel, 2. Dolmetscher, 3. Fristen, 4. {label}, 5. Checkliste."
    resp = client.chat.completions.create(model="gpt-4o", messages=[{"role": "system", "content": sys_p}, {"role": "user", "content": raw_text}])
    return resp.choices.message.content

# ==========================================
# 5. UI (SIDEBAR MIT SHOP)
# ==========================================
with st.sidebar:
    if os.path.exists(LOGO_DATEI): st.image(LOGO_DATEI, use_container_width=True)
    st.metric("Dein Guthaben", f"{st.session_state.credits} Scans")
    
    st.subheader("🛒 Scans aufladen")
    st.link_button("☕ 1 Scan - 2,99€", STRIPE_1_SCAN, use_container_width=True)
    st.link_button("📦 5 Scans - 9,99€", STRIPE_5_SCANS, use_container_width=True)
    st.link_button("🚀 10 Scans - 14,99€", STRIPE_10_SCANS, use_container_width=True)
    
    st.divider()
    lang_choice = st.selectbox("🌍 Sprache", ["🇩🇪 Deutsch", "🇺🇸 English", "🇹🇷 Türkçe", "🇵🇱 Polski"])
    
    with st.expander("ℹ️ Impressum"): st.write(IMPRESSUM_TEXT)
    with st.expander("🛡️ Datenschutz"): st.write(DATENSCHUTZ_TEXT)
    with st.expander("❓ FAQ"): st.write(FAQ_TEXT)

# ==========================================
# MAIN UI
# ==========================================
st.title("📄 Amtsschimmel-Killer")
col1, col2 = st.columns(2)

with col1:
    st.subheader("1. Brief hochladen")
    u_file = st.file_uploader("Bild oder PDF", type=['png', 'jpg', 'pdf'])
    mode = st.radio("Ziel:", ["📝 Antwortbrief", "🛑 Widerspruch"])
    
    if u_file and st.button("🚀 Analyse starten (-1 Scan)"):
        if st.session_state.credits > 0:
            with st.spinner("KI arbeitet..."):
                raw = get_text(u_file)
                res = run_ai(raw, lang_choice, "W" if "Widerspruch" in mode else "A")
                if res == "FEHLER_UNSCHARF": st.error("Bitte schärferes Foto!")
                else:
                    st.session_state.full_res = res
                    st.session_state.credits -= 1
                    st.rerun()
        else: st.warning("Bitte Scans kaufen!")

with col2:
    st.subheader("2. Ergebnis")
    if st.session_state.full_res:
        st.markdown(st.session_state.full_res)
        st.download_button("📥 PDF", create_pdf_final(st.session_state.full_res), "Analyse.pdf")
    else: st.info("Warte auf Upload...")

st.divider()
st.subheader("📋 Vorlagen")
for t, txt in VORLAGEN:
    with st.expander(t): st.code(txt)
