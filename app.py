import streamlit as st
from openai import OpenAI
import pytesseract
from PIL import Image
import pdfplumber
from pdf2image import convert_from_bytes
# Import für Word
from docx import Document
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

IMPRESSUM_TEXT = """**Amtsschimmel-Killer**  
Betreiberin: Elisabeth Reinecke, Ringelsweide 9, 40223 Düsseldorf  
Telefon: +49 211 15821329 | E-Mail: amtsschimmel-killer@proton.me"""

DATENSCHUTZ_TEXT = """**1. Datenschutz:** Vertraulichkeit nach DSGVO.  
**2. Hosting:** Streamlit Cloud.  
**3. Dokumente:** Übertragung via TLS an OpenAI (USA). Keine Speicherung auf unseren Servern."""

FAQ_TEXT = """**Abo?** Nein, Einmalzahlung.  
**Sicherheit?** Dokumente werden nach Analyse sofort gelöscht."""

VORLAGEN_TEXT = """**Fristverlängerung:** 'Ich bitte um Verlängerung bis...'  
**Widerspruch:** 'Gegen den Bescheid vom... lege ich Widerspruch ein.'"""

# ==========================================
# 2. SESSION STATE
# ==========================================
if "credits" not in st.session_state: st.session_state.credits = 0
if "full_res" not in st.session_state: st.session_state.full_res = ""
if "processed_sessions" not in st.session_state: st.session_state.processed_sessions = []

# ==========================================
# 3. EXPORT FUNKTIONEN (ALLE FORMATE)
# ==========================================
def clean_txt(t):
    return t.replace("###","").replace("**","").replace("🚦","").replace("📖","").replace("📅","").replace("✍️","").replace("📋","").encode('latin-1', 'replace').decode('latin-1')

def create_pdf(text):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", 'B', 16)
    pdf.cell(0, 10, "ANALYSE-ERGEBNIS", ln=True)
    pdf.set_font("Helvetica", size=11)
    pdf.multi_cell(0, 8, txt=clean_txt(text))
    return pdf.output(dest='S').encode('latin-1')

def create_docx(text):
    doc = Document()
    doc.add_heading('Analyse-Ergebnis', 0)
    doc.add_paragraph(text.replace("#", ""))
    bio = io.BytesIO()
    doc.save(bio)
    return bio.getvalue()

def create_excel(text):
    dates = re.findall(r'(\d{2}\.\d{2}\.\d{4})', text)
    df = pd.DataFrame({"Frist/Datum": dates if dates else ["Kein Datum erkannt"], "Info": ["Wichtiger Termin" for _ in range(max(1, len(dates)))]})
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
            ics += f"BEGIN:VEVENT\nSUMMARY:Amtsschimmel Frist\nDTSTART:{cd}\nDTEND:{cd}\nEND:VEVENT\n"
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
        else:
            text = pytesseract.image_to_string(Image.open(file))
    except: pass
    return text

def run_ai(raw_text, lang, mode):
    label = "Widerspruch" if mode == "W" else "Antwortbrief"
    sys_p = f"Rechtsexperte. Sprache: {lang}. Erstelle: 🚦AMPEL, 📖GLOSSAR, 📅FRISTEN, ✍️{label}, 📋CHECKLISTE."
    resp = client.chat.completions.create(model="gpt-4o", messages=[{"role": "system", "content": sys_p}, {"role": "user", "content": raw_text}])
    return resp.choices.message.content

# ==========================================
# 5. UI - OBERE LEISTE & SIDEBAR
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

with st.sidebar:
    st.subheader("🌍 Sprache & Guthaben")
    lang_choice = st.selectbox("Ausgabe:", ["🇩🇪 Deutsch", "🇺🇸 English", "🇹🇷 Türkçe", "🇵🇱 Polski", "🇷🇺 Русский", "🇮🇹 Italiano", "🇫🇷 Français"])
    st.metric("Scans verfügbar", st.session_state.credits)
    
    st.divider()
    st.markdown("### 🛒 Scans kaufen")
    st.markdown('<div style="background-color:#f0f2f6; padding:10px; border-radius:5px; border:1px solid #ddd;"><b>BASIS</b>: 1 Scan | 3,99€<br>Einmalzahlung</div>', unsafe_allow_html=True)
    st.link_button("Basis kaufen", "DEIN_LINK_1", use_container_width=True)
    
    st.markdown('<div style="background-color:#e3f2fd; padding:10px; border-radius:5px; border:1px solid #bbdefb;"><b>SPAR</b>: 5 Scans | 9,99€<br>Einmalzahlung</div>', unsafe_allow_html=True)
    st.link_button("Spar kaufen", "DEIN_LINK_5", use_container_width=True)
    
    st.markdown('<div style="background-color:#e8f5e9; padding:10px; border-radius:5px; border:1px solid #c8e6c9;"><b>PREMIUM</b>: 10 Scans | 19,99€<br>Einmalzahlung</div>', unsafe_allow_html=True)
    st.link_button("Premium kaufen", "DEIN_LINK_10", use_container_width=True)

# ==========================================
# 6. HAUPTBEREICH (VORSCHAU LINKS | ERGEBNIS RECHTS)
# ==========================================
st.title("📄 Amtsschimmel-Killer")

col_left, col_right = st.columns([1, 1])

with col_left:
    st.subheader("1. Dokument & Vorschau")
    u_file = st.file_uploader("Bild oder PDF hochladen", type=['png', 'jpg', 'pdf'])
    
    if u_file:
        if u_file.type == "application/pdf":
            st.info("PDF hochgeladen.")
        else:
            st.image(u_file, caption="Deine Vorschau", use_container_width=True)
    
    mode = st.radio("Ziel:", ["📝 Antwortbrief", "🛑 Widerspruch"], horizontal=True)
    
    if u_file and st.button("🚀 Jetzt analysieren (-1 Scan)"):
        if st.session_state.credits > 0:
            with st.spinner("KI analysiert..."):
                raw = get_text(u_file)
                st.session_state.full_res = run_ai(raw, lang_choice, "W" if "Widerspruch" in mode else "A")
                st.session_state.credits -= 1
                st.rerun()
        else:
            st.error("Bitte Guthaben aufladen!")

with col_right:
    st.subheader("2. Analyse & Export")
    if st.session_state.full_res:
        st.markdown(st.session_state.full_res)
        st.divider()
        st.write("📥 **Ergebnis exportieren:**")
        ex1, ex2, ex3, ex4 = st.columns(4)
        with ex1: st.download_button("📄 PDF", create_pdf(st.session_state.full_res), "Analyse.pdf")
        with ex2: st.download_button("📝 Word", create_docx(st.session_state.full_res), "Analyse.docx")
        with ex3: st.download_button("📊 Excel", create_excel(st.session_state.full_res), "Fristen.xlsx")
        with ex4: st.download_button("📅 Kalender", create_ics(st.session_state.full_res), "Termin.ics")
    else:
        st.info("Das Ergebnis erscheint hier nach der Analyse.")
