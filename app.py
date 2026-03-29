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
**Impressum:**

**Amtsschimmel-Killer**

Betreiberin: Elisabeth Reinecke  
Ringelsweide 9  
40223 Düsseldorf

**Kontakt:**  
Telefon: +49 211 15821329  
E-Mail: amtsschimmel-killer@proton.me  
Web: amtsschimmel-killer.streamlit.app

**Haftung:**  
Inhalte nach § 5 TMG. Keine Haftung für KI-generierte Texte.
"""

DATENSCHUTZ_TEXT = """
**1. Datenschutz auf einen Blick**  
Wir behandeln Ihre personenbezogenen Daten vertraulich und entsprechend der gesetzlichen Vorschriften (DSGVO).

**2. Datenerfassung & Hosting**  
Diese App wird auf Streamlit Cloud gehostet. Beim Besuch werden Logfiles automatisch vom Hoster erfasst.

**3. Dokumentenverarbeitung**  
Ihre hochgeladenen Briefe werden per TLS-verschlüsselter Schnittstelle an OpenAI (USA) zur Analyse übertragen. Wir speichern keine Briefe auf unseren Servern.

**4. Zahlungsabwicklung (Stripe)**  
Bei Käufen werden Sie zu Stripe weitergeleitet. Stripe erhebt die erforderlichen Daten zur Abrechnung.

**5. Ihre Rechte**  
Sie haben das Recht auf Auskunft, Löschung und Sperrung Ihrer Daten. Kontakt: amtsschimmel-killer@proton.me.
"""

FAQ_TEXT = """
**Ist das ein Abonnement?**  
Nein. Wir hassen Abos genauso wie Amtsschimmel. Jede Zahlung ist eine **Einmalzahlung** für eine feste Anzahl an Scans. Es gibt keine automatische Verlängerung.

**Wie sicher sind meine Dokumente?**  
Ihre Dokumente werden verschlüsselt an die KI übertragen, dort nur kurzzeitig im Arbeitsspeicher verarbeitet und niemals dauerhaft auf unseren Servern gespeichert.

**Ersetzt die App eine Rechtsberatung?**  
Nein. Wir bieten eine Formulierungshilfe. Für verbindliche Rechtsberatung wenden Sie sich bitte an einen Rechtsanwalt.

**Was passiert, wenn der Scan fehlschlägt?**  
Ein Scan wird erst berechnet, wenn die KI den Text erfolgreich verarbeitet hat.
"""

VORLAGEN_TEXT = """
**Fristverlängerung:**  
"Sehr geehrte Damen und Herren, in der Angelegenheit [Aktenzeichen] bitte ich um Verlängerung der gesetzten Frist bis zum [Datum]..."

**Widerspruch (Fristwahrend):**  
"Sehr geehrte Damen und Herren, gegen Ihren Bescheid vom [Datum] lege ich hiermit Widerspruch ein. Begründung folgt."

**Akteneinsicht:**  
"Sehr geehrte Damen und Herren, ich beantrage hiermit Akteneinsicht gemäß § 25 SGB X."
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
# 3. EXPORT & KI LOGIK
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
# 4. UI LAYOUT OBEN (RECHTLICHES & VORLAGEN)
# ==========================================
info_col1, info_col2, info_col3, info_col4 = st.columns(4)
with info_col1:
    with st.expander("⚖️ Impressum"): st.write(IMPRESSUM_TEXT)
with info_col2:
    with st.expander("🛡️ Datenschutz"): st.write(DATENSCHUTZ_TEXT)
with info_col3:
    with st.expander("❓ FAQ"): st.write(FAQ_TEXT)
with info_col4:
    with st.expander("📋 Vorlagen"): st.write(VORLAGEN_TEXT)

st.divider()

# ==========================================
# 5. SIDEBAR (SPRACHE & SHOP)
# ==========================================
with st.sidebar:
    if os.path.exists(LOGO_DATEI): st.image(LOGO_DATEI, use_container_width=True)
    
    st.subheader("🌍 Sprache wählen")
    lang_choice = st.selectbox("Ausgabe in:", ["🇩🇪 Deutsch", "🇺🇸 English", "🇹🇷 Türkçe", "🇵🇱 Polski", "🇷🇺 Русский"], label_visibility="collapsed")
    
    st.divider()
    
    st.subheader("🛒 Scans aufladen")
    st.metric("Dein Guthaben", f"{st.session_state.credits} Scans")
    
    # Optisch hervorgehobene Pakete
    st.info("**PAKET-AUSWAHL (Einmalzahlung)**")
    
    st.link_button("☕ **1 SCAN** | 2,99€ \n (Kein Abo)", "DEIN_STRIPE_LINK_1", use_container_width=True)
    st.link_button("📦 **5 SCANS** | 9,99€ \n (Kein Abo)", "DEIN_STRIPE_LINK_5", use_container_width=True)
    st.link_button("🚀 **10 SCANS** | 14,99€ \n (Kein Abo)", "DEIN_STRIPE_LINK_10", use_container_width=True)
    
    st.warning("⚠️ **KEIN ABONNEMENT.** Sie zahlen nur, was Sie brauchen.")

# ==========================================
# 6. HAUPTBEREICH
# ==========================================
st.title("📄 Amtsschimmel-Killer")

col_main1, col_main2 = st.columns(2)

with col_main1:
    st.subheader("1. Dokument hochladen")
    u_file = st.file_uploader("Bild oder PDF hier reinziehen", type=['png', 'jpg', 'jpeg', 'pdf'])
    mode = st.radio("Gewünschtes Ziel:", ["📝 Antwortbrief", "🛑 Widerspruch"], horizontal=True)
    
    if u_file and st.button("🚀 Jetzt analysieren (-1 Scan)"):
        if st.session_state.credits > 0:
            with st.spinner("KI liest den Brief..."):
                raw = get_text(u_file)
                res = run_ai(raw, lang_choice, "W" if "Widerspruch" in mode else "A")
                if res == "FEHLER_UNSCHARF":
                    st.error("Text zu unscharf! Bitte neu fotografieren.")
                else:
                    st.session_state.full_res = res
                    st.session_state.credits -= 1
                    st.rerun()
        else:
            st.error("Guthaben leer! Bitte links ein Paket wählen.")

with col_main2:
    st.subheader("2. Analyse-Ergebnis")
    if st.session_state.full_res:
        st.markdown(st.session_state.full_res)
        st.divider()
        st.download_button("📥 Als PDF speichern", create_pdf_final(st.session_state.full_res), "Analyse.pdf")
    else:
        st.info("Das Ergebnis erscheint hier nach dem Scan.")
