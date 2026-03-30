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

# --- 3. FUNKTIONEN (KI, EXCEL MIT BREITEN SPALTEN, WORD) ---
def get_ai_analysis(text):
    try:
        client = openai.OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
        sys_msg = (
            "Du bist ein Experte für deutsches Verwaltungsrecht. Erstelle SEHR AUSFÜHRLICHE Entwürfe. "
            "Antwortschreiben und Widerspruch müssen detailliert sein und folgende Platzhalter am Ende enthalten: "
            "[Vorname Nachname], [Straße Hausnummer], [PLZ Ort], [Datum]. "
            "Antworte NUR im JSON-Format: {'analyse': '...', 'antwort': '...', 'widerspruch': '...', 'frist': 'DD.MM.YYYY'}"
        )
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "system", "content": sys_msg}, {"role": "user", "content": text}],
            response_format={ "type": "json_object" }
        )
        return json.loads(response.choices.message.content)
    except:
        return {"analyse": "Fehler bei der Analyse", "antwort": "Fehler", "widerspruch": "Fehler"}

def create_excel_pro(ana, ant, wid):
    output = BytesIO()
    df = pd.DataFrame([{"Kategorie": "Analyse", "Inhalt": ana}, {"Kategorie": "Antwort", "Inhalt": ant}, {"Kategorie": "Widerspruch", "Inhalt": wid}])
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Ergebnis')
        worksheet = writer.sheets['Ergebnis']
        wrap = writer.book.add_format({'text_wrap': True, 'valign': 'top', 'border': 1})
        worksheet.set_column(0, 0, 20, wrap)
        worksheet.set_column(1, 1, 120, wrap)
    return output.getvalue()

def create_word_complete(ana, ant, wid):
    doc = Document()
    doc.add_heading('Amtsschimmel-Killer Analyse-Report', 0)
    for t, c in [("1. Analyse", ana), ("2. Antwortschreiben", ant), ("3. Widerspruch", wid)]:
        doc.add_heading(t, level=1)
        doc.add_paragraph(str(c))
    target = BytesIO()
    doc.save(target)
    return target.getvalue()

def perform_ocr_preview(uploaded_file):
    try:
        if uploaded_file.type == "application/pdf":
            images = convert_from_bytes(uploaded_file.getvalue())
            return "".join([pytesseract.image_to_string(img, lang='deu') + "\n" for img in images])
        return pytesseract.image_to_string(Image.open(uploaded_file), lang='deu')
    except: return "OCR fehlgeschlagen."

# --- 4. TOP-BAR: RECHTLICHES ---
t1, t2, t3, t4 = st.columns(4)
with t1:
    with st.expander("⚖️ Impressum"):
        st.markdown("""**Amtsschimmel-Killer**<br><br>**Betreiberin:** Elisabeth Reinecke<br>Ringelsweide 9<br>40223 Düsseldorf<br><br>**Kontakt:**<br>Telefon: +49 211 15821329<br>E-Mail: amtsschimmel-killer@proton.me<br>Web: amtsschimmel-killer.streamlit.app<br><br>**Haftung:**<br>Inhalte nach § 5 TMG. Keine Haftung für KI-generierte Texte.""", unsafe_allow_html=True)
with t2:
    with st.expander("🛡️ Datenschutz"):
        st.markdown("""**Datenschutz:**<br><br>**1. Datenschutz auf einen Blick**<br>Wir behandeln Ihre personenbezogenen Daten vertraulich...<br><br>**2. Datenerfassung & Hosting**<br>Diese App wird auf Streamlit Cloud gehostet...<br><br>**3. Dokumentenverarbeitung**<br>Übertragung an OpenAI (USA)...<br><br>**4. Stripe**<br>Zahlungsabwicklung über Stripe...<br><br>**5. Rechte**<br>Auskunft, Löschung und Sperrung...""", unsafe_allow_html=True)
with t3:
    with st.expander("❓ FAQ"):
        st.markdown("""**FAQ**<br><br>**Abo?** Nein, Einmalzahlung.<br><br>**Sicherheit?** Keine dauerhafte Speicherung.<br><br>**Rechtsberatung?** Nein, nur Formulierungshilfe.""", unsafe_allow_html=True)
with t4:
    with st.expander("📝 Vorlagen"):
        st.markdown("""**Vorlagen:**<br><br>**Fristverlängerung:** [Text...]<br><br>**Widerspruch:** [Text...]<br><br>**Akteneinsicht:** [Text...]""", unsafe_allow_html=True)

st.divider()

# --- 5. HAUPT-LAYOUT ---
col_left, col_mid, col_right = st.columns([1, 1.6, 1.3])

with col_left:
    st.markdown("### 🏛️ Amtsschimmel-Killer")
    st.selectbox("Sprache wählen", ["DE Deutsch", "EN English", "TR Türkçe", "PL Polski", "UA Українська", "RU Русский", "AR العربية", "FR Français", "IT Italiano", "ES Español", "NL Nederlands", "RO Română", "GR Ελληνικά", "CN 中文", "VN Tiếng Việt"], label_visibility="collapsed")
    
    with st.container(border=True):
        st.markdown('<div class="pkg-icon">📄</div>**Analyse (1 Dokument)**<div class="pkg-price">3,99 €</div><div class="pkg-footer">EINMALZAHLUNG</div>', unsafe_allow_html=True)
        st.link_button("Jetzt kaufen", "https://buy.stripe.com", use_container_width=True)

    with st.container(border=True):
        st.markdown('<div style="background-color: #ebf5fb; padding: 10px; border-radius: 10px;"><div class="pkg-icon">🥈</div>**Spar-Paket (3 Dokumente)**<div class="pkg-price">9,99 €</div></div>', unsafe_allow_html=True)
        st.link_button("Jetzt kaufen", "https://buy.stripe.com", use_container_width=True)

    with st.container(border=True):
        st.markdown('<div style="background-color: #fef9e7; padding: 10px; border-radius: 10px;"><div class="pkg-icon">🥇</div>**Sorglos-Paket (10 Dokumente)**<div class="pkg-price">19,99 €</div></div>', unsafe_allow_html=True)
        st.link_button("Jetzt kaufen", "https://buy.stripe.com", use_container_width=True)

with col_mid:
    st.subheader("1. Brief hochladen")
    up_file = st.file_uploader("Datei wählen", type=['pdf', 'png', 'jpg', 'jpeg'], label_visibility="collapsed")
    if up_file:
        if up_file.type.startswith("image"): st.image(up_file, caption="Vorschau", use_container_width=True)
        if st.button("Analyse starten ✨", use_container_width=True):
            with st.spinner("Amtsschimmel wird vertrieben..."):
                txt = perform_ocr_preview(up_file)
                st.session_state['res'] = get_ai_analysis(txt)

with col_right:
    st.subheader("2. Ergebnisse")
    if 'res' in st.session_state:
        r = st.session_state['res']
        st.markdown("### 📅 Frist-Checker")
        erhalt = st.date_input("Wann kam der Brief an?", datetime.now())
        st.info(f"Fristende: **{(erhalt + timedelta(days=30)).strftime('%d.%m.%Y')}**")
        
        t1, t2, t3 = st.tabs(["Analyse", "Antwortbrief", "Widerspruch"])
        with t1: st.write(r['analyse'])
        with t2: st.text_area("Entwurf Antwort:", r['antwort'], height=300)
        with t3: st.text_area("Entwurf Widerspruch:", r['widerspruch'], height=300)
        
        st.divider()
        st.download_button("📥 Excel Download", create_excel_pro(r['analyse'], r['antwort'], r['widerspruch']), "Analyse.xlsx", use_container_width=True)
        st.download_button("📥 Word Dokument", create_word_complete(r['analyse'], r['antwort'], r['widerspruch']), "Analyse.docx", use_container_width=True)
    else:
        st.info("Bitte Dokument hochladen und Analyse starten.")
