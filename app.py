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
# 1. SETUP & ZAHLUNGSSICHERHEIT (STRIPE FIX)
# ==========================================
st.set_page_config(page_title="Amtsschimmel-Killer", page_icon="📄", layout="wide")

if "credits" not in st.session_state:
    st.session_state.credits = 0
if "full_res" not in st.session_state:
    st.session_state.full_res = ""
if "processed_session" not in st.session_state:
    st.session_state.processed_session = ""

# ZAHLUNGSERKENNUNG: Prüft "pack" und "session_id" aus der URL
params = st.query_params
current_session = params.get("session_id", "")

if "pack" in params and current_session != st.session_state.processed_session:
    val = params["pack"]
    if val == "1": st.session_state.credits += 1
    elif val == "2": st.session_state.credits += 3
    elif val == "3": st.session_state.credits += 10
    st.session_state.processed_session = current_session
    st.toast("✅ Zahlung erfolgreich!", icon="💰")

if params.get("admin") == "GeheimAmt2024!":
    st.session_state.credits = 999

# ==========================================
# 2. STRIPE LINKS & DESIGN
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
        .no-abo-text { font-size: 11px; color: #d32f2f; font-weight: bold; text-transform: uppercase; }
        .paket-title { font-size: 12px; font-weight: bold; color: #333; margin-bottom: 2px; }
        .stLinkButton a {
            width: 100% !important; background-color: #0d47a1 !important;
            color: white !important; border-radius: 6px !important;
            font-weight: bold !important; padding: 8px !important;
            font-size: 13px !important; text-decoration: none;
            display: inline-block; text-align: center;
        }
        .analysis-box { background-color: #ffffff; padding: 20px; border-radius: 10px; border: 1px solid #ddd; white-space: pre-wrap; }
    </style>
    """, unsafe_allow_html=True)

LOGO_DATEI = "icon_final_blau.png"
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

def generate_pdf(content):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    safe_text = content.encode('latin-1', 'replace').decode('latin-1')
    pdf.multi_cell(0, 10, txt=safe_text)
    return pdf.output(dest='S').encode('latin-1')

# ==========================================
# 3. HEADER & INFOS (EINGEKLAPPT)
# ==========================================
st.title("Amtsschimmel-Killer 🪓")

t1, t2, t3, t4 = st.columns(4)
with t1:
    with st.expander("⚖️ Impressum", expanded=False):
        st.write("Amtsschimmel-Killer\nBetreiberin: Elisabeth Reinecke\nRingelsweide 9\n40223 Düsseldorf\n\nKontakt: +49 211 15821329\namtsschimmel-killer@proton.me\nWeb: amtsschimmel-killer.streamlit.app\n\nHaftung: Inhalte nach § 5 TMG. Keine Haftung für KI-Texte.")
with t2:
    with st.expander("🛡️ Datenschutz", expanded=False):
        st.write("1. Vertrauliche Behandlung (DSGVO).\n2. Hosting: Streamlit Cloud.\n3. Dokumentenverarbeitung: OpenAI (TLS-Verschlüsselt).\n4. Stripe: Nur Zahlungsbestätigung.\n5. Rechte: amtsschimmel-killer@proton.me.")
with t3:
    with st.expander("❓ FAQ", expanded=False):
        st.write("Ist das ein Abo? Nein.\nSicherheit? Keine Speicherung der Briefe.\nRechtsberatung? Nein.\nFehler? Scan wird erst nach Erfolg berechnet.")
with t4:
    with st.expander("📝 Vorlagen", expanded=False):
        st.write("Fristverlängerung:\nSehr geehrte Damen...\nWiderspruch:\nSehr geehrte Damen...\nAkteneinsicht:\nSehr geehrte Damen...")

st.divider()

# ==========================================
# 4. HAUPTBEREICH
# ==========================================
c_pak, c_up, c_res = st.columns([0.9, 1.4, 1.2])

with c_pak:
    st.subheader("🌐 Sprachen")
    lang = st.selectbox("Wahl", ["🇩🇪 Deutsch", "🇺🇸 English", "🇹🇷 Türkçe", "🇵🇱 Polski", "🇷🇺 Русский", "🇸🇦 العربية", "🇪🇸 Español", "🇫🇷 Français", "🇮🇹 Italiano", "🇷🇴 Română", "🇺🇦 Українська", "🇬🇷 Ελληνικά"], label_visibility="collapsed")
    
    if os.path.exists(LOGO_DATEI): st.image(LOGO_DATEI, width=110)
    
    st.write("---")
    st.markdown('<div class="paket-card"><div class="paket-title">Amtsschimmel-Killer: Analyse<br>(1 Dokument)</div><div class="price-tag">Einmalpreis 3,99 €</div><div class="no-abo-text">❌ KEIN ABO</div></div>', unsafe_allow_html=True)
    st.link_button("Jetzt kaufen", STRIPE_1)
    
    st.markdown('<div class="paket-card"><div class="paket-title">Amtsschimmel-Killer: Spar-Paket<br>(3 Dokumente)</div><div class="price-tag">Einmalpreis 9,99 €</div><div class="no-abo-text">❌ KEIN ABO</div></div>', unsafe_allow_html=True)
    st.link_button("Jetzt kaufen", STRIPE_2)
    
    st.markdown('<div class="paket-card"><div class="paket-title">Amtsschimmel-Killer: Sorglos-Paket<br>(10 Dokumente)</div><div class="price-tag">Einmalpreis 19,99 €</div><div class="no-abo-text">❌ KEIN ABO</div></div>', unsafe_allow_html=True)
    st.link_button("Jetzt kaufen", STRIPE_3)

with c_up:
    # EXAKTE POSITIONIERUNG (145px tief)
    st.markdown("<div style='height: 145px;'></div>", unsafe_allow_html=True)
    st.subheader("📄 Dokument hochladen")
    
    # Horizontale Reihe: Info links, Button rechts
    info_col, btn_col = st.columns([1, 1.5])
    with info_col:
        st.info(f"Guthaben: **{st.session_state.credits}**")
    
    upped = st.file_uploader("Upload", type=["pdf", "jpg", "png", "jpeg"], label_visibility="collapsed")
    
    extracted = ""
    if upped:
        if upped.type == "application/pdf":
            try:
                raw = upped.read()
                with pdfplumber.open(io.BytesIO(raw)) as pdf:
                    for page in pdf.pages: extracted += (page.extract_text() or "") + "\n"
                st.image(convert_from_bytes(raw, first_page=1, last_page=1), caption="Vorschau", use_container_width=True)
            except: st.info("PDF Vorschau lädt...")
        else:
            img = Image.open(upped)
            st.image(img, caption="Vorschau", use_container_width=True)
            extracted = pytesseract.image_to_string(img)
        
        # Button RECHTS neben der Info platziert
        with btn_col:
            if st.button("🚀 JETZT ANALYSIEREN", type="primary", use_container_width=True):
                if st.session_state.credits > 0:
                    with st.spinner("Amtsschimmel wird bekämpft..."):
                        try:
                            # FIX: OpenAI API Aufruf korrigiert
                            res = client.chat.completions.create(
                                model="gpt-4o",
                                messages=[{"role": "user", "content": f"Analysiere auf {lang} und erstelle Zusammenfassung & Antwort:\n\n{extracted}"}]
                            )
                            st.session_state.full_res = res.choices[0].message.content
                            st.session_state.credits -= 1
                            st.rerun()
                        except Exception as e: st.error(f"Fehler: {e}")
                else: st.error("Bitte erst Guthaben kaufen!")

with c_res:
    st.subheader("🔍 Analyse & Antwort")
    if st.session_state.full_res:
        st.markdown(f'<div class="analysis-box">{st.session_state.full_res}</div>', unsafe_allow_html=True)
        pdf_f = generate_pdf(st.session_state.full_res)
        st.download_button("📥 PDF herunterladen", data=pdf_f, file_name="Analyse.pdf", mime="application/pdf")
        if st.button("Neuer Scan"):
            st.session_state.full_res = ""
            st.rerun()
    else:
        st.info("Das Ergebnis erscheint hier nach der Analyse.")
