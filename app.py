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

# --- 1. SEITEN-KONFIGURATION ---
st.set_page_config(page_title="Amtsschimmel-Killer", layout="wide", page_icon="🏛️")

# OpenAI API Key
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
                {"role": "system", "content": "Du bist ein Experte für deutsches Verwaltungsrecht. Erstelle ausführliche, sauber formatierte Entwürfe. Antworte NUR im JSON-Format: {'analyse': '...', 'antwort': '...', 'widerspruch': '...', 'frist': 'DD.MM.YYYY'}"},
                {"role": "user", "content": text}
            ],
            response_format={ "type": "json_object" }
        )
        data = json.loads(response.choices.message.content)
        # Fix für Zeilenumbrüche
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

def create_excel_pro(ana, ant, wid):
    output = BytesIO()
    df = pd.DataFrame([{"Kategorie": "1. Analyse", "Inhalt": ana}, {"Kategorie": "2. Antwort", "Inhalt": ant}, {"Kategorie": "3. Widerspruch", "Inhalt": wid}])
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Analyse')
        worksheet = writer.sheets['Analyse']
        wrap = writer.book.add_format({'text_wrap': True, 'valign': 'top', 'border': 1})
        worksheet.set_column(0, 0, 25, wrap)
        worksheet.set_column(1, 1, 120, wrap)
    return output.getvalue()

def perform_ocr_preview(uploaded_file):
    try:
        if uploaded_file.type == "application/pdf":
            images = convert_from_bytes(uploaded_file.getvalue())
            return "".join([pytesseract.image_to_string(img, lang='deu') + "\n" for img in images])
        return pytesseract.image_to_string(Image.open(uploaded_file), lang='deu')
    except: return "Vorschau nicht möglich."

# --- 4. TOP-BAR: RECHTLICHES (GROSSE ABSTÄNDE) ---
t1, t2, t3, t4 = st.columns(4)

with t1:
    with st.expander("⚖️ Impressum"):
        st.markdown("""
**Amtsschimmel-Killer**

Betreiberin: Elisabeth Reinecke

Ringelsweide 9

40223 Düsseldorf

&nbsp;

**Kontakt:**

Telefon: +49 211 15821329

E-Mail: amtsschimmel-killer@proton.me

Web: amtsschimmel-killer.streamlit.app

&nbsp;

**Haftung:**

Inhalte nach § 5 TMG. Keine Haftung für KI-generierte Texte.
        """)

with t2:
    with st.expander("🛡️ Datenschutz"):
        st.markdown("""
**1. Datenschutz auf einen Blick**

Wir behandeln Ihre personenbezogenen Daten vertraulich (DSGVO).

&nbsp;

**2. Datenerfassung & Hosting**

Streamlit Cloud (Hoster) erfasst Logfiles. Wir nutzen diese Daten nicht.

&nbsp;

**3. Dokumentenverarbeitung**

TLS-Verschlüsselung an OpenAI (USA). Keine Speicherung vor Ort.

&nbsp;

**4. Zahlungsabwicklung (Stripe)**

Sichere Abwicklung über Stripe.

&nbsp;

**5. Ihre Rechte**

Auskunft/Löschung: amtsschimmel-killer@proton.me.
        """)

with t3:
    with st.expander("❓ FAQ"):
        st.markdown("""
**Abonnement?**

Nein. Nur Einmalzahlungen.

&nbsp;

**Sicherheit?**

Verschlüsselt an OpenAI, danach Löschung.
        """)

with t4:
    with st.expander("📝 Vorlagen"):
        st.markdown("""
**Fristverlängerung:**

"...bitte ich um Verlängerung der Frist bis zum [Datum]..."

&nbsp;

**Widerspruch:**

"...lege ich hiermit Widerspruch ein."
        """)

st.divider()

# --- 5. HAUPT-LAYOUT ---
col_left, col_mid, col_right = st.columns([1, 1.6, 1.3])

# LINKS: PAKETE & STRIPE
with col_left:
    try: st.image("icon_final_blau.png", width=160)
    except: st.markdown("### 🏛️ Amtsschimmel-Killer")
    
    st.markdown("### 🌐 Sprachen")
    st.selectbox("Sprache", ["DE Deutsch", "EN English", "TR Türkçe", "PL Polski", "UA Українська", "RU Русский", "AR العربية", "FR Français", "IT Italiano", "ES Español", "NL Nederlands", "RO Română", "GR Ελληνικά", "CN 中文", "VN Tiếng Việt"], label_visibility="collapsed")
    st.write("")
    
    with st.container(border=True):
        st.markdown('<div class="pkg-icon">📄</div>**Analyse (1 Dokument)**<div class="pkg-price">3,99 €</div><div class="pkg-footer">EINMALZAHLUNG • KEIN ABO</div>', unsafe_allow_html=True)
        st.link_button("Jetzt kaufen", "https://buy.stripe.com")

    st.write("")
    with st.container(border=True):
        st.markdown('<div style="background-color: #ebf5fb; padding: 10px; border-radius: 10px;">'
                    '<div class="pkg-icon">🥈</div>**Spar-Paket (3 Dokumente)**<div class="pkg-price">9,99 €</div><div class="pkg-footer">EINMALZAHLUNG • KEIN ABO</div>', unsafe_allow_html=True)
        st.link_button("Jetzt kaufen", "https://buy.stripe.com/8x228retRbj50paalq1gs03")
        st.markdown('</div>', unsafe_allow_html=True)

    st.write("")
    with st.container(border=True):
        st.markdown('<div style="background-color: #fef9e7; padding: 10px; border-radius: 10px;">'
                    '<div class="pkg-icon">🥇</div>**Sorglos-Paket (10 Dokumente)**<div class="pkg-price">19,99 €</div><div class="pkg-footer">EINMALZAHLUNG • KEIN ABO</div>', unsafe_allow_html=True)
        st.link_button("Jetzt kaufen", "https://buy.stripe.com")
        st.markdown('</div>', unsafe_allow_html=True)

# MITTE: UPLOAD
with col_mid:
    st.markdown("### 📑 Upload & Vorschau")
    st.success("👑 Admin Guthaben: 999 Dokumente")
    uploaded_file = st.file_uploader("Datei hier reinziehen", type=["pdf", "jpg", "png", "jpeg"], label_visibility="collapsed")
    if uploaded_file:
        with st.spinner("Lese Dokument..."):
            ocr_text = perform_ocr_preview(uploaded_file)
        st.text_area("OCR-Vorschau:", ocr_text, height=450)

# RECHTE SPALTE: KI & DOWNLOADS
with col_right:
    st.markdown("### 🔍 Analyse & Antwort")
    if uploaded_file:
        with st.spinner("KI arbeitet..."):
            res = get_ai_analysis(ocr_text)
        
        # FRIST MIT KALENDER-ICON
        st.error(f"📅 FRIST ERKANNT: {res.get('frist', 'Nicht erkannt')}")
        st.info(res.get('analyse'))
        
        t1, t2, t3 = st.tabs(["✍️ Antwort", "⚖️ Widerspruch", "📥 Downloads"])
        with t1: st.text_area("Entwurf:", res.get('antwort'), height=350, key="txt_ans")
        with t2: st.text_area("Entwurf:", res.get('widerspruch'), height=350, key="txt_wid")
        with t3:
            st.download_button("📊 Excel", create_excel_pro(res['analyse'], res['antwort'], res['widerspruch']), "Analyse.xlsx")
            st.download_button("📝 Word", create_word_complete(res['analyse'], res['antwort'], res['widerspruch']), "Bericht.docx")
            pdf_bytes = create_pdf_adobe_ready(res['analyse'], res['antwort'], res['widerspruch'])
            st.download_button("📕 PDF", pdf_bytes, "Bericht.pdf", mime="application/pdf")
