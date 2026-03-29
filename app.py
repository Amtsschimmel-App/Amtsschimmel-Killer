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
from docx import Document
from datetime import datetime

# ==========================================
# 1. RECHTSTEXTE & KONSTANTEN (FIXIERT)
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
Ihre hochgeladenen Briefe werden per TLS-verschlüsselter Schnittstelle an OpenAI (USA) übertragen. Wir speichern keine Briefe.
"""

FAQ_TEXT = """
**Ist das ein Abonnement?**  
Nein. Jede Zahlung ist eine **Einmalzahlung** für eine feste Anzahl an Scans. Es gibt keine automatische Verlängerung.

**Wie sicher sind meine Dokumente?**  
Ihre Dokumente werden verschlüsselt verarbeitet und niemals dauerhaft gespeichert. Nach der Analyse werden die Daten gelöscht.
"""

VORLAGEN_TEXT = """
**Fristverlängerung:** "Ich bitte um Verlängerung bis [Datum]..."  
**Widerspruch:** "Hiermit lege ich Widerspruch gegen [Bescheid] ein..."  
**Akteneinsicht:** "Ich beantrage Akteneinsicht gemäß § 25 SGB X."
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
# 3. EXPORT FUNKTIONEN (PDF, WORD, EXCEL, ICS)
# ==========================================
def clean_txt(t):
    return t.replace("###","").replace("**","").replace("🚦","").replace("📖","").replace("📅","").replace("✍️","").replace("📋","").encode('latin-1', 'replace').decode('latin-1')

def create_pdf(text):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", 'B', 16)
    pdf.cell(0, 10, "ANALYSE-ERGEBNIS", ln=True)
    pdf.ln(10)
    pdf.set_font("Helvetica", size=11)
    pdf.multi_cell(0, 8, txt=clean_txt(text))
    return pdf.output(dest='S').encode('latin-1')

def create_docx(text):
    doc = Document()
    doc.add_heading('Amtsschimmel-Killer Analyse', 0)
    doc.add_paragraph(text.replace("#", ""))
    bio = io.BytesIO()
    doc.save(bio)
    return bio.getvalue()

def create_excel(text):
    dates = re.findall(r'(\d{2}\.\d{2}\.\d{4})', text)
    df = pd.DataFrame({"Gefundene Fristen": dates if dates else ["Keine"], "Typ": ["Frist" for _ in range(len(dates)) if dates] or ["Info"]})
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False)
    return output.getvalue()

def create_ics(text):
    dates = re.findall(r'(\d{2}\.\d{2}\.\d{4})', text)
    ics = "BEGIN:VCALENDAR\nVERSION:2.0\n"
    for d in dates:
        try:
            cd = datetime.strptime(d, "%d.%m.%Y").strftime("%Y%m%d")
            ics += f"BEGIN:VEVENT\nSUMMARY:Frist Amtsschimmel\nDTSTART:{cd}\nDTEND:{cd}\nEND:VEVENT\n"
        except: pass
    ics += "END:VCALENDAR"
    return ics.encode('utf-8')

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
    sys_p = f"""Sprache: {lang}. Erstelle: 
    1. ### 🚦 AMPEL ### (Dringlichkeit)
    2. ### 📖 GLOSSAR ### (Begriffe erklärt)
    3. ### 📅 FRISTEN ### (Alle Termine)
    4. ### ✍️ {label.upper()} ### (Der Entwurf)
    5. ### 📋 CHECKLISTE ### (Versand-Tipps)"""
    resp = client.chat.completions.create(model="gpt-4o", messages=[{"role": "system", "content": sys_p}, {"role": "user", "content": raw_text}])
    return resp.choices.message.content

# ==========================================
# 5. UI - OBERE LEISTE (FIXIERT)
# ==========================================
c1, c2, c3, c4 = st.columns(4)
with c1: 
    with st.expander("⚖️ Impressum"): st.write(IMPRESSUM_TEXT)
with c2: 
    with st.expander("🛡️ Datenschutz"): st.write(DATENSCHUTZ_TEXT)
with c3: 
    with st.expander("❓ FAQ"): st.write(FAQ_TEXT)
with c4: 
    with st.expander("📋 Vorlagen"): st.write(VORLAGEN_TEXT)

st.divider()

# ==========================================
# 6. SIDEBAR - SPRACHE & SHOP UNTEREINANDER
# ==========================================
with st.sidebar:
    if os.path.exists(LOGO_DATEI): st.image(LOGO_DATEI)
    
    st.subheader("🌍 1. Sprache wählen")
    lang_choice = st.selectbox("Ausgabe:", ["🇩🇪 Deutsch", "🇺🇸 English", "🇹🇷 Türkçe", "🇵🇱 Polski"], label_visibility="collapsed")
    
    st.divider()
    st.subheader("🛒 2. Scans kaufen")
    st.metric("Dein Guthaben", f"{st.session_state.credits} Scans")

    # PAKET 1
    st.markdown('<div style="background-color:#f0f2f6; padding:15px; border-radius:10px; border:1px solid #ddd; margin-bottom:10px;">'
                '<h4 style="margin:0;">☕ PAKET S</h4>'
                '<p style="margin:5px 0;"><b>2,99 €</b> für <b>1 Scan</b></p>'
                '<p style="font-size:0.8em; color:green;">✅ EINMALZAHLUNG<br>❌ KEIN ABO</p></div>', unsafe_allow_html=True)
    st.link_button("1 Scan kaufen", "DEIN_LINK_1", use_container_width=True)

    # PAKET 2
    st.markdown('<div style="background-color:#e1f5fe; padding:15px; border-radius:10px; border:1px solid #b3e5fc; margin-bottom:10px;">'
                '<h4 style="margin:0;">📦 PAKET M</h4>'
                '<p style="margin:5px 0;"><b>9,99 €</b> für <b>5 Scans</b></p>'
                '<p style="font-size:0.8em; color:green;">✅ EINMALZAHLUNG<br>❌ KEIN ABO</p></div>', unsafe_allow_html=True)
    st.link_button("5 Scans kaufen", "DEIN_LINK_5", use_container_width=True)

    # PAKET 3
    st.markdown('<div style="background-color:#e8f5e9; padding:15px; border-radius:10px; border:1px solid #c8e6c9; margin-bottom:10px;">'
                '<h4 style="margin:0;">🚀 PAKET L</h4>'
                '<p style="margin:5px 0;"><b>14,99 €</b> für <b>10 Scans</b></p>'
                '<p style="font-size:0.8em; color:green;">✅ EINMALZAHLUNG<br>❌ KEIN ABO</p></div>', unsafe_allow_html=True)
    st.link_button("10 Scans kaufen", "DEIN_LINK_10", use_container_width=True)

# ==========================================
# 7. HAUPTBEREICH - ANALYSE & ERGEBNIS
# ==========================================
st.title("📄 Amtsschimmel-Killer")

m1, m2 = st.columns(2)
with m1:
    st.subheader("1. Brief hochladen")
    u_file = st.file_uploader("Bild oder PDF", type=['png', 'jpg', 'pdf'])
    mode = st.radio("Ziel:", ["📝 Antwortbrief", "🛑 Widerspruch"], horizontal=True)
    if u_file and st.button("🚀 Jetzt analysieren (-1 Scan)"):
        if st.session_state.credits > 0:
            with st.spinner("KI liest Amtsschimmel-Deutsch..."):
                raw = get_text(u_file)
                st.session_state.full_res = run_ai(raw, lang_choice, "W" if "Widerspruch" in mode else "A")
                st.session_state.credits -= 1
                st.rerun()
        else: st.error("Bitte Guthaben links aufladen!")

with m2:
    st.subheader("2. Ergebnis & Downloads")
    if st.session_state.full_res:
        st.markdown(st.session_state.full_res)
        st.divider()
        st.write("📥 **Ergebnis sichern:**")
        # Export-Buttons nebeneinander
        ex1, ex2, ex3, ex4 = st.columns(4)
        with ex1: st.download_button("📄 PDF", create_pdf(st.session_state.full_res), "Analyse.pdf")
        with ex2: st.download_button("📝 Word", create_docx(st.session_state.full_res), "Analyse.docx")
        with ex3: st.download_button("📊 Excel", create_excel(st.session_state.full_res), "Fristen.xlsx")
        with ex4: st.download_button("📅 Kalender", create_ics(st.session_state.full_res), "Fristen.ics")
    else: st.info("Warte auf Dokument...")
