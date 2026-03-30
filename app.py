import streamlit as st
import pandas as pd
from io import BytesIO
from docx import Document
from fpdf import FPDF
import pytesseract
from PIL import Image
from pdf2image import convert_from_bytes
import openai
import json
from datetime import datetime, timedelta

# --- 1. SEITEN-KONFIGURATION ---
st.set_page_config(page_title="Amtsschimmel-Killer", layout="wide", page_icon="🏛️")

# OpenAI API Key aus den Secrets
if "OPENAI_API_KEY" in st.secrets:
    openai.api_key = st.secrets["OPENAI_API_KEY"]

# --- 2. CUSTOM CSS ---
st.markdown("""
    <style>
    .pkg-icon { font-size: 2rem; margin-bottom: 0.5rem; }
    .pkg-price { font-size: 1.5rem; font-weight: bold; color: #1E3A8A; margin: 0.5rem 0; }
    .pkg-footer { font-size: 0.8rem; color: gray; margin-bottom: 1rem; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. FUNKTIONEN ---
def get_ai_analysis(text):
    try:
        client = openai.OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "Du bist ein Experte für deutsches Verwaltungsrecht. Erstelle SEHR AUSFÜHRLICHE, rechtlich fundierte Entwürfe. Die Antwortschreiben und Widersprüche müssen lang und detailliert sein. Füge UNTEN in jedem Schreiben (Antwort & Widerspruch) zwingend Platzhalter für Name und Adresse ein: [Vorname Nachname], [Straße Hausnummer], [PLZ Ort], [Datum]. Antworte NUR im JSON-Format: {'analyse': '...', 'antwort': '...', 'widerspruch': '...', 'frist': 'DD.MM.YYYY'}"},
                {"role": "user", "content": text}
            ],
            response_format={ "type": "json_object" }
        )
        data = json.loads(response.choices[0].message.content)
        for key in ['analyse', 'antwort', 'widerspruch']:
            data[key] = data[key].replace('\\n', '\n')
        return data
    except Exception as e:
        return {"analyse": f"Fehler: {str(e)}", "antwort": "Fehler", "widerspruch": "Fehler", "frist": "Nicht erkannt"}

def create_pdf_adobe_ready(analyse, antwort, widerspruch):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.set_font("helvetica", 'B', 16)
    pdf.cell(0, 10, "Amtsschimmel-Killer Analyse-Report", ln=True, align='C')
    for title, content in [("1. Analyse", analyse), ("2. Antwort", antwort), ("3. Widerspruch", widerspruch)]:
        pdf.ln(10)
        pdf.set_font("helvetica", 'B', 14)
        pdf.cell(0, 10, title, ln=True)
        pdf.set_font("helvetica", '', 11)
        safe_text = str(content).replace('•', '-').replace('–', '-').replace('„', '"').replace('“', '"')
        pdf.multi_cell(0, 6, safe_text.encode('latin-1', 'replace').decode('latin-1'))
    return bytes(pdf.output())

def create_word_complete(analyse, antwort, widerspruch):
    doc = Document()
    doc.add_heading('Amtsschimmel-Killer Report', 0)
    for title, content in [("Analyse", analyse), ("Antwort", antwort), ("Widerspruch", widerspruch)]:
        doc.add_heading(title, level=1)
        doc.add_paragraph(str(content))
    target = BytesIO()
    doc.save(target)
    return target.getvalue()

def perform_ocr_preview(uploaded_file):
    try:
        if uploaded_file.type == "application/pdf":
            images = convert_from_bytes(uploaded_file.getvalue())
            return "".join([pytesseract.image_to_string(img, lang='deu') + "\n" for img in images])
        return pytesseract.image_to_string(Image.open(uploaded_file), lang='deu')
    except: return "Vorschau nicht möglich."

# --- 4. TOP-BAR: RECHTLICHES ---
t1, t2, t3, t4 = st.columns(4)
with t1:
    with st.expander("⚖️ Impressum"):
        st.markdown("Amtsschimmel-Killer\nBetreiberin:\nElisabeth Reinecke\nRingelsweide 9\n40223 Düsseldorf\n\nKontakt:\nTelefon: +49 211 15821329\nE-Mail: amtsschimmel-killer@proton.me\nWeb: amtsschimmel-killer.streamlit.app\n\nHaftung:\nInhalte nach § 5 TMG.\nKeine Haftung für KI-generierte Texte.", unsafe_allow_html=True)
with t2:
    with st.expander("🛡️ Datenschutz"):
        st.markdown("1. Datenschutz auf einen Blick...\n2. Datenerfassung...\n3. Dokumentenverarbeitung...\n4. Stripe...\n5. Ihre Rechte...")
with t3:
    with st.expander("❓ FAQ"):
        st.markdown("Ist das ein Abonnement? Nein...\nWie sicher sind meine Dokumente?...\nErsetzt die App eine Rechtsberatung?...")
with t4:
    with st.expander("📝 Vorlagen"):
        st.markdown("Fristverlängerung...\nWiderspruch einlegen...\nAkteneinsicht einfordern...")

st.divider()

# --- 5. HAUPT-LAYOUT ---
col_left, col_mid, col_right = st.columns([1, 1.6, 1.3])

with col_left:
    try: st.image("icon_final_blau.png", width=160)
    except: st.markdown("### 🏛️ Amtsschimmel-Killer")
    st.markdown("### 🌐 Sprachen")
    st.selectbox("Sprache wählen", ["DE Deutsch", "EN English", "TR Türkçe", "PL Polski", "UA Українська", "RU Русский", "AR العربية", "FR Français", "IT Italiano", "ES Español", "NL Nederlands", "RO Română", "GR Ελληνικά", "CN 中文", "VN Tiếng Việt"], label_visibility="collapsed")
    st.write("")

    with st.container(border=True):
        st.markdown('<div class="pkg-icon">📄</div>**Analyse (1 Dokument)**<div class="pkg-price">3,99 €</div><div class="pkg-footer">EINMALZAHLUNG • KEIN ABO</div>', unsafe_allow_html=True)
        st.link_button("Jetzt kaufen", "https://buy.stripe.com/eVqcN53Pd5YLgo8alq1gs02", use_container_width=True)

    with st.container(border=True):
        st.markdown('<div style="background-color: #ebf5fb; padding: 10px; border-radius: 10px;">'
                    '<div class="pkg-icon">🥈</div>**Spar-Paket (3 Dokumente)**<div class="pkg-price">9,99 €</div><div class="pkg-footer">EINMALZAHLUNG • KEIN ABO</div>', unsafe_allow_html=True)
        st.link_button("Jetzt kaufen", "https://buy.stripe.com/8x228retRbj50paalq1gs03", use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with st.container(border=True):
        st.markdown('<div style="background-color: #fef9e7; padding: 10px; border-radius: 10px;">'
                    '<div class="pkg-icon">🥇</div>**Sorglos-Paket (10 Dokumente)**<div class="pkg-price">19,99 €</div><div class="pkg-footer">EINMALZAHLUNG • KEIN ABO</div>', unsafe_allow_html=True)
        st.link_button("Jetzt kaufen", "https://buy.stripe.com/28EcN50D1bj52xi8di1gs04", use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

with col_mid:
    st.subheader("1. Dokument hochladen")
    uploaded_file = st.file_uploader("Brief fotografieren oder PDF wählen", type=['pdf', 'png', 'jpg', 'jpeg'], label_visibility="collapsed")
    
    st.write("---")
    st.subheader("📅 Frist-Checker")
    erhalt_datum = st.date_input("Wann haben Sie den Brief erhalten?", datetime.now())
    frist_ende = erhalt_datum + timedelta(days=30)
    st.info(f"Die gesetzliche Frist (1 Monat) endet voraussichtlich am: **{frist_ende.strftime('%d.%m.%Y')}**")

    if uploaded_file and st.button("Analyse starten ✨", use_container_width=True):
        with st.spinner("Amtsschimmel wird vertrieben..."):
            text_content = perform_ocr_preview(uploaded_file)
            st.session_state['analysis_results'] = get_ai_analysis(text_content)

with col_right:
    st.subheader("2. Ergebnisse")
    if 'analysis_results' in st.session_state:
        res = st.session_state['analysis_results']
        t1, t2, t3 = st.tabs(["Analyse", "Antwortbrief", "Widerspruch"])
        with t1: st.write(res['analyse'])
        with t2: st.text_area("Entwurf (lang):", res['antwort'], height=400)
        with t3: st.text_area("Entwurf (lang):", res['widerspruch'], height=400)
        
        st.divider()
        c1, c2 = st.columns(2)
        with c1: st.download_button("📥 PDF", create_pdf_adobe_ready(res['analyse'], res['antwort'], res['widerspruch']), "Analyse.pdf", use_container_width=True)
        with c2: st.download_button("📥 Word", create_word_complete(res['analyse'], res['antwort'], res['widerspruch']), "Analyse.docx", use_container_width=True)
    else:
        st.info("Bitte Dokument hochladen und Analyse starten.")
