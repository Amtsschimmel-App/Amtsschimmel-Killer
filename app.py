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
# 1. SETUP & DESIGN (STRENG FIXIERT)
# ==========================================
st.set_page_config(page_title="Amtsschimmel-Killer", page_icon="📄", layout="wide")

st.markdown("""
    <style>
        .block-container { padding-top: 1rem; }
        .paket-box { border: 2px solid #0d47a1; padding: 12px; border-radius: 10px; background-color: #f0f7ff; margin-bottom: 5px; text-align: center; }
        .stDownloadButton button { width: 100% !important; background-color: #e1f5fe; border: 1px solid #01579b; font-weight: bold; }
        .stLinkButton a { width: 100% !important; background-color: #0d47a1 !important; color: white !important; font-weight: bold; padding: 10px; border-radius: 5px; text-decoration: none; display: inline-block; }
        .stExpander div { line-height: 1.6 !important; }
    </style>
    """, unsafe_allow_html=True)

LOGO_DATEI = "icon_final_blau.png"
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# ==========================================
# 2. ADMIN & SESSION STATE (999 SCANS)
# ==========================================
if "credits" not in st.session_state: st.session_state.credits = 0
if "full_res" not in st.session_state: st.session_state.full_res = ""

if st.query_params.get("admin") == "GeheimAmt2024!":
    st.session_state.credits = 999

# ==========================================
# 3. OBERE ZEILE: RECHTSTEXTE (DEINE TEXTE)
# ==========================================
st.title("Amtsschimmel-Killer 🪓")

t1, t2, t3, t4 = st.columns(4)

with t1:
    with st.expander("⚖️ Impressum", expanded=True):
        st.write("""
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
        """)

with t2:
    with st.expander("🛡️ Datenschutz", expanded=True):
        st.write("""
        **1. Datenschutz auf einen Blick**  
        Wir behandeln Ihre personenbezogenen Daten vertraulich und entsprechend der gesetzlichen Vorschriften (DSGVO).

        **2. Datenerfassung & Hosting**  
        Diese App wird auf Streamlit Cloud gehostet. Beim Besuch werden Logfiles automatisch vom Hoster erfasst. Wir nutzen diese Daten nicht.

        **3. Dokumentenverarbeitung**  
        Ihre hochgeladenen Briefe werden per TLS an OpenAI übertragen. Wir speichern keine Briefe auf unseren Servern.

        **4. Zahlungsabwicklung (Stripe)**  
        Bei Käufen werden Sie zu Stripe weitergeleitet. Wir erhalten lediglich eine Bestätigung über die erfolgreiche Zahlung.

        **5. Ihre Rechte**  
        Sie haben das Recht auf Auskunft, Löschung und Sperrung Ihrer Daten.
        """)

with t3:
    with st.expander("❓ FAQ", expanded=True):
        st.write("""
        **Ist das ein Abonnement?**  
        Nein. Wir hassen Abos genauso wie Amtsschimmel. Jede Zahlung ist eine Einmalzahlung für eine feste Anzahl an Scans. Es gibt keine automatische Verlängerung.

        **Wie sicher sind meine Dokumente?**  
        Ihre Dokumente werden verschlüsselt an die KI (OpenAI) übertragen und niemals dauerhaft auf unseren Servern gespeichert. Nach der Analyse werden die Daten gelöscht.

        **Ersetzt die App eine Rechtsberatung?**  
        Nein. Wir bieten eine Formulierungshilfe. Für verbindliche Rechtsberatung wenden Sie sich bitte an einen Rechtsanwalt.

        **Was passiert, wenn der Scan fehlschlägt?**  
        Sollte ein Upload technisch scheitern, wird kein Guthaben abgezogen.
        """)

with t4:
    with st.expander("📝 Vorlagen", expanded=True):
        st.write("""
        **Fristverlängerung:**  
        In der Angelegenheit [Aktenzeichen] bitte ich um Verlängerung der Frist bis zum [Datum], da mir noch notwendige Unterlagen fehlen.

        **Widerspruch einlegen:**  
        Gegen Ihren Bescheid vom [Datum], erhalten am [Datum], lege ich hiermit Widerspruch ein. Eine detaillierte Begründung folgt separat.

        **Akteneinsicht einfordern:**  
        Zur Prüfung des Sachverhalts [Aktenzeichen] beantrage ich hiermit gemäß § 25 SGB X bzw. § 29 VwVfG Akteneinsicht.
        """)

st.divider()

# ==========================================
# 4. HILFSFUNKTIONEN (OCR & EXPORT INKL. ICS)
# ==========================================
def extract_text(file):
    text = ""
    if file.type == "application/pdf":
        with pdfplumber.open(file) as pdf:
            for page in pdf.pages: text += (page.extract_text() or "") + "\n"
        if not text.strip():
            images = convert_from_bytes(file.read())
            for img in images: text += pytesseract.image_to_string(img, lang='deu') + "\n"
    else:
        text = pytesseract.image_to_string(Image.open(file), lang='deu')
    return text

def create_pdf(text):
    pdf = FPDF(); pdf.add_page(); pdf.set_font("Arial", size=10)
    pdf.multi_cell(0, 10, text.encode('latin-1', 'replace').decode('latin-1'))
    return pdf.output(dest='S').encode('latin-1')

def create_ics(text):
    # Sucht das erste Datum im Format TT.MM.JJJJ
    dates = re.findall(r'(\d{2})\.(\d{2})\.(\d{4})', text)
    if dates:
        d, m, y = dates[0]
        date_str = f"{y}{m}{d}"
    else:
        date_str = datetime.now().strftime("%Y%m%d")
    ics = f"BEGIN:VCALENDAR\nVERSION:2.0\nBEGIN:VEVENT\nSUMMARY:Amtsschimmel Frist\nDTSTART;VALUE=DATE:{date_str}\nDTEND;VALUE=DATE:{date_str}\nDESCRIPTION:Analyse-Frist aus Amtsschimmel-Killer\nEND:VEVENT\nEND:VCALENDAR"
    return ics.encode('utf-8')

# ==========================================
# 5. HAUPTBEREICH (PAKETE & APP)
# ==========================================
main_l, main_r = st.columns([1, 2.2])

with main_l:
    st.subheader("🌐 Sprachen")
    st.selectbox("Übersetzung wählen:", ["Deutsch", "English", "Türkçe", "Polski", "Русский", "العربية", "Español", "Français", "Italiano", "Română"], label_visibility="collapsed")
    
    if os.path.exists(LOGO_DATEI):
        st.image(LOGO_DATEI, width=200)
    
    st.subheader("💰 Scans kaufen")
    st.markdown('<div class="paket-box"><b>📦 1. Paket</b><br>1 Scan für 3,99€<br><small>Einmalzahlung - Kein Abo</small></div>', unsafe_allow_html=True)
    st.link_button("Jetzt kaufen", "https://buy.stripe.com")
    st.markdown('<div class="paket-box"><b>📦 2. Paket</b><br>3 Scans für 9,99€<br><small>Einmalzahlung - Kein Abo</small></div>', unsafe_allow_html=True)
    st.link_button("Jetzt kaufen", "https://buy.stripe.com")
    st.markdown('<div class="paket-box"><b>📦 3. Paket</b><br>10 Scans für 19,99€<br><small>Einmalzahlung - Kein Abo</small></div>', unsafe_allow_html=True)
    st.link_button("Jetzt kaufen", "https://buy.stripe.com")

with main_r:
    st.subheader("📄 Analyse-Zentrum")
    st.info(f"Guthaben: **{st.session_state.credits} Scans**")
    upped = st.file_uploader("Brief hochladen", type=["pdf", "jpg", "png", "jpeg"], label_visibility="collapsed")
    
    if upped and st.session_state.credits > 0:
        if st.button("🚀 JETZT ANALYSIEREN"):
            with st.spinner("Amtsschimmel wird verjagt..."):
                raw = extract_text(upped)
                resp = client.chat.completions.create(
                    model="gpt-4o",
                    messages=[{"role": "system", "content": "Analysiere präzise: 🚦 WICHTIGKEIT, 📖 ZUSAMMENFASSUNG, 📅 FRISTEN, ✍️ ANTWORT-ENTWURF."},
                              {"role": "user", "content": raw}]
                )
                st.session_state.full_res = resp.choices.message.content
                st.session_state.credits -= 1
                st.rerun()

    if st.session_state.full_res:
        res = st.session_state.full_res
        st.divider()
        b1, b2 = st.columns(2); b1.info(f"### 🚦 Wichtigkeit\n{re.search(r'🚦(.*?)(?=📖|$)', res, re.S).group(1) if '🚦' in res else 'Prüfen'}"); b2.write(f"### 📖 Zusammenfassung\n{re.search(r'📖(.*?)(?=📅|$)', res, re.S).group(1) if '📖' in res else '...'}")
        b3, b4 = st.columns(2); b3.warning(f"### 📅 Fristen\n{re.search(r'📅(.*?)(?=✍️|$)', res, re.S).group(1) if '📅' in res else 'Keine'}"); b4.success(f"### ✍️ Antwort-Entwurf\n{re.search(r'✍️(.*)', res, re.S).group(1) if '✍️' in res else '...'}")
        
        st.divider(); st.subheader("📥 Downloads")
        d1, d2, d3, d4 = st.columns(4)
        with d1: st.download_button("📄 PDF", create_pdf(res), "Analyse.pdf")
        with d2: st.download_button("📝 Word", create_pdf(res), "Analyse.docx")
        with d3:
            dates = re.findall(r'(\d{2}\.\d{2}\.\d{4})', res)
            df = pd.DataFrame({"Termine": dates if dates else ["Keine"], "Analyse": [res]})
            out = io.BytesIO(); 
            with pd.ExcelWriter(out, engine='xlsxwriter') as wr: df.to_excel(wr, index=False)
            st.download_button("📊 Excel", out.getvalue(), "Fristen.xlsx")
        with d4: st.download_button("📅 Kalender", create_ics(res), "Frist.ics")
