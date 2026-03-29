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
        .stDownloadButton { width: 100%; }
    </style>
    """, unsafe_allow_html=True)

LOGO_DATEI = "icon_final_blau.png"

# ==========================================
# 2. RECHTSTEXTE (EXAKT DEINE VORGABE)
# ==========================================
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
**Datenschutz:**

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
**FAQ**

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
**Vorlagen:**

**Fristverlängerung:**  
Sehr geehrte Damen und Herren, in der Angelegenheit [Aktenzeichen] bitte ich um Verlängerung der gesetzten Frist bis zum [Datum], da mir noch notwendige Unterlagen fehlen. Mit freundlichen Grüßen, [Name]

**Widerspruch einlegen (Fristwahrend):**  
Sehr geehrte Damen und Herren, gegen Ihren Bescheid vom [Datum], erhalten am [Datum], lege ich hiermit Widerspruch ein. Eine detaillierte Begründung folgt in einem separaten Schreiben. Mit freundlichen Grüßen, [Name]

**Akteneinsicht einfordern:**  
Sehr geehrte Damen und Herren, zur Prüfung des Sachverhalts [Aktenzeichen] beantrage ich hiermit gemäß § 25 SGB X bzw. § 29 VwVfG Akteneinsicht. Mit freundlichen Grüßen, [Name]
"""

# ==========================================
# 3. SESSION STATE & STRIPE LINKS (FEST)
# ==========================================
if "credits" not in st.session_state: st.session_state.credits = 0
if "full_res" not in st.session_state: st.session_state.full_res = ""
if "processed_sessions" not in st.session_state: st.session_state.processed_sessions = []

# DIE FIXIERTEN STRIPE LINKS
STRIPE_BASIS = "https://buy.stripe.com/eVqcN53Pd5YLgo8alq1gs02"
STRIPE_SPAR = "https://buy.stripe.com/8x228retRbj50paalq1gs03"
STRIPE_PREMIUM = "https://buy.stripe.com/28EcN50D1bj52xi8di1gs04"

# Admin Logik (999 Scans)
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
# 4. EXPORT LOGIK (ABSTURZSICHER)
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
    return pdf.output(dest='S') # Gibt Bytes direkt zurück

def create_docx(text):
    doc = Document()
    doc.add_heading('Analyse-Ergebnis', 0)
    doc.add_paragraph(text.replace("#", "").replace("*", ""))
    bio = io.BytesIO()
    doc.save(bio)
    return bio.getvalue()

def create_excel(text):
    dates = re.findall(r'(\d{2}\.\d{2}\.\d{4})', text)
    df = pd.DataFrame({"Frist/Datum": dates if dates else ["Kein Datum"], "Info": ["Aus Analyse" for _ in range(max(1, len(dates)))]})
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
# 5. KI-LOGIK
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
    return resp.choices[0].message.content # Korrektur für OpenAI v1+

# ==========================================
# 6. UI - OBERE INFO-LEISTE (FIXIERT)
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
# 7. SIDEBAR - SHOP (AUFGEMOTZT & FEST)
# ==========================================
with st.sidebar:
    if os.path.exists(LOGO_DATEI): st.image(LOGO_DATEI, use_container_width=True)
    
    st.subheader("🌍 1. Sprache wählen")
    lang_choice = st.selectbox("Ausgabe:", ["🇩🇪 Deutsch", "🇺🇸 English", "🇹🇷 Türkçe", "🇵🇱 Polski", "🇷🇺 Русский"], label_visibility="collapsed")
    
    st.divider()
    st.subheader("🛒 2. Scans kaufen")
    st.metric("Guthaben", f"{st.session_state.credits} Scans")

    # BASIS BOX
    st.markdown('<div style="background-color:#ffffff; padding:15px; border-radius:10px; border:2px solid #f0f2f6; margin-bottom:5px;">'
                '<h4 style="margin:0; color:#1f77b4;">☕ BASIS</h4>'
                '<p style="margin:5px 0; font-size:1.1em;"><b>3,99 €</b> / 1 Scan</p>'
                '<p style="font-size:0.85em; color:#28a745;"><b>✓ EINMALZAHLUNG</b><br>✓ KEIN ABO</p></div>', unsafe_allow_html=True)
    st.link_button("Basis kaufen", STRIPE_BASIS, use_container_width=True)

    # SPAR BOX
    st.markdown('<div style="background-color:#e3f2fd; padding:15px; border-radius:10px; border:2px solid #2196f3; margin-top:15px; margin-bottom:5px;">'
                '<h4 style="margin:0; color:#0d47a1;">📦 SPAR-PAKET</h4>'
                '<p style="margin:5px 0; font-size:1.1em;"><b>9,99 €</b> / 5 Scans</p>'
                '<p style="font-size:0.85em; color:#28a745;"><b>✓ EINMALZAHLUNG</b><br>✓ KEIN ABO</p></div>', unsafe_allow_html=True)
    st.link_button("Spar-Paket kaufen", STRIPE_SPAR, use_container_width=True)

    # PREMIUM BOX
    st.markdown('<div style="background-color:#e8f5e9; padding:15px; border-radius:10px; border:2px solid #4caf50; margin-top:15px; margin-bottom:5px;">'
                '<h4 style="margin:0; color:#1b5e20;">🚀 PREMIUM</h4>'
                '<p style="margin:5px 0; font-size:1.1em;"><b>19,99 €</b> / 10 Scans</p>'
                '<p style="font-size:0.85em; color:#28a745;"><b>✓ EINMALZAHLUNG</b><br>✓ KEIN ABO</p></div>', unsafe_allow_html=True)
    st.link_button("Premium kaufen", STRIPE_PREMIUM, use_container_width=True)

# ==========================================
# 8. HAUPTBEREICH (VORSCHAU LINKS | ANALYSE RECHTS)
# ==========================================
st.title("📄 Amtsschimmel-Killer")

col_left, col_right = st.columns(2)

with col_left:
    st.subheader("1. Dokument & Vorschau")
    u_file = st.file_uploader("Brief fotografieren oder PDF hochladen", type=['png', 'jpg', 'jpeg', 'pdf'])
    
    if u_file:
        if u_file.type != "application/pdf":
            st.image(u_file, caption="Dokument Vorschau", use_container_width=True)
        else:
            st.info("📄 PDF erfolgreich geladen.")
    
    mode = st.radio("Was soll erstellt werden?", ["Antwortbrief 📝", "Widerspruch 🛑"], horizontal=True)
    
    if u_file and st.button("🚀 Jetzt analysieren (-1 Scan)"):
        if st.session_state.credits > 0:
            with st.spinner("KI übersetzt Amtsschimmel-Deutsch..."):
                raw = get_text(u_file)
                st.session_state.full_res = run_ai(raw, lang_choice, "W" if "Widerspruch" in mode else "A")
                st.session_state.credits -= 1
                st.rerun()
        else:
            st.error("Guthaben leer! Bitte links wählen.")

with col_right:
    st.subheader("2. Analyse & Export")
    if st.session_state.full_res:
        st.markdown(st.session_state.full_res)
        st.divider()
        st.write("📥 **Export:**")
        ex1, ex2, ex3, ex4 = st.columns(4)
        with ex1: st.download_button("📄 PDF", create_pdf(st.session_state.full_res), "Analyse.pdf", mime="application/pdf")
        with ex2: st.download_button("📝 Word", create_docx(st.session_state.full_res), "Analyse.docx", mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document")
        with ex3: st.download_button("📊 Excel", create_excel(st.session_state.full_res), "Fristen.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        with ex4: st.download_button("📅 Kalender", create_ics(st.session_state.full_res), "Termine.ics", mime="text/calendar")
    else:
        st.info("Hier erscheint das Ergebnis nach dem Scan.")
