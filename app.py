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
# 1. KONFIGURATION & OPTIK (STRENG FIXIERT)
# ==========================================
st.set_page_config(page_title="Amtsschimmel-Killer", page_icon="📄", layout="wide")

st.markdown("""
    <style>
        [data-testid="stSidebar"] { background-color: #f0f7ff; }
        .stDownloadButton button { width: 100%; background-color: #e1f5fe; border: 1px solid #01579b; font-weight: bold; }
        .stButton button { width: 100%; background-color: #0d47a1; color: white; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

LOGO_DATEI = "icon_final_blau.png"

# ==========================================
# 2. RECHTSTEXTE & INHALTE (WORTGENAU)
# ==========================================
IMPRESSUM_TEXT = """
**Amtsschimmel-Killer**  
Betreiberin: Elisabeth Reinecke, Ringelsweide 9, 40223 Düsseldorf  
**Kontakt:** Telefon: +49 211 15821329 | E-Mail: amtsschimmel-killer@proton.me  
**Haftung:** Inhalte nach § 5 TMG. Keine Haftung für KI-generierte Texte.
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

**Wie erreiche ich Elisabeth Reinecke?**  
Nutzen Sie einfach die E-Mail amtsschimmel-killer@proton.me oder die Telefonnummer im Impressum.
"""

VORLAGEN_TEXT = """
**Fristverlängerung:**  
Sehr geehrte Damen und Herren, in der Angelegenheit [Aktenzeichen] bitte ich um Verlängerung der gesetzten Frist bis zum [Datum], da mir noch notwendige Unterlagen fehlen. Mit freundlichen Grüßen, [Name]

**Widerspruch einlegen (Fristwahrend):**  
Sehr geehrte Damen und Herren, gegen Ihren Bescheid vom [Datum], erhalten am [Datum], lege ich hiermit Widerspruch ein. Eine detaillierte Begründung folgt in einem separaten Schreiben. Mit freundlichen Grüßen, [Name]

**Akteneinsicht einfordern:**  
Sehr geehrte Damen und Herren, zur Prüfung des Sachverhalts [Aktenzeichen] beantrage ich hiermit gemäß § 25 SGB X bzw. § 29 VwVfG Akteneinsicht. Mit freundlichen Grüßen, [Name]
"""

# ==========================================
# 3. SESSION STATE & STRIPE
# ==========================================
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

if "credits" not in st.session_state: st.session_state.credits = 0
if "full_res" not in st.session_state: st.session_state.full_res = ""
if "processed_sessions" not in st.session_state: st.session_state.processed_sessions = []

STRIPE_BASIS = "https://buy.stripe.com/eVqcN53Pd5YLgo8alq1gs02"
STRIPE_SPAR = "https://buy.stripe.com/8x228retRbj50paalq1gs03"
STRIPE_PREMIUM = "https://buy.stripe.com/28EcN50D1bj52xi8di1gs04"

# Payment-Check über URL Parameter
params = st.query_params
if "session_id" in params and params["session_id"] not in st.session_state.processed_sessions:
    try:
        st.session_state.credits += int(params.get("pack", 0))
        st.session_state.processed_sessions.append(params["session_id"])
        st.balloons()
    except: pass

# ==========================================
# 4. FUNKTIONEN (OCR & EXPORT)
# ==========================================
def extract_text(file):
    text = ""
    if file.type == "application/pdf":
        with pdfplumber.open(file) as pdf:
            for page in pdf.pages:
                c = page.extract_text()
                if c: text += c + "\n"
        if not text.strip():
            images = convert_from_bytes(file.read())
            for img in images: text += pytesseract.image_to_string(img, lang='deu') + "\n"
    else:
        img = Image.open(file)
        text = pytesseract.image_to_string(img, lang='deu')
    return text

def create_pdf(text):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", 'B', 16); pdf.cell(0, 10, "Amtsschimmel-Killer Analyse", ln=True)
    pdf.set_font("Helvetica", size=11); pdf.multi_cell(0, 8, txt=text.encode('latin-1', 'replace').decode('latin-1'))
    return pdf.output(dest='S').encode('latin-1')

def create_excel(text):
    dates = re.findall(r'(\d{2}\.\d{2}\.\d{4})', text)
    df = pd.DataFrame({"Kategorie": ["Gefundene Fristen", "Brief-Inhalt"], "Daten": [", ".join(dates) if dates else "Keine", text]})
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False)
    return output.getvalue()

def create_docx(text):
    doc = Document()
    doc.add_heading('Amtsschimmel-Killer Analyse', 0)
    doc.add_paragraph(text)
    bio = io.BytesIO()
    doc.save(bio)
    return bio.getvalue()

# ==========================================
# 5. SEITE 1: ALLES OBEN (FIXIERT)
# ==========================================
if os.path.exists(LOGO_DATEI):
    st.image(LOGO_DATEI, width=280)

st.title("Amtsschimmel-Killer 🪓")

st.subheader("FAQ")
st.markdown(FAQ_TEXT)

st.divider()

st.subheader("Pakete & Preise (Einmalzahlung)")
p1, p2, p3 = st.columns(3)
with p1: st.markdown(f"**1. Paket 3,99€**\n[Hier kaufen]({STRIPE_BASIS})")
with p2: st.markdown(f"**2. Paket 9,99€**\n[Hier kaufen]({STRIPE_SPAR})")
with p3: st.markdown(f"**3. Paket 19,99€**\n[Hier kaufen]({STRIPE_PREMIUM})")

st.divider()

st.subheader("Vorlagen")
st.markdown(VORLAGEN_TEXT)

st.divider()

# ==========================================
# 6. ARBEITSBEREICH (UNTEN)
# ==========================================
col_l, col_r = st.columns([1, 1.2])

with col_l:
    st.subheader("Brief hochladen")
    st.info(f"Aktuelles Guthaben: **{st.session_state.credits} Scans**")
    
    upped = st.file_uploader("Datei wählen (PDF oder Bild)", type=["pdf", "jpg", "png", "jpeg"])
    
    if upped and st.session_state.credits > 0:
        if st.button("🚀 JETZT ANALYSIEREN"):
            with st.spinner("Amtsschimmel wird verjagt..."):
                raw_text = extract_text(upped)
                resp = client.chat.completions.create(
                    model="gpt-4o",
                    messages=[{"role": "system", "content": "Analysiere den Brief. Trenne in: 🚦 WICHTIGKEIT, 📖 ZUSAMMENFASSUNG, 📅 FRISTEN, ✍️ ANTWORT-ENTWURF."},
                              {"role": "user", "content": raw_text}]
                )
                st.session_state.full_res = resp.choices.message.content
                st.session_state.credits -= 1
                st.rerun()

with col_r:
    st.subheader("Analyse-Ergebnis")
    if st.session_state.full_res:
        res = st.session_state.full_res
        
        # Abgegrenzte Boxen für die Übersicht
        st.info(f"### 🚦 Wichtigkeit\n{re.search(r'🚦(.*?)(?=📖|📅|✍️|$)', res, re.S).group(1) if '🚦' in res else 'Siehe Text'}")
        st.write(f"### 📖 Zusammenfassung\n{re.search(r'📖(.*?)(?=📅|✍️|$)', res, re.S).group(1) if '📖' in res else 'Siehe Text'}")
        st.warning(f"### 📅 Fristen\n{re.search(r'📅(.*?)(?=✍️|$)', res, re.S).group(1) if '📅' in res else 'Keine Fristen erkannt'}")
        st.success(f"### ✍️ Antwort-Entwurf\n{re.search(r'✍️(.*)', res, re.S).group(1) if '✍️' in res else 'Entwurf im Text'}")
        
        st.divider()
        st.subheader("Downloads")
        d1, d2, d3, d4 = st.columns(4)
        with d1: st.download_button("📄 PDF", create_pdf(res), "Analyse.pdf")
        with d2: st.download_button("📝 Word", create_docx(res), "Analyse.docx")
        with d3: st.download_button("📊 Excel", create_excel(res), "Fristen.xlsx")
        with d4: st.download_button("📅 .ics", b"BEGIN:VCALENDAR\nEND:VCALENDAR", "Termin.ics")
    else:
        st.info("Hier erscheint das Ergebnis nach dem Upload.")

# Sidebar für das Kleingedruckte
with st.sidebar:
    st.markdown("### Impressum & Datenschutz")
    with st.expander("⚖️ Impressum"): st.markdown(IMPRESSUM_TEXT)
    with st.expander("🛡️ Datenschutz"): st.markdown(re.sub(r'\n\d\.', '\n\n\g<0>', st.secrets.get("DS_TEXT", "Datenschutz siehe oben")))

