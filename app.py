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
# 1. KONFIGURATION & TEXTE (FIXIERT)
# ==========================================
st.set_page_config(page_title="Amtsschimmel-Killer", page_icon="📄", layout="wide")

LOGO_DATEI = "icon_final_blau.png"

IMPRESSUM_TEXT = """
**Amtsschimmel-Killer**  
Betreiberin: Elisabeth Reinecke  
Ringelsweide 9, 40223 Düsseldorf  
**Kontakt:**  
Telefon: +49 211 15821329  
E-Mail: amtsschimmel-killer@proton.me  
Web: amtsschimmel-killer.streamlit.app  
**Haftung:** Inhalte nach § 5 TMG. Keine Haftung für KI-Texte.
"""

DATENSCHUTZ_TEXT = """
**1. Datenschutz:** Vertrauliche Behandlung nach DSGVO.  
**2. Hosting:** Streamlit Cloud (Logfiles durch Hoster).  
**3. Dokumente:** TLS-Übertragung an OpenAI (USA). Keine dauerhafte Speicherung.  
**4. Stripe:** Daten nur zur Abrechnung.  
**5. Rechte:** Auskunft/Löschung via amtsschimmel-killer@proton.me.
"""

FAQ_TEXT = """
**Ist das ein Abonnement?**  
Nein. Wir hassen Abos genauso wie Amtsschimmel. Jede Zahlung ist eine Einmalzahlung für eine feste Anzahl an Scans. Es gibt keine automatische Verlängerung.

**Wie sicher sind meine Dokumente?**  
Ihre Dokumente werden verschlüsselt an die KI (OpenAI) übertragen, dort nur kurzzeitig im Arbeitsspeicher verarbeitet und niemals dauerhaft auf unseren Servern gespeichert. Nach der Analyse werden die Daten gelöscht.

**Ersetzt die App eine Rechtsberatung?**  
Nein. Wir bieten eine Formulierungshilfe und Unterstützung beim Textverständnis. Für verbindliche Rechtsberatung wenden Sie sich bitte an einen Rechtsanwalt.

**Was passiert, wenn der Scan fehlschlägt?**  
Ein Scan wird erst berechnet, wenn die KI den Text erfolgreich verarbeitet hat. Sollte ein Upload technisch scheitern (z.B. wegen eines unscharfen Fotos), wird kein Guthaben abgezogen.
"""

VORLAGEN = """
**Fristverlängerung:**  
"Sehr geehrte Damen und Herren, in der Angelegenheit [Aktenzeichen] bitte ich um Verlängerung der gesetzten Frist bis zum [Datum], da mir noch notwendige Unterlagen fehlen."

**Widerspruch (Fristwahrend):**  
"Sehr geehrte Damen und Herren, gegen Ihren Bescheid vom [Datum], erhalten am [Datum], lege ich hiermit Widerspruch ein. Begründung folgt."

**Akteneinsicht:**  
"Sehr geehrte Damen und Herren, zur Prüfung des Sachverhalts [Aktenzeichen] beantrage ich hiermit Akteneinsicht gemäß § 25 SGB X."
"""

# ==========================================
# 2. SESSION STATE & ZAHLUNG
# ==========================================
if "credits" not in st.session_state: st.session_state.credits = 0
if "full_res" not in st.session_state: st.session_state.full_res = ""
if "processed_sessions" not in st.session_state: st.session_state.processed_sessions = []

params = st.query_params
if params.get("admin") == "GeheimAmt2024!" and st.session_state.credits < 500:
    st.session_state.credits = 999

if "session_id" in params and params["session_id"] not in st.session_state.processed_sessions:
    try:
        st.session_state.credits += int(params.get("pack", 0))
        st.session_state.processed_sessions.append(params["session_id"])
        st.balloons()
    except: pass

# ==========================================
# 3. HILFSFUNKTIONEN (EXPORT & KI)
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
# 4. UI LAYOUT OBEN (INFO-LEISTE)
# ==========================================
info_col1, info_col2, info_col3, info_col4 = st.columns(4)
with info_col1:
    with st.expander("⚖️ Impressum"): st.write(IMPRESSUM_TEXT)
with info_col2:
    with st.expander("🛡️ Datenschutz"): st.write(DATENSCHUTZ_TEXT)
with info_col3:
    with st.expander("❓ FAQ"): st.write(FAQ_TEXT)
with info_col4:
    with st.expander("📋 Vorlagen"): st.write(VORLAGEN)

st.divider()

# ==========================================
# 5. SIDEBAR (SPRACHE & SHOP)
# ==========================================
with st.sidebar:
    if os.path.exists(LOGO_DATEI): st.image(LOGO_DATEI, use_container_width=True)
    
    st.header("🌍 Sprache")
    lang_choice = st.selectbox("Ausgabe-Sprache:", ["🇩🇪 Deutsch", "🇺🇸 English", "🇹🇷 Türkçe", "🇵🇱 Polski", "🇷🇺 Русский"])
    
    st.divider()
    
    st.header("🛒 Guthaben")
    st.metric("Verfügbare Scans", f"{st.session_state.credits}")
    
    st.subheader("Scans kaufen (Einmalzahlung)")
    st.link_button("☕ 1 Scan - 2,99€", "DEIN_STRIPE_LINK_1", use_container_width=True)
    st.link_button("📦 5 Scans - 9,99€", "DEIN_STRIPE_LINK_5", use_container_width=True)
    st.link_button("🚀 10 Scans - 14,99€", "DEIN_STRIPE_LINK_10", use_container_width=True)
    st.caption("KEIN Abo! Keine automatische Verlängerung.")

# ==========================================
# 6. HAUPTBEREICH
# ==========================================
st.title("📄 Amtsschimmel-Killer")

col_main1, col_main2 = st.columns(2)

with col_main1:
    st.subheader("1. Brief hochladen")
    u_file = st.file_uploader("Datei wählen (PDF oder Bild)", type=['png', 'jpg', 'jpeg', 'pdf'])
    mode = st.radio("Was soll erstellt werden?", ["📝 Antwortbrief", "🛑 Widerspruch"], horizontal=True)
    
    if u_file and st.button("🚀 Jetzt analysieren (-1 Scan)"):
        if st.session_state.credits > 0:
            with st.spinner("KI liest Dokument..."):
                raw = get_text(u_file)
                res = run_ai(raw, lang_choice, "W" if "Widerspruch" in mode else "A")
                if res == "FEHLER_UNSCHARF":
                    st.error("Text zu unscharf! Bitte neu fotografieren.")
                else:
                    st.session_state.full_res = res
                    st.session_state.credits -= 1
                    st.rerun()
        else:
            st.warning("Bitte Scans im Shop aufladen.")

with col_main2:
    st.subheader("2. Analyse-Ergebnis")
    if st.session_state.full_res:
        st.markdown(st.session_state.full_res)
        st.divider()
        st.download_button("📥 Als PDF speichern", create_pdf_final(st.session_state.full_res), "Analyse.pdf")
    else:
        st.info("Das Ergebnis erscheint hier nach dem Scan.")
