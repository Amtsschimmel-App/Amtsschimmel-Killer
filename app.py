import streamlit as st
import pandas as pd
from io import BytesIO
from docx import Document
from fpdf import FPDF
import pytesseract
from PIL import Image
from pdf2image import convert_from_bytes
import openai
import os

# --- 1. SEITEN-KONFIGURATION ---
st.set_page_config(page_title="Amtsschimmel-Killer", layout="wide", page_icon="🏛️")

# OpenAI API Key (Sicher über Streamlit Secrets)
if "OPENAI_API_KEY" in st.secrets:
    openai.api_key = st.secrets["OPENAI_API_KEY"]
else:
    st.error("OpenAI API Key fehlt in den Secrets!")

# --- 2. CUSTOM CSS ---
st.markdown("""
    <style>
    .pkg-icon { font-size: 2rem; margin-bottom: 0.5rem; }
    .pkg-price { font-size: 1.5rem; font-weight: bold; color: #1E3A8A; margin: 0.5rem 0; }
    .pkg-footer { font-size: 0.8rem; color: gray; margin-bottom: 1rem; }
    .legal-text { white-space: pre-wrap; font-family: sans-serif; line-height: 1.6; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. KI & EXPORT FUNKTIONEN ---

def get_ai_analysis(text):
    """Schnittstelle zu OpenAI für Analyse, Antwort und Widerspruch."""
    try:
        response = openai.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "Du bist ein Experte für deutsches Verwaltungsrecht. Analysiere den Text, erkenne Fristen und erstelle ein Antwortschreiben sowie einen Widerspruch. Antworte in JSON mit den Feldern: analyse, antwort, widerspruch, frist."},
                {"role": "user", "content": f"Hier ist der Text des Behördenbriefs:\n\n{text}"}
            ],
            response_format={ "type": "json_object" }
        )
        import json
        return json.loads(response.choices[0].message.content)
    except Exception as e:
        return {"analyse": f"Fehler: {str(e)}", "antwort": "KI-Fehler", "widerspruch": "KI-Fehler", "frist": "Unbekannt"}

def create_pdf_adobe_ready(analyse, antwort, widerspruch):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.set_font("helvetica", 'B', 16)
    pdf.cell(0, 10, "Amtsschimmel-Killer Analyse-Report", ln=True, align='C')
    sections = [("1. Juristische Analyse", analyse), ("2. Antwortschreiben-Entwurf", antwort), ("3. Widerspruchs-Entwurf", widerspruch)]
    for title, content in sections:
        pdf.ln(10)
        pdf.set_font("helvetica", 'B', 14)
        pdf.cell(0, 10, title, ln=True)
        pdf.set_font("helvetica", '', 11)
        safe_text = content.replace('•', '-').replace('–', '-').replace('„', '"').replace('“', '"').replace('”', '"').replace('’', "'")
        pdf.multi_cell(0, 6, safe_text.encode('latin-1', 'replace').decode('latin-1'))
    return bytes(pdf.output())

def create_word_complete(analyse, antwort, widerspruch):
    doc = Document()
    doc.add_heading('Amtsschimmel-Killer: Ihr Report', 0)
    for title, content in [("Analyse", analyse), ("Antwortschreiben", antwort), ("Widerspruch", widerspruch)]:
        doc.add_heading(title, level=1)
        doc.add_paragraph(content)
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
    except: return "Fehler bei der Texterkennung."

# --- 4. TOP-BAR: RECHTLICHES ---
t1, t2, t3, t4 = st.columns(4)
with t1:
    with st.expander("⚖️ Impressum"):
        st.markdown("""Amtsschimmel-Killer  
Betreiberin: Elisabeth Reinecke  
Ringelsweide 9  
40223 Düsseldorf  

Kontakt:  
Telefon: +49 211 15821329  
E-Mail: amtsschimmel-killer@proton.me  
Web: amtsschimmel-killer.streamlit.app  

Haftung:  
Inhalte nach § 5 TMG. Keine Haftung für KI-generierte Texte.""")

with t2:
    with st.expander("🛡️ Datenschutz"):
        st.markdown("""1. Datenschutz auf einen Blick  
Wir behandeln Ihre personenbezogenen Daten vertraulich und entsprechend der gesetzlichen Vorschriften (DSGVO).  

2. Datenerfassung & Hosting  
Diese App wird auf Streamlit Cloud gehostet. Beim Besuch werden Logfiles (IP-Adresse, Browser) automatisch vom Hoster erfasst. Wir nutzen diese Daten nicht.  

3. Dokumentenverarbeitung  
Ihre hochgeladenen Briefe werden per TLS-verschlüsselter Schnittstelle an OpenAI (USA) zur Analyse übertragen. Wir speichern keine Briefe auf unseren Servern.  

4. Zahlungsabwicklung (Stripe)  
Bei Käufen werden Sie zu Stripe weitergeleitet. Wir erhalten lediglich eine Bestätigung über die erfolgreiche Zahlung.  

5. Ihre Rechte  
Sie haben das Recht auf Auskunft, Löschung und Sperrung Ihrer Daten. Kontaktieren Sie uns unter amtsschimmel-killer@proton.me.""")

with t3:
    with st.expander("❓ FAQ"):
        st.markdown("""Ist das ein Abonnement?  
Nein. Wir hassen Abos genauso wie Amtsschimmel. Jede Zahlung ist eine Einmalzahlung für eine feste Anzahl an Scans.  

Wie sicher sind meine Dokumente?  
Ihre Dokumente werden verschlüsselt an die KI (OpenAI) übertragen und niemals dauerhaft auf unseren Servern gespeichert.  

Ersetzt die App eine Rechtsberatung?  
Nein. Wir bieten eine Formulierungshilfe und Unterstützung beim Textverständnis.  

Was passiert, wenn der Scan fehlschlägt?  
Ein Scan wird erst berechnet, wenn die KI den Text erfolgreich verarbeitet hat.  

Wie erreiche ich Elisabeth Reinecke?  
Nutzen Sie einfach die E-Mail amtsschimmel-killer@proton.me oder die Telefonnummer im Impressum.""")

with t4:
    with st.expander("📝 Vorlagen"):
        st.markdown("""Fristverlängerung:  
Sehr geehrte Damen und Herren, in der Angelegenheit [Aktenzeichen] bitte ich um Verlängerung der gesetzten Frist bis zum [Datum], da mir noch notwendige Unterlagen fehlen.  

Widerspruch einlegen (Fristwahrend):  
Sehr geehrte Damen und Herren, gegen Ihren Bescheid vom [Datum], erhalten am [Datum], lege ich hiermit Widerspruch ein.  

Akteneinsicht einfordern:  
Sehr geehrte Damen und Herren, zur Prüfung des Sachverhalts [Aktenzeichen] beantrage ich hiermit gemäß § 25 SGB X Akteneinsicht.""")

st.divider()

# --- 5. HAUPT-LAYOUT ---
col_left, col_mid, col_right = st.columns([1, 1.6, 1.3])

with col_left:
    st.markdown("### 🏛️ Amtsschimmel-Killer")
    st.selectbox("Sprache", ["DE Deutsch", "EN English", "TR Türkçe", "PL Polski", "UA Українська", "RU Русский", "AR العربية", "FR Français", "IT Italiano", "ES Español", "NL Nederlands", "RO Română", "GR Ελληνικά", "CN 中文", "VN Tiếng Việt"], label_visibility="collapsed")
    st.write("")
    st.link_button("📄 Analyse (3,99 €)", "https://buy.stripe.com/eVqcN53Pd5YLgo8alq1gs02")
    st.link_button("🥈 Spar-Paket (9,99 €)", "https://buy.stripe.com/8x228retRbj50paalq1gs03")
    st.link_button("🥇 Sorglos (19,99 €)", "https://buy.stripe.com/28EcN50D1bj52xi8di1gs04")

with col_mid:
    st.markdown("### 📑 Upload & Vorschau")
    st.success("👑 Admin Guthaben: 999 Dokumente")
    uploaded_file = st.file_uploader("Datei hier reinziehen", type=["pdf", "jpg", "png", "jpeg"], label_visibility="collapsed")
    if uploaded_file:
        with st.spinner("Lese Dokument..."):
            raw_text = perform_ocr_preview(uploaded_file)
        st.text_area("Erkannter Inhalt:", raw_text, height=450)

with col_right:
    st.markdown("### 🔍 Analyse & Antwort")
    if uploaded_file:
        with st.spinner("KI analysiert..."):
            res = get_ai_analysis(raw_text)
        
        st.error(f"📅 FRIST ERKANNT: {res.get('frist', 'Nicht gefunden')}")
        st.info(res['analyse'])
        
        tabs = st.tabs(["✍️ Antwort", "⚖️ Widerspruch", "📥 Downloads"])
        with tabs[0]: st.text_area("Entwurf Antwort:", res['antwort'], height=300)
        with tabs[1]: st.text_area("Entwurf Widerspruch:", res['widerspruch'], height=300)
        with tabs[2]:
            st.download_button("📊 Excel-Bericht", create_excel_pro(res['analyse'], res['antwort'], res['widerspruch']), "Analyse.xlsx")
            st.download_button("📝 Word (Komplett)", create_word_complete(res['analyse'], res['antwort'], res['widerspruch']), "Bericht.docx")
            pdf_bytes = create_pdf_adobe_ready(res['analyse'], res['antwort'], res['widerspruch'])
            st.download_button("📕 PDF (Adobe Ready)", pdf_bytes, "Bericht.pdf", mime="application/pdf")
