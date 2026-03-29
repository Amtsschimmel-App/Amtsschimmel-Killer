import streamlit as st
from openai import OpenAI
import pytesseract
from PIL import Image
import pdfplumber
from pdf2image import convert_from_bytes
import io
import os
from fpdf import FPDF 
from datetime import datetime

# ==========================================
# 1. SETUP & ABSOLUTE ZAHLUNGSSICHERHEIT
# ==========================================
st.set_page_config(page_title="Amtsschimmel-Killer", page_icon="📄", layout="wide")

if "credits" not in st.session_state:
    st.session_state.credits = 0
if "full_res" not in st.session_state:
    st.session_state.full_res = None
if "processed_sessions" not in st.session_state:
    st.session_state.processed_sessions = set()

# GUTHABEN-LOGIK (Stripe Return Check)
params = st.query_params
sid = params.get("session_id", "")
if "pack" in params and sid not in st.session_state.processed_sessions:
    val = params["pack"]
    if val == "1": st.session_state.credits += 1
    elif val == "2": st.session_state.credits += 3
    elif val == "3": st.session_state.credits += 10
    if sid: st.session_state.processed_sessions.add(sid)
    st.toast("✅ Zahlung erfolgreich verbucht!", icon="💰")

# SADMIN MODUS (999 Dokumente)
if params.get("admin") == "GeheimAmt2024!":
    st.session_state.credits = 999

# ==========================================
# 2. STRIPE LINKS (FIXIERT) & DESIGN
# ==========================================
STRIPE_1 = "https://buy.stripe.com/eVqcN53Pd5YLgo8alq1gs02"
STRIPE_2 = "https://buy.stripe.com/8x228retRbj50paalq1gs03"
STRIPE_3 = "https://buy.stripe.com/28EcN50D1bj52xi8di1gs04"

st.markdown("""
    <style>
        .block-container { padding-top: 1rem; }
        .paket-card {
            border: 1px solid #0d47a1; padding: 10px; border-radius: 10px;
            background-color: #f8fbff; margin-bottom: 5px; text-align: center;
        }
        .price-tag { font-size: 15px; font-weight: bold; color: #0d47a1; margin: 2px; }
        .no-abo-text { font-size: 10px; color: #d32f2f; font-weight: bold; text-transform: uppercase; }
        .stLinkButton a {
            width: 100% !important; background-color: #0d47a1 !important;
            color: white !important; border-radius: 6px !important;
            font-weight: bold !important; padding: 8px !important;
            font-size: 13px !important; text-decoration: none;
            display: inline-block; text-align: center;
        }
        .stExpander div { line-height: 1.4 !important; white-space: pre-wrap !important; font-size: 12px; }
        .result-box { 
            background-color: #ffffff; padding: 15px; border-radius: 10px; 
            border-left: 5px solid #0d47a1; margin-bottom: 15px; 
            box-shadow: 2px 2px 8px rgba(0,0,0,0.1); 
        }
        .box-title { font-weight: bold; color: #0d47a1; margin-bottom: 5px; text-transform: uppercase; font-size: 13px; border-bottom: 1px solid #eee; padding-bottom: 3px; }
    </style>
    """, unsafe_allow_html=True)

LOGO_DATEI = "icon_final_blau.png"
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# PDF GENERIERUNG FIX (Bytes Rückgabe ohne .encode Fehler)
def generate_pdf(data_dict):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, "Amtsschimmel-Killer Analyse", ln=True, align='C')
    pdf.ln(10)
    for title, content in data_dict.items():
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(0, 10, title.upper(), ln=True)
        pdf.set_font("Arial", size=11)
        # Fix für Latin-1 Encoding
        txt_safe = str(content).encode('latin-1', 'replace').decode('latin-1')
        pdf.multi_cell(0, 7, txt=txt_safe)
        pdf.ln(5)
    return pdf.output(dest='S')

# ==========================================
# 3. OBERE ZEILE: EINGEKLAPPTE INFOS (WORTWÖRTLICH)
# ==========================================
st.title("Amtsschimmel-Killer 🪓")

t1, t2, t3, t4 = st.columns(4)
with t1:
    with st.expander("⚖️ Impressum", expanded=False):
        st.write("""Amtsschimmel-Killer
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
    with st.expander("🛡️ Datenschutz", expanded=False):
        st.write("""1. Datenschutz auf einen Blick
Wir behandeln Ihre personenbezogenen Daten vertraulich und entsprechend der gesetzlichen Vorschriften (DSGVO).

2. Datenerfassung & Hosting
Diese App wird auf Streamlit Cloud gehostet. Beim Besuch werden Logfiles automatisch vom Hoster erfasst. Wir nutzen diese Daten nicht.

3. Dokumentenverarbeitung
Ihre hochgeladenen Briefe werden per TLS-verschlüsselter Schnittstelle an OpenAI (USA) zur Analyse übertragen. Wir speichern keine Briefe auf unseren Servern.

4. Zahlungsabwicklung (Stripe)
Bei Käufen werden Sie zu Stripe weitergeleitet. Wir erhalten lediglich eine Bestätigung über die erfolgreiche Zahlung.

5. Ihre Rechte
Sie haben das Recht auf Auskunft, Löschung und Sperrung Ihrer Daten. Kontaktieren Sie uns unter amtsschimmel-killer@proton.me.""")
with t3:
    with st.expander("❓ FAQ", expanded=False):
        st.write("""Ist das ein Abonnement?
Nein. Wir hassen Abos genauso wie Amtsschimmel. Jede Zahlung ist eine Einmalzahlung für eine feste Anzahl an Scans. Es gibt keine automatische Verlängerung.

Wie sicher sind meine Dokumente?
Ihre Dokumente werden verschlüsselt an die KI (OpenAI) übertragen, dort nur kurzzeitig im Arbeitsspeicher verarbeitet und niemals dauerhaft auf unseren Servern gespeichert.

Ersetzt die App eine Rechtsberatung?
Nein. Wir bieten eine Formulierungshilfe und Unterstützung beim Textverständnis.

Was passiert, wenn der Scan fehlschlägt?
Ein Scan wird erst berechnet, wenn die KI den Text erfolgreich verarbeitet hat.""")
with t4:
    with st.expander("📝 Vorlagen", expanded=False):
        st.write("""Fristverlängerung:
Sehr geehrte Damen und Herren, in der Angelegenheit [Aktenzeichen] bitte ich um Verlängerung der gesetzten Frist bis zum [Datum]...

Widerspruch einlegen (Fristwahrend):
Sehr geehrte Damen und Herren, gegen Ihren Bescheid vom [Datum], erhalten am [Datum], lege ich hiermit Widerspruch ein...

Akteneinsicht einfordern:
Sehr geehrte Damen und Herren, ich beantrage hiermit gemäß § 25 SGB X bzw. § 29 VwVfG Akteneinsicht.""")

st.divider()

# ==========================================
# 4. HAUPTBEREICH (LAYOUT EXAKT WIE IM SCREENSHOT)
# ==========================================
c_pak, c_up, c_res = st.columns([0.9, 1.2, 1.5])

with c_pak:
    st.subheader("🌐 Sprachen")
    lang = st.selectbox("Wahl", ["🇩🇪 Deutsch", "🇺🇸 English", "🇹🇷 Türkçe", "🇵🇱 Polski", "🇷🇺 Русский", "🇸🇦 العربية", "🇪🇸 Español", "🇫🇷 Français", "🇮🇹 Italiano", "🇺🇦 Українська"], label_visibility="collapsed")
    if os.path.exists(LOGO_DATEI): st.image(LOGO_DATEI, width=110)
    st.write("---")
    
    for t, p, l in [("Analyse (1 Dokument)", "3,99 €", STRIPE_1), ("Spar-Paket (3 Dokumente)", "9,99 €", STRIPE_2), ("Sorglos-Paket (10 Dokumente)", "19,99 €", STRIPE_3)]:
        st.markdown(f'<div class="paket-card"><div class="paket-title">Amtsschimmel-Killer: {t}</div><div class="price-tag">Einmalpreis {p}</div><div class="no-abo-text">❌ KEIN ABO</div></div>', unsafe_allow_html=True)
        st.link_button("Jetzt kaufen", l)

with c_up:
    # EXAKTE POSITIONIERUNG (155px tief für mittiges Alignment)
    st.markdown("<div style='height: 155px;'></div>", unsafe_allow_html=True)
    st.subheader("📄 Upload & Vorschau")
    st.info(f"Guthaben: **{st.session_state.credits} Dokumente**")
    upped = st.file_uploader("Upload", type=["pdf", "jpg", "png", "jpeg"], label_visibility="collapsed")
    
    extracted_text = ""
    if upped:
        if upped.type == "application/pdf":
            try:
                raw = upped.read()
                with pdfplumber.open(io.BytesIO(raw)) as pdf:
                    for page in pdf.pages: extracted_text += (page.extract_text() or "") + "\n"
                st.image(convert_from_bytes(raw, first_page=1, last_page=1), caption="Vorschau", use_container_width=True)
            except: st.info("PDF wird verarbeitet...")
        else:
            img = Image.open(upped)
            st.image(img, caption="Vorschau", use_container_width=True)
            extracted_text = pytesseract.image_to_string(img)
        
        if st.button("🚀 JETZT ANALYSIEREN", type="primary", use_container_width=True):
            if st.session_state.credits > 0:
                with st.spinner("Amtsschimmel wird bekämpft..."):
                    try:
                        prompt = f"Analysiere auf {lang}. Gib mir strikt getrennt aus: [START_SUM] Zusammenfassung [END_SUM] [START_FRIST] Fristen [END_FRIST] [START_ANTWORT] Antwortschreiben [END_ANTWORT]. Text: {extracted_text}"
                        res = client.chat.completions.create(model="gpt-4o", messages=[{"role": "user", "content": prompt}])
                        full = res.choices.message.content
                        
                        st.session_state.full_res = {
                            "Zusammenfassung": full.split("[START_SUM]")[-1].split("[END_SUM]")[0].strip(),
                            "Fristen": full.split("[START_FRIST]")[-1].split("[END_FRIST]")[0].strip(),
                            "Antwort-Entwurf": full.split("[START_ANTWORT]")[-1].split("[END_ANTWORT]")[0].strip()
                        }
                        st.session_state.credits -= 1
                        st.balloons()
                        st.rerun()
                    except Exception as e: st.error(f"Fehler: {e}")
            else: st.error("Kein Guthaben!")

with c_res:
    st.subheader("🔍 Analyse & Antwort")
    if st.session_state.full_res:
        for title, text in st.session_state.full_res.items():
            st.markdown(f'<div class="result-box"><div class="box-title">{title}</div>{text}</div>', unsafe_allow_html=True)
        
        pdf_bytes = generate_pdf(st.session_state.full_res)
        st.download_button("📥 PDF Analyse herunterladen", data=pdf_bytes, file_name="Amtsschimmel_Analyse.pdf", mime="application/pdf")
        if st.button("🔄 Neuer Scan"):
            st.session_state.full_res = None
            st.rerun()
    else:
        st.info("Hier erscheint das Ergebnis nach dem Scan.")
