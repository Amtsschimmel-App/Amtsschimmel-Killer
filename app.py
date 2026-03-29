import streamlit as st
from openai import OpenAI
import pytesseract
from PIL import Image
import pdfplumber
from pdf2image import convert_from_bytes
from docx import Document
import io
import pandas as pd
import re
from fpdf import FPDF 
from datetime import datetime
import os

# ==========================================
# 1. KONFIGURATION & TEXTE (FEST VERANKERT)
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
Web: amtsschimmel-killer.streamlit.app  

**Haftung:**  
Inhalte nach § 5 TMG. Keine Haftung für KI-generierte Texte.
"""

DATENSCHUTZ_TEXT = """
**1. Datenschutz auf einen Blick**  
Wir behandeln Ihre personenbezogenen Daten vertraulich und entsprechend der gesetzlichen Vorschriften (DSGVO).

**2. Datenerfassung & Hosting**  
Diese App wird auf Streamlit Cloud gehostet. Beim Besuch werden Logfiles (IP-Adresse, Browser) automatisch vom Hoster erfasst. Wir nutzen diese Daten nicht.

**3. Dokumentenverarbeitung**  
Ihre hochgeladenen Briefe werden per TLS-verschlüsselter Schnittstelle an OpenAI (USA) zur Analyse übertragen. Wir speichern keine Briefe auf unseren Servern. Die Verarbeitung dient rein dem Zweck, Ihnen einen Antwortentwurf zu erstellen.

**4. Zahlungsabwicklung (Stripe)**  
Bei Käufen werden Sie zu Stripe weitergeleitet. Stripe erhebt die erforderlichen Daten zur Abrechnung. Wir erhalten lediglich eine Bestätigung über die erfolgreiche Zahlung.

**5. Ihre Rechte**  
Sie haben das Recht auf Auskunft, Löschung und Sperrung Ihrer Daten. Kontaktieren Sie uns unter amtsschimmel-killer@proton.me.
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
# 2. LOGIK & STRIPE (FESTE LINKS)
# ==========================================
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

if "credits" not in st.session_state: st.session_state.credits = 0
if "full_res" not in st.session_state: st.session_state.full_res = ""
if "processed_sessions" not in st.session_state: st.session_state.processed_sessions = []

# DEINE STRIPE CODES
STRIPE_BASIS = "https://buy.stripe.com/eVqcN53Pd5YLgo8alq1gs02"    # 3,99€
STRIPE_SPAR = "https://buy.stripe.com/8x228retRbj50paalq1gs03"     # 9,99€
STRIPE_PREMIUM = "https://buy.stripe.com/28EcN50D1bj52xi8di1gs04"  # 19,99€

# ==========================================
# 3. FUNKTIONEN (OCR & EXPORT)
# ==========================================
def extract_text(file):
    text = ""
    if file.type == "application/pdf":
        with pdfplumber.open(file) as pdf:
            for page in pdf.pages:
                content = page.extract_text()
                if content: text += content + "\n"
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
    df = pd.DataFrame({"Kategorie": ["Fristen", "Zusammenfassung"], "Inhalt": [", ".join(dates) if dates else "Keine", text[:800]]})
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
# 4. LAYOUT OBEN (LOGO, FAQ, VORLAGEN)
# ==========================================
if os.path.exists(LOGO_DATEI):
    st.image(LOGO_DATEI, width=280)

st.title("Amtsschimmel-Killer 🪓")

c1, c2 = st.columns(2)
with c1:
    with st.expander("❓ FAQ", expanded=True): st.markdown(FAQ_TEXT)
with c2:
    with st.expander("📝 Vorlagen", expanded=True): st.markdown(VORLAGEN_TEXT)

st.divider()

# ==========================================
# 5. HAUPTBEREICH (LINKS: VORSCHAU | RECHTS: ANALYSE)
# ==========================================
col_links, col_rechts = st.columns([1, 1.2])

with col_links:
    st.subheader("1. Paket & Dokument")
    s1, s2, s3 = st.columns(3)
    with s1: st.link_button("1 Paket\n3,99€", STRIPE_BASIS)
    with s2: st.link_button("2 Paket\n9,99€", STRIPE_SPAR)
    with s3: st.link_button("3 Paket\n19,99€", STRIPE_PREMIUM)
    
    st.info(f"Guthaben: **{st.session_state.credits} Scans**")
    
    upped = st.file_uploader("Brief (Foto oder PDF) wählen", type=["pdf", "jpg", "png"])
    
    if upped:
        if upped.type != "application/pdf":
            st.image(upped, caption="Vorschau des Uploads", use_container_width=True)
        else:
            st.success(f"📄 PDF geladen: {upped.name}")

        if st.session_state.credits > 0:
            if st.button("🚀 JETZT ANALYSIEREN"):
                with st.spinner("Amtsschimmel wird verjagt..."):
                    raw = extract_text(upped)
                    response = client.chat.completions.create(
                        model="gpt-4o",
                        messages=[{"role": "system", "content": "Analysiere strikt: 🚦 WICHTIGKEIT, 📖 ZUSAMMENFASSUNG, 📅 FRISTEN, ✍️ ANTWORT-ENTWURF."},
                                  {"role": "user", "content": raw}]
                    )
                    st.session_state.full_res = response.choices.message.content
                    st.session_state.credits -= 1
                    st.rerun()

with col_rechts:
    st.subheader("2. Analyse-Boxen")
    if st.session_state.full_res:
        res = st.session_state.full_res
        st.info(f"### 🚦 Wichtigkeit\n{re.search(r'🚦(.*?)(?=📖|📅|✍️|$)', res, re.S).group(1) if '🚦' in res else 'Siehe Text'}")
        st.write(f"### 📖 Zusammenfassung\n{re.search(r'📖(.*?)(?=📅|✍️|$)', res, re.S).group(1) if '📖' in res else 'Siehe Text'}")
        st.warning(f"### 📅 Fristen\n{re.search(r'📅(.*?)(?=✍️|$)', res, re.S).group(1) if '📅' in res else 'Keine Fristen erkannt'}")
        st.success(f"### ✍️ Antwort-Entwurf\n{re.search(r'✍️(.*)', res, re.S).group(1) if '✍️' in res else 'Entwurf im Text'}")
    else:
        st.info("Hier erscheinen die Daten nach der Analyse.")

# ==========================================
# 6. DOWNLOADS GANZ UNTEN (KOMPLETT)
# ==========================================
if st.session_state.full_res:
    st.divider()
    st.subheader("3. Alle Dokumente herunterladen")
    d1, d2, d3, d4 = st.columns(4)
    with d1: st.download_button("📄 PDF Export", create_pdf(st.session_state.full_res), "Analyse.pdf")
    with d2: st.download_button("📝 Word Export", create_docx(st.session_state.full_res), "Analyse.docx")
    with d3: st.download_button("📊 Excel Liste", create_excel(st.session_state.full_res), "Fristen.xlsx")
    with d4: st.download_button("📅 Kalender", b"BEGIN:VCALENDAR\nEND:VCALENDAR", "Termin.ics")

with st.sidebar:
    with st.expander("⚖️ Impressum"): st.markdown(IMPRESSUM_TEXT)
    with st.expander("🛡️ Datenschutz"): st.markdown(DATENSCHUTZ_TEXT)
